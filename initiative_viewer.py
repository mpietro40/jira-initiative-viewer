"""
Initiative Viewer - Flask Application
Displays hierarchical Jira structure: Business Initiative → Feature → Sub-Feature → Epic
With area-based organization and risk probability color coding.

Author: Initiative Viewer by Pietro Maffi
"""

from flask import Flask, render_template, request, jsonify, session, send_file
import logging
from typing import List, Dict, Optional, Set
from collections import defaultdict
import os
import pickle
import tempfile
import uuid
import argparse
import io
from datetime import datetime, timedelta
from jira_client import JiraClient
from initiative_viewer_pdf import InitiativeViewerPDFGenerator

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('InitiativeViewer')

# Define completed statuses (used for highlighting completed epics across all views)
COMPLETED_STATUSES = ['done', 'closed', 'completed', 'resolved', 'Prod deployed']

app = Flask(__name__)
# Use a consistent secret key (in production, use environment variable)
app.secret_key = 'initiative-viewer-secret-key-2026'  # Change this in production

# Create temp directory for data storage
DATA_DIR = os.path.join(tempfile.gettempdir(), 'initiative_viewer_data')
os.makedirs(DATA_DIR, exist_ok=True)

def save_analysis_data(data: Dict) -> str:
    """Save analysis data to file and return a unique key."""
    key = str(uuid.uuid4())
    filepath = os.path.join(DATA_DIR, f"{key}.pkl")
    with open(filepath, 'wb') as f:
        pickle.dump(data, f)
    logger.info(f"💾 Saved analysis data with key: {key}")
    return key

def load_analysis_data(key: str) -> Optional[Dict]:
    """Load analysis data from file using the key."""
    if not key:
        return None
    filepath = os.path.join(DATA_DIR, f"{key}.pkl")
    if not os.path.exists(filepath):
        logger.warning(f"⚠️ Data file not found for key: {key}")
        return None
    try:
        with open(filepath, 'rb') as f:
            data = pickle.load(f)
        logger.info(f"📂 Loaded analysis data with key: {key}")
        return data
    except Exception as e:
        logger.error(f"❌ Error loading data: {e}")
        return None

def cleanup_old_files():
    """Remove data files older than 1 hour."""
    try:
        now = datetime.now()
        for filename in os.listdir(DATA_DIR):
            if filename.endswith('.pkl'):
                filepath = os.path.join(DATA_DIR, filename)
                file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                if now - file_time > timedelta(hours=1):
                    os.remove(filepath)
                    logger.info(f"🗑️ Cleaned up old file: {filename}")
    except Exception as e:
        logger.error(f"❌ Cleanup error: {e}")

def get_most_recent_cache() -> Optional[tuple]:
    """Get the most recent cached data file.
    Returns: (key, data, timestamp) or None if no cache exists.
    """
    try:
        files = [f for f in os.listdir(DATA_DIR) if f.endswith('.pkl')]
        if not files:
            logger.warning("⚠️ No cached files found")
            return None
        
        # Find most recent file
        most_recent = max(files, key=lambda f: os.path.getmtime(os.path.join(DATA_DIR, f)))
        filepath = os.path.join(DATA_DIR, most_recent)
        key = most_recent.replace('.pkl', '')
        
        # Load data
        with open(filepath, 'rb') as f:
            data = pickle.load(f)
        
        file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
        logger.info(f"📦 Found cached data from {file_time.strftime('%Y-%m-%d %H:%M:%S')}")
        return (key, data, file_time)
    except Exception as e:
        logger.error(f"❌ Error loading cached data: {e}")
        return None

class JiraHierarchyFetcher:
    """
    Fetches Jira hierarchy: Business Initiative → Feature → Sub-Feature → Epic
    """
    
    def __init__(self, jira_client: JiraClient):
        """Initialize with Jira client."""
        self.jira_client = jira_client
    
    def fetch_hierarchy(self, query: str, fix_version: str) -> List[Dict]:
        """
        Fetch complete hierarchy starting from Business Initiatives.
        
        Args:
            query (str): JQL query to filter initiatives
            fix_version (str): Fix version to filter features/sub-features
            
        Returns:
            List[Dict]: Complete hierarchical data structure
        """
        logger.info(f"🔍 Fetching hierarchy for fixVersion: {fix_version}")
        
        # Step 1: Fetch Business Initiatives
        logger.info(f"⏳ Step 1/4: Fetching Business Initiatives...")
        initiatives = self._fetch_initiatives(query)
        logger.info(f"📊 Found {len(initiatives)} initiatives")
        
        # Step 2: For each initiative, fetch features with fixVersion
        logger.info(f"⏳ Step 2/4: Fetching Features for {len(initiatives)} initiatives...")
        for i, initiative in enumerate(initiatives, 1):
            logger.info(f"  📍 Processing initiative {i}/{len(initiatives)}: {initiative['key']}")
            initiative['features'] = self._fetch_features(initiative['key'], fix_version)
            logger.info(f"    ✓ Found {len(initiative['features'])} features")
            
            # Step 3: For each feature, fetch sub-features
            logger.info(f"  ⏳ Step 3/4: Fetching Sub-Features for {len(initiative['features'])} features...")
            for feature in initiative['features']:
                feature['sub_features'] = self._fetch_sub_features(feature['key'], fix_version)
                logger.info(f"    ✓ Feature {feature['key']}: {len(feature['sub_features'])} sub-features")
                
                # Step 4: For each sub-feature, fetch epics by area
                logger.info(f"    ⏳ Step 4/4: Fetching Epics for {len(feature['sub_features'])} sub-features...")
                for sub_feature in feature['sub_features']:
                    sub_feature['epics_by_area'] = self._fetch_epics_by_area(sub_feature['key'])
                    total_epics = sum(len(epics) for epics in sub_feature['epics_by_area'].values())
                    logger.info(f"      ✓ Sub-Feature {sub_feature['key']}: {total_epics} epics")
        
        return initiatives
    
    def _fetch_initiatives(self, query: str) -> List[Dict]:
        """Fetch Business Initiatives based on query."""
        # Use the query as-is (user should include issuetype filter)
        jql = query
        
        try:
            issues = self.jira_client.fetch_issues(jql, max_results=100)
            
            initiatives = []
            for issue in issues:
                initiative_data = self._fetch_issue_details(issue['key'])
                if initiative_data:
                    initiatives.append(initiative_data)
            
            return initiatives
        except Exception as e:
            logger.error(f"Failed to fetch initiatives: {str(e)}")
            return []
    
    def _fetch_features(self, initiative_key: str, fix_version: str) -> List[Dict]:
        """Fetch Features under an initiative with specific fixVersion."""
        jql = (f'issuekey in childIssuesOf("{initiative_key}") '
               f'AND issuetype = Feature '
               f'AND fixVersion = "{fix_version}"')
        
        try:
            logger.info(f"🔍 Features JQL: {jql}")
            issues = self.jira_client.fetch_issues(jql, max_results=200)
            
            # Log if no results found, but DON'T fall back to unfiltered query
            if not issues:
                logger.info(f"ℹ️ No features found with fixVersion '{fix_version}' for {initiative_key}")
            
            features = []
            for issue in issues:
                feature_data = self._fetch_issue_details(issue['key'])
                if feature_data:
                    features.append(feature_data)
            
            return features
        except Exception as e:
            logger.error(f"Failed to fetch features for {initiative_key}: {str(e)}")
            return []
    
    def _fetch_sub_features(self, feature_key: str, fix_version: str) -> List[Dict]:
        """Fetch Sub-Features under a feature with specific fixVersion."""
        jql = (f'issuekey in childIssuesOf("{feature_key}") '
               f'AND issuetype = "Sub-Feature" '
               f'AND fixVersion = "{fix_version}"')
        
        try:
            logger.debug(f"🔍 Sub-Features JQL: {jql}")
            issues = self.jira_client.fetch_issues(jql, max_results=200)
            
            # Log if no results found, but DON'T fall back to unfiltered query
            if not issues:
                logger.debug(f"ℹ️ No sub-features found with fixVersion '{fix_version}' for {feature_key}")
            
            sub_features = []
            for issue in issues:
                sub_feature_data = self._fetch_issue_details(issue['key'])
                if sub_feature_data:
                    sub_features.append(sub_feature_data)
            
            return sub_features
        except Exception as e:
            logger.error(f"Failed to fetch sub-features for {feature_key}: {str(e)}")
            return []
    
    def _fetch_epics_by_area(self, sub_feature_key: str) -> Dict[str, List[Dict]]:
        """
        Fetch Epics linked to a sub-feature, organized by area (project).
        
        Returns:
            Dict[str, List[Dict]]: Epics grouped by area/project
        """
        jql = f'issuekey in childIssuesOf("{sub_feature_key}") AND issuetype = Epic'
        
        try:
            issues = self.jira_client.fetch_issues(jql, max_results=500)
            
            epics_by_area = defaultdict(list)
            
            for issue in issues:
                epic_data = self._fetch_issue_details(issue['key'])
                if epic_data:
                    area = epic_data.get('project_key', 'Unknown')
                    epics_by_area[area].append(epic_data)
            
            return dict(epics_by_area)
        except Exception as e:
            logger.error(f"Failed to fetch epics for {sub_feature_key}: {str(e)}")
            return {}
    
    def _fetch_issue_details(self, issue_key: str) -> Optional[Dict]:
        """
        Fetch detailed information for a single issue.
        
        Returns:
            Optional[Dict]: Issue details including risk probability
        """
        try:
            # Fetch ALL fields to find the Risk Status field automatically
            response = self.jira_client.session.get(
                f"{self.jira_client.base_url}/rest/api/2/issue/{issue_key}",
                params={'expand': 'names'}
            )
            
            if response.status_code != 200:
                logger.warning(f"Failed to fetch details for {issue_key}")
                return None
            
            data = response.json()
            fields = data.get('fields', {})
            field_names = data.get('names', {})
            
            # Search for Risk-related fields by name
            risk_field_id = None
            risk_field_name = None
            
            for field_id, field_name in field_names.items():
                field_name_lower = field_name.lower()
                if 'risk' in field_name_lower and ('status' in field_name_lower or 'probability' in field_name_lower):
                    risk_field_id = field_id
                    risk_field_name = field_name
                    logger.info(f"🎯 Found risk field for {issue_key}: {field_name} ({field_id})")
                    break
            
            assignee = fields.get('assignee')
            assignee_name = assignee.get('displayName', 'Unassigned') if assignee else 'Unassigned'
            
            status = fields.get('status', {})
            status_name = status.get('name', 'Unknown')
            
            project = fields.get('project', {})
            project_key = project.get('key', 'Unknown')
            
            # Get risk value from the discovered field
            risk_probability = None
            if risk_field_id:
                risk_probability = fields.get(risk_field_id)
                logger.info(f"📊 Risk value for {issue_key} from '{risk_field_name}': {risk_probability}")
            else:
                logger.info(f"⚠️ No risk field found for {issue_key}")
            
            # Handle different risk field data types
            risk_value = None
            risk_str = None  # Initialize to avoid undefined variable error
            
            if risk_probability:
                if isinstance(risk_probability, dict):
                    risk_value = risk_probability.get('value')
                elif isinstance(risk_probability, list):
                    # If it's a list, take the first value
                    if risk_probability and isinstance(risk_probability[0], dict):
                        risk_value = risk_probability[0].get('value')
                    elif risk_probability:
                        risk_value = risk_probability[0]
                else:
                    risk_value = risk_probability
            
            # Normalize risk value to numeric 1-5 scale
            normalized_risk = None
            if risk_value:
                risk_str = str(risk_value).lower()
                
                # Skip if it looks like a user ID (e.g., A695494(a695494))
                if '(' in str(risk_value) and ')' in str(risk_value):
                    logger.info(f"⚠️ Skipping user ID field for {issue_key}: '{risk_value}'")
                    risk_value = None
                    risk_str = None
                else:
                    logger.info(f"Processing risk value for {issue_key}: '{risk_value}' -> '{risk_str}'")
            else:
                logger.info(f"ℹ️ No risk value for {issue_key} - will display without color")
                
            # Only process if we have a valid risk_str (not a user ID)
            if risk_str:                # Handle text-based risk status with full descriptions
                # Examples: "Green: no risk / committed", "Red: high risk / can't deliver"
                if 'green' in risk_str or 'no risk' in risk_str or 'committed' in risk_str:
                    normalized_risk = 1  # Green → Low risk
                    logger.info(f"  → Mapped to level 1 (Green)")
                elif 'yellow' in risk_str or 'medium' in risk_str:
                    normalized_risk = 3  # Yellow → Medium risk
                    logger.info(f"  → Mapped to level 3 (Yellow/Orange)")
                elif 'red' in risk_str or 'high risk' in risk_str or "can't deliver" in risk_str or 'cannot deliver' in risk_str:
                    normalized_risk = 5  # Red → High risk
                    logger.info(f"  → Mapped to level 5 (Red)")
                elif 'none' in risk_str or 'undefined' in risk_str:
                    normalized_risk = None
                    logger.info(f"  → No risk defined")
                else:
                    # Try numeric format (1-5)
                    try:
                        numeric_value = int(str(risk_value))
                        if 1 <= numeric_value <= 5:
                            normalized_risk = numeric_value
                            logger.info(f"  → Numeric value: {numeric_value}")
                    except (ValueError, TypeError):
                        logger.warning(f"  → Could not parse risk value: {risk_value}")
                        normalized_risk = None
            
            risk_probability = normalized_risk
            
            return {
                'key': issue_key,
                'summary': fields.get('summary', 'No summary'),
                'assignee': assignee_name,
                'status': status_name,
                'project_key': project_key,
                'risk_probability': risk_probability
            }
        except Exception as e:
            logger.error(f"Failed to fetch details for {issue_key}: {str(e)}")
            # Return basic info even if there's an error, so epic is still displayed
            return {
                'key': issue_key,
                'summary': 'Error fetching details',
                'assignee': 'Unknown',
                'status': 'Unknown',
                'project_key': 'Unknown',
                'risk_probability': None
            }
            return None


@app.route('/')
def index():
    """Display input form."""
    return render_template('initiative_form.html')


@app.route('/analyze', methods=['POST'])
def analyze():
    """Process form and display hierarchy."""
    jira_url = request.form.get('jira_url')
    access_token = request.form.get('access_token')
    query = request.form.get('query')
    fix_version = request.form.get('fix_version')
    use_cache_form = request.form.get('use_cache') == 'true'  # Checkbox from form
    
    # Get initiative limit - None means no limit, otherwise use the specified number
    enable_limit = request.form.get('enable_limit') == 'true'
    if enable_limit:
        try:
            limit_count = int(request.form.get('limit_count', 25))
            if limit_count <= 0:
                limit_count = None  # Invalid number, disable limit
        except (ValueError, TypeError):
            limit_count = 25  # Default to 25 if invalid input
    else:
        limit_count = None  # No limit
    
    # Check if cache should be used (form checkbox OR command-line flag)
    use_cache = use_cache_form or app.config.get('USE_CACHE', False)
    
    if use_cache:
        logger.info("🔄 CACHE MODE: Checking for cached data...")
        cache_result = get_most_recent_cache()
        
        if cache_result:
            key, data, file_time = cache_result
            cached_query = data.get('query', '')
            
            # Compare queries - only use cache if query matches
            if cached_query.strip() == query.strip():
                initiatives = data.get('initiatives', [])
                cached_fix_version = data.get('fix_version', 'Unknown')
                all_areas = data.get('all_areas', [])
                
                session['data_key'] = key
                
                age_minutes = int((datetime.now() - file_time).total_seconds() / 60)
                logger.info(f"✅ Cache HIT: Query matches! Loaded {len(initiatives)} initiatives (age: {age_minutes} minutes)")
                
                return render_template(
                    'initiative_hierarchy.html',
                    initiatives=initiatives,
                    fix_version=cached_fix_version,
                    all_areas=all_areas,
                    cached_mode=True,
                    cache_age=f"{age_minutes} minutes ago",
                    query=cached_query,
                    completed_statuses=COMPLETED_STATUSES
                )
            else:
                logger.warning(f"⚠️ Cache MISS: Query changed!")
                logger.warning(f"   Cached query: {cached_query[:50]}...")
                logger.warning(f"   Current query: {query[:50]}...")
                logger.info("   → Fetching fresh data from Jira")
                # Fall through to normal processing
        else:
            logger.warning("⚠️ No cached data found, proceeding with normal fetch...")
            # Fall through to normal processing
    
    # Log the received URL for debugging
    logger.info(f"📥 Received Jira URL: {jira_url}")
    
    # Validate inputs
    if not all([jira_url, access_token, query, fix_version]):
        return render_template('initiative_form.html', error="All fields are required")
    
    # Validate URL format
    if not jira_url.startswith('http'):
        return render_template('initiative_form.html', error="Jira URL must start with http:// or https://")
    
    # Validate and clean JQL query
    logger.info(f"🔍 Received JQL Query: {query}")
    
    if ' and order by' in query.lower():
        return render_template('initiative_form.html',
            error="Invalid JQL: Remove 'AND' before 'ORDER BY'. Example: ... ORDER BY Rank")
    
    try:
        # Initialize Jira client
        logger.info(f"🔗 Initializing Jira client with URL: {jira_url}")
        jira_client = JiraClient(base_url=jira_url, access_token=access_token)
        
        # Fetch hierarchy
        fetcher = JiraHierarchyFetcher(jira_client)
        initiatives = fetcher.fetch_hierarchy(query, fix_version)
        
        # Apply initiative limit if enabled and there are more initiatives than the limit
        is_limited = False
        original_count = len(initiatives)
        if limit_count and original_count > limit_count:
            initiatives = initiatives[:limit_count]
            is_limited = True
            logger.info(f"⚠️ Limited initiatives from {original_count} to {limit_count} (limit enabled)")
        
        # Get all unique areas for table headers
        all_areas = set()
        for initiative in initiatives:
            for feature in initiative.get('features', []):
                for sub_feature in feature.get('sub_features', []):
                    all_areas.update(sub_feature.get('epics_by_area', {}).keys())
        
        # Store data in file-based storage (not session - too large for cookies)
        data_key = save_analysis_data({
            'initiatives': initiatives,
            'fix_version': fix_version,
            'all_areas': sorted(all_areas),
            'query': query,
            'jira_url': jira_url,
            'is_limited': is_limited,
            'limit_count': limit_count,
            'original_count': original_count
        })
        session['data_key'] = data_key
        
        # Cleanup old files
        cleanup_old_files()
        
        return render_template(
            'initiative_hierarchy.html',
            initiatives=initiatives,
            fix_version=fix_version,
            all_areas=sorted(all_areas),
            query=query,
            is_limited=is_limited,
            limit_count=limit_count if is_limited else None,
            original_count=original_count if is_limited else None,
            completed_statuses=COMPLETED_STATUSES
        )
    
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        return render_template('initiative_form.html', error=f"Analysis failed: {str(e)}")


@app.route('/export_pdf', methods=['GET'])
def export_pdf():
    """Export the current analysis results as a PDF report."""
    try:
        # Retrieve data from file storage using session key
        data_key = session.get('data_key')
        if not data_key:
            logger.error("❌ No data_key in session")
            return "No data available for export. Please run an analysis first.", 400
        
        data = load_analysis_data(data_key)
        if not data:
            logger.error(f"❌ Could not load data for key: {data_key}")
            return "Data expired or not found. Please run the analysis again.", 400
        
        initiatives = data.get('initiatives')
        fix_version = data.get('fix_version')
        all_areas = data.get('all_areas', [])
        query = data.get('query', '')
        jira_url = data.get('jira_url', '')
        is_limited = data.get('is_limited', False)
        limit_count = data.get('limit_count')
        original_count = data.get('original_count')
        
        if not initiatives or not fix_version:
            logger.error("❌ Invalid data structure")
            return "Invalid data. Please run an analysis first.", 400
        
        logger.info(f"✅ Exporting PDF for {len(initiatives)} initiatives")
        
        # Generate PDF
        pdf_generator = InitiativeViewerPDFGenerator(
            initiatives, fix_version, all_areas, query, 
            jira_url=jira_url, is_limited=is_limited, 
            limit_count=limit_count, original_count=original_count,
            completed_statuses=COMPLETED_STATUSES
        )
        pdf_buffer = pdf_generator.generate()
        
        # Generate filename with timestamp
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"Initiative_Report_{fix_version}_{timestamp}.pdf"
        
        # Send PDF file
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        logger.error(f"PDF export failed: {str(e)}")
        return f"PDF export failed: {str(e)}", 500


@app.route('/export_pdf_wide', methods=['GET'])
def export_pdf_wide():
    """Export the current analysis results as a wide PDF report (A3/Wide format)."""
    try:
        # Retrieve data from file storage using session key
        data_key = session.get('data_key')
        if not data_key:
            logger.error("❌ No data_key in session")
            return "No data available for export. Please run an analysis first.", 400
        
        data = load_analysis_data(data_key)
        if not data:
            logger.error(f"❌ Could not load data for key: {data_key}")
            return "Data expired or not found. Please run the analysis again.", 400
        
        initiatives = data.get('initiatives')
        fix_version = data.get('fix_version')
        all_areas = data.get('all_areas', [])
        query = data.get('query', '')
        jira_url = data.get('jira_url', '')
        is_limited = data.get('is_limited', False)
        limit_count = data.get('limit_count')
        original_count = data.get('original_count')
        
        if not initiatives or not fix_version:
            logger.error("❌ Invalid data structure")
            return "Invalid data. Please run an analysis first.", 400
        
        # Determine format based on number of areas
        num_areas = len(all_areas)
        if num_areas <= 8:
            page_format = 'A3'
            format_name = 'A3'
        else:
            page_format = 'wide'
            format_name = 'Wide'
        
        logger.info(f"✅ Exporting {format_name} PDF for {len(initiatives)} initiatives with {num_areas} areas")
        
        # Generate wide PDF
        pdf_generator = InitiativeViewerPDFGenerator(
            initiatives, fix_version, all_areas, query, 
            page_format=page_format, jira_url=jira_url,
            is_limited=is_limited, limit_count=limit_count, 
            original_count=original_count,
            completed_statuses=COMPLETED_STATUSES
        )
        pdf_buffer = pdf_generator.generate()
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"Initiative_Report_{fix_version}_{format_name}_{timestamp}.pdf"
        
        # Send PDF file
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        logger.error(f"Wide PDF export failed: {str(e)}")
        return f"Wide PDF export failed: {str(e)}", 500


@app.route('/export_html', methods=['GET'])
def export_html():
    """Export the current analysis results as an HTML report."""
    try:
        # Retrieve data from file storage using session key
        data_key = session.get('data_key')
        if not data_key:
            logger.error("❌ No data_key in session")
            return "No data available for export. Please run an analysis first.", 400
        
        data = load_analysis_data(data_key)
        if not data:
            logger.error(f"❌ Could not load data for key: {data_key}")
            return "Data expired or not found. Please run the analysis again.", 400
        
        initiatives = data.get('initiatives', [])
        fix_version = data.get('fix_version', 'Unknown')
        all_areas = data.get('all_areas', [])
        query = data.get('query', '')
        is_limited = data.get('is_limited', False)
        limit_count = data.get('limit_count')
        original_count = data.get('original_count')
        
        if not initiatives:
            logger.error("❌ No initiatives found")
            return "No data available. Please run an analysis first.", 400
        
        # Count initiatives with features
        initiatives_with_features = sum(1 for init in initiatives if init.get('features'))
        
        logger.info(f"✅ Exporting HTML for {len(initiatives)} initiatives")
        
        # Generate Confluence-compatible HTML (body content only, no html/head/body tags)
        html_content = render_template(
            'export_confluence.html',
            initiatives=initiatives,
            fix_version=fix_version,
            all_areas=all_areas,
            query=query,
            initiatives_with_features=initiatives_with_features,
            generated_date=datetime.now().strftime('%B %d, %Y at %H:%M'),
            year=datetime.now().year,
            is_limited=is_limited,
            limit_count=limit_count,
            original_count=original_count,
            completed_statuses=COMPLETED_STATUSES
        )
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"Initiative_Report_Confluence_{fix_version}_{timestamp}.html"
        
        # Send HTML file
        return send_file(
            io.BytesIO(html_content.encode('utf-8')),
            mimetype='text/html',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        logger.error(f"HTML export failed: {str(e)}")
        return f"HTML export failed: {str(e)}", 500


if __name__ == '__main__':
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Initiative Viewer - Jira Hierarchy Analyzer')
    parser.add_argument('--cached', '--use-cache', action='store_true',
                       help='Use cached data from previous analysis instead of fetching from Jira')
    parser.add_argument('--port', type=int, default=5001,
                       help='Port to run the Flask application (default: 5001)')
    args = parser.parse_args()
    
    # Configure app based on arguments
    app.config['USE_CACHE'] = args.cached
    
    if args.cached:
        logger.info("🔄 ========================================")
        logger.info("🔄 CACHE MODE ENABLED")
        logger.info("🔄 Will load most recent cached data")
        logger.info("🔄 ========================================")
    
    app.run(debug=True, host='0.0.0.0', port=args.port)
