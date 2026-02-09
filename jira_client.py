"""
Jira API Client
Handles connection and data retrieval from Jira servers.
"""

import requests
import requests.adapters
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import json
import time

# Import urllib3 with fallback
try:
    from urllib3.util.retry import Retry
except ImportError:
    try:
        from requests.packages.urllib3.util.retry import Retry
    except ImportError:
        Retry = None

# Configure logger with proper name
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s')
logger = logging.getLogger('JiraClient')

# Set logger level to DEBUG for detailed tracing    

max_results = 5000  # Default maximum results for issue fetching
class JiraClient:
    """
    Client for connecting to Jira API and retrieving issue data.
    
    This class handles authentication, API requests, and data parsing
    for Jira issue analysis and Epic tracking.
    """
    
    def __init__(self, base_url: str, access_token: str):
        """
        Initialize Jira client with connection details.
        
        Args:
            base_url (str): Jira server URL (e.g., https://company.atlassian.net)
            access_token (str): API access token for authentication
        """
        self.base_url = base_url.rstrip('/')
        logger.info(f"🔧 JiraClient initialized with base_url: {self.base_url}")
        self.access_token = access_token
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'JiraObeyaEpicAnalyzer/1.0'
        })
        
        # Connection settings for production
        self.timeout = (15, 60)  # (connect, read) timeouts - increased for large queries
        self.max_retries = 3
        self.retry_delay = 2  # seconds
        self.batch_size = 200  # Default batch size
        self.min_batch_size = 50  # Minimum batch size when reducing due to timeouts
        
        # Configure session for better performance
        if Retry:
            self.session.mount('https://', requests.adapters.HTTPAdapter(
                max_retries=Retry(
                    total=0,  # We handle retries manually
                    backoff_factor=0.3,
                    status_forcelist=[500, 502, 503, 504]
                )
            ))
    
    def configure_timeouts(self, connect_timeout: int = 15, read_timeout: int = 60, 
                          batch_size: int = 200, min_batch_size: int = 50):
        """
        Configure timeout and batch size settings.
        
        Args:
            connect_timeout (int): Connection timeout in seconds
            read_timeout (int): Read timeout in seconds
            batch_size (int): Default batch size for queries
            min_batch_size (int): Minimum batch size when reducing due to timeouts
        """
        self.timeout = (connect_timeout, read_timeout)
        self.batch_size = batch_size
        self.min_batch_size = min_batch_size
        logger.info(f"🔧 Updated timeouts: connect={connect_timeout}s, read={read_timeout}s, batch={batch_size}")
    
    def test_connection(self) -> bool:
        """
        Test connection to Jira server with timeout and retry.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        for attempt in range(self.max_retries):
            try:
                response = self.session.get(
                    f'{self.base_url}/rest/api/2/myself',
                    timeout=self.timeout
                )
                if response.status_code == 200:
                    return True
                elif response.status_code == 401:
                    logger.error("🚩 Authentication failed - invalid token")
                    return False
                elif response.status_code == 403:
                    logger.error("🚩 Access forbidden - insufficient permissions")
                    return False
                    
            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
                logger.warning(f"⏰ Connection issue (attempt {attempt + 1}/{self.max_retries}): {str(e)}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (attempt + 1))
            except Exception as e:
                logger.error(f"🚩 Connection test failed: {str(e)}")
                return False
                
        return False
    
    def get_epic_children(self, epic_key: str) -> List[Dict]:
        """
        Fetch all issues linked to an epic.
        
        Args:
            epic_key (str): The key of the epic
            
        Returns:
            List[Dict]: List of child issues
        """
        logger.info(f"🔍 Fetching child issues for epic: {epic_key}")
        
        try:
            # Get issues in the epic
            jql = f"'Epic Link' = {epic_key}"
            params = {
                'jql': jql,
                'maxResults': 500,  # Adjust if needed
                'fields': 'key,summary,status,timeoriginalestimate,timeestimate'
            }
            
            response = self.session.get(
                f'{self.base_url}/rest/api/2/search',
                params=params
            )
            response.raise_for_status()
            
            return response.json().get('issues', [])
            
        except Exception as e:
            logger.error(f"Error fetching epic children for {epic_key}: {str(e)}")
            return []
        
    ## Fetch issues based on JQL query
    ## This method retrieves issues from Jira using a JQL query.
    ## It handles pagination and processes each issue to extract relevant data.
    ## max rows is set to 5000 by default, but can be adjusted.
    ## fetching is done in chunks of 200 to avoid hitting API limits.
    def fetch_issues(self, jql_query: str, max_results, start_at: int = 0) -> List[Dict]:
        """
        Fetch issues from Jira using JQL query with adaptive timeout handling.
        
        Args:
            jql_query (str): JQL query string
            max_results (int): Maximum number of results to fetch
            
        Returns:
            List[Dict]: List of issue dictionaries with relevant data
        """
        issues = []
        current_start = start_at
        current_batch_size = self.batch_size
        consecutive_timeouts = 0
        
        logger.info(f"🔍 Fetching issues with JQL: {jql_query}")
        
        while True:
            # Retry logic for each batch with adaptive strategies
            batch_success = False
            timeout_occurred = False
            
            for attempt in range(self.max_retries):
                try:
                    # Prepare request parameters with current batch size
                    params = {
                        'jql': jql_query,
                        'startAt': current_start,
                        'maxResults': min(current_batch_size, max_results - len(issues)),
                        'expand': 'changelog',
                        'fields': 'key,summary,status,created,resolutiondate,assignee,reporter,priority,issuetype,timeoriginalestimate,timeestimate,fixVersions,project,customfield_10037,customfield_10095,customfield_10096,customfield_10097,comment'
                    }
                    
                    logger.info(f"🔄 Fetching batch starting at {current_start} (size: {params['maxResults']}, attempt {attempt + 1}/{self.max_retries})")
                    
                    # Use longer timeout for retries
                    current_timeout = (self.timeout[0], self.timeout[1] * (attempt + 1))
                    
                    response = self.session.get(
                        f'{self.base_url}/rest/api/2/search',
                        params=params,
                        timeout=current_timeout
                    )
                    response.raise_for_status()
                    batch_success = True
                    consecutive_timeouts = 0  # Reset timeout counter on success
                    break
                    
                except requests.exceptions.Timeout as e:
                    timeout_occurred = True
                    logger.warning(f"⏰ Timeout on attempt {attempt + 1}/{self.max_retries} for batch at {current_start} (timeout: {current_timeout[1]}s): {str(e)}")
                    if attempt < self.max_retries - 1:
                        # Exponential backoff with jitter
                        delay = self.retry_delay * (2 ** attempt) + (attempt * 0.5)
                        logger.info(f"⏳ Waiting {delay:.1f}s before retry...")
                        time.sleep(delay)
                except requests.exceptions.RequestException as e:
                    logger.warning(f"⚠️ Request failed on attempt {attempt + 1}/{self.max_retries} for batch at {current_start}: {str(e)}")
                    if attempt < self.max_retries - 1:
                        time.sleep(self.retry_delay * (attempt + 1))
            
            # Handle batch failure with adaptive strategies
            if not batch_success:
                if timeout_occurred:
                    consecutive_timeouts += 1
                    
                    # Try reducing batch size if we have consecutive timeouts
                    if consecutive_timeouts >= 2 and current_batch_size > self.min_batch_size:
                        old_size = current_batch_size
                        current_batch_size = max(self.min_batch_size, current_batch_size // 2)
                        logger.info(f"🔧 Reducing batch size from {old_size} to {current_batch_size} due to timeouts")
                        consecutive_timeouts = 0  # Reset counter after adjustment
                        continue  # Try again with smaller batch
                    
                    # If still failing with minimum batch size, try skipping this batch
                    if current_batch_size == self.min_batch_size:
                        logger.warning(f"⏭️ Skipping batch at {current_start} due to persistent timeouts")
                        current_start += self.min_batch_size
                        continue
                
                logger.error(f"🚩 Failed to fetch batch after {self.max_retries} attempts, stopping at {current_start}")
                break
            
            if batch_success:
                data = response.json()
                batch_issues = data.get('issues', [])
                
                if not batch_issues:
                    break
                
                # Process each issue to extract relevant data
                for issue in batch_issues:
                    processed_issue = self._process_issue(issue)
                    if processed_issue:
                        issues.append(processed_issue)
                
                current_start += len(batch_issues)
                
                # Gradually increase batch size back to normal if we had reduced it
                if current_batch_size < self.batch_size and consecutive_timeouts == 0:
                    current_batch_size = min(self.batch_size, current_batch_size + 25)
                    if current_batch_size < self.batch_size:
                        logger.info(f"📈 Increasing batch size to {current_batch_size}")
                
                # Log progress
                total_available = data.get('total', 0)
                logger.info(f"📊 Progress: {len(issues)}/{min(max_results, total_available)} issues fetched (batch: {len(batch_issues)} issues)")
                
                # Check if we've fetched all available issues
                if current_start >= data.get('total', 0) or len(issues) >= max_results:
                    break
        
        # Final summary
        if issues:
            logger.info(f"✅ Successfully fetched {len(issues)} issues from Jira")
        else:
            logger.warning(f"⚠️ No issues fetched - check JQL query and permissions")
        
        return issues
    
    def handle_timeout_recovery(self, jql_query: str, failed_start: int, max_results: int) -> List[Dict]:
        """
        Attempt to recover from timeout by using simpler queries.
        
        Args:
            jql_query (str): Original JQL query
            failed_start (int): Position where timeout occurred
            max_results (int): Maximum results to fetch
            
        Returns:
            List[Dict]: Recovered issues if any
        """
        logger.info(f"🔧 Attempting timeout recovery from position {failed_start}")
        
        # Try with minimal fields first
        simple_params = {
            'jql': jql_query,
            'startAt': failed_start,
            'maxResults': self.min_batch_size,
            'fields': 'key,summary,status'  # Minimal fields
        }
        
        try:
            response = self.session.get(
                f'{self.base_url}/rest/api/2/search',
                params=simple_params,
                timeout=(self.timeout[0], 30)  # Shorter timeout
            )
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"✅ Recovery successful - fetched {len(data.get('issues', []))} issues with minimal fields")
            return data.get('issues', [])
            
        except Exception as e:
            logger.error(f"🚩 Recovery attempt failed: {str(e)}")
            return []
    
    def _process_issue(self, issue: Dict) -> Optional[Dict]:
        """
        Process raw issue data and extract relevant information.
        
        Args:
            issue (Dict): Raw issue data from Jira API
            
        Returns:
            Optional[Dict]: Processed issue data or None if processing fails
        """
        try:
            # Extract basic issue information
            key = issue['key']
            fields = issue['fields']
            
            # Extract reporter
            reporter = fields.get('reporter', {}).get('displayName', '') if fields.get('reporter') else ''
            
            # Extract comments
            comments = []
            comment_data = fields.get('comment', {})
            if comment_data and 'comments' in comment_data:
                for comment in comment_data['comments']:
                    comments.append({
                        'author': comment.get('author', {}).get('displayName', ''),
                        'body': comment.get('body', ''),
                        'created': comment.get('created', '')
                    })
            
            processed = {
                'key': key,
                'summary': fields.get('summary', ''),
                'status': fields.get('status', {}).get('name', ''),
                'issue_type': fields.get('issuetype', {}).get('name', ''),
                'priority': fields.get('priority', {}).get('name', ''),
                'created': fields.get('created'),
                'resolution_date': fields.get('resolutiondate'),
                'assignee': fields.get('assignee', {}).get('displayName', '') if fields.get('assignee') else '',
                'reporter': reporter,
                'comments': comments,
                'fields': fields,  # Include raw fields for estimate access
                'status_history': []
            }
            
            # Process changelog for status transitions
            changelog = issue.get('changelog', {})
            if changelog and 'histories' in changelog:
                for history in changelog['histories']:
                    created = history.get('created')
                    for item in history.get('items', []):
                        if item.get('field') == 'status':
                            processed['status_history'].append({
                                'from_status': item.get('fromString', ''),
                                'to_status': item.get('toString', ''),
                                'changed': created
                            })
            
            return processed
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to process issue {issue.get('key', 'unknown')}: {str(e)}")
            return None
        
    def update_issue_estimates(self, issue_key: str, original_estimate: str, remaining_estimate: str = None) -> bool:
        """
        Update issue time estimates using Jira API.
        
        Args:
            issue_key (str): The issue key to update
            original_estimate (str): Original estimate in Jira format (e.g., "4h", "2d", "30m")
            remaining_estimate (str, optional): Remaining estimate, defaults to original_estimate
            
        Returns:
            bool: True if update successful, False otherwise
        """
        if remaining_estimate is None:
            remaining_estimate = original_estimate
            
        try:
            # Use the fields format for updating time tracking
            payload = {
                "fields": {
                    "timetracking": {
                        "originalEstimate": original_estimate,
                        "remainingEstimate": remaining_estimate
                    }
                }
            }
            
            response = self.session.put(
                f'{self.base_url}/rest/api/2/issue/{issue_key}',
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 204:
                logger.info(f"✅ Updated estimates for {issue_key}: {original_estimate}")
                return True
            else:
                logger.error(f"🚩 Failed to update {issue_key}: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"🚩 Error updating estimates for {issue_key}: {str(e)}")
            return False
    
    # Parse CSV file for issue keys
    def parse_csv_for_issue_keys(self, csv_file) -> List[str]:
        """
        Parse CSV file to extract Jira issue keys.
    
        Args:
            csv_file: Uploaded CSV file object
        
        Returns:
            List[str]: List of valid Jira issue keys
        """
        import csv
        import re
    
        issue_keys = []
        jira_key_pattern = re.compile(r'^[A-Z][A-Z0-9]*-\d+$')
    
        try:
            # Read CSV content
            csv_content = csv_file.read().decode('utf-8')
            csv_reader = csv.DictReader(csv_content.splitlines())
        
            # Look for columns that might contain issue keys
            key_columns = []
            if csv_reader.fieldnames:
                for field in csv_reader.fieldnames:
                    if any(keyword in field.lower() for keyword in ['key', 'issue', 'ticket', 'id']):
                        key_columns.append(field)
        
            if not key_columns:
                logger.warning(f"⚠️ No key columns found, using first column")
                key_columns = [csv_reader.fieldnames[0]] if csv_reader.fieldnames else []
        
            logger.info(f"📋 Using columns for issue keys: {key_columns}")
        
            # Extract issue keys
            for row in csv_reader:
                for column in key_columns:
                    value = row.get(column, '').strip().upper()
                    if value and jira_key_pattern.match(value):
                        if value not in issue_keys:  # Avoid duplicates
                            issue_keys.append(value)
                        break  # Found valid key in this row
        
            logger.info(f"✅ Extracted {len(issue_keys)} unique issue keys from CSV")
            return issue_keys
        
        except Exception as e:
            logger.error(f"🚩 Failed to parse CSV: {str(e)}")
            raise Exception(f"CSV parsing failed: {str(e)}")

    def fetch_issues_by_keys(self, issue_keys: List[str], include_subtasks: bool = False) -> List[Dict]:
        """
        Fetch specific issues by their keys.
    
        Args:
            issue_keys (List[str]): List of Jira issue keys
            include_subtasks (bool): Whether to include subtasks and linked issues
        
        Returns:
            List[Dict]: List of issue dictionaries with relevant data
        """
        all_issues = []
        logger.info(f"🔍 Attempting to fetch {len(issue_keys)} issue keys")
    
        # Process in batches to avoid URL length limits
        batch_size = 50  # Conservative batch size for key-based queries
    
        batch_num = 1
        for i in range(0, len(issue_keys), batch_size):
            batch_keys = issue_keys[i:i + batch_size]
        
            try:
                # Create JQL for this batch
                keys_str = ','.join(batch_keys)
                jql = f"key in ({keys_str})"
            
                logger.info(f"📦 Fetching batch {batch_num}: {len(batch_keys)} keys")
                logger.info(f"🔍 JQL query: {jql}")
            
                # Fetch this batch directly
                batch_issues = self._fetch_batch_directly(jql, len(batch_keys))
                logger.info(f"✅ Fetched {len(batch_issues)} issues from batch {batch_num}")
                all_issues.extend(batch_issues)
            
                # If including subtasks, fetch related issues
                if include_subtasks:
                    related_issues = self._fetch_related_issues(batch_keys)
                    logger.info(f"🔗 Fetched {len(related_issues)} related issues for batch {batch_num}")
                    all_issues.extend(related_issues)
                
                batch_num += 1
                
            except Exception as e:
                logger.error(f"🚩 Failed to fetch batch {batch_num}: {str(e)}")
                batch_num += 1
                continue
    
        # Remove duplicates based on key
        seen_keys = set()
        unique_issues = []
        for issue in all_issues:
            if issue['key'] not in seen_keys:
                seen_keys.add(issue['key'])
                unique_issues.append(issue)
    
        logger.info(f"✅ Final result: {len(unique_issues)} unique issues for {len(issue_keys)} requested keys")
        if len(unique_issues) == 0 and len(issue_keys) > 0:
            logger.error("🚩 No issues found! Possible causes:")
            logger.error("🚩 1. Issue keys don't exist in this Jira instance")
            logger.error("🚩 2. User doesn't have permission to view these issues")
            logger.error("🚩 3. Issues are in different projects not accessible with current token")
        
        return unique_issues

    def _fetch_related_issues(self, parent_keys: List[str]) -> List[Dict]:
        """
        Fetch subtasks and linked issues for given parent keys.
    
        Args:
            parent_keys (List[str]): List of parent issue keys
        
        Returns:
            List[Dict]: List of related issues
        """
        related_issues = []
    
        try:
            # Fetch subtasks
            keys_str = ','.join(parent_keys)
            subtask_jql = f"parent in ({keys_str})"
        
            subtasks = self._fetch_batch_directly(subtask_jql, max_results)
            related_issues.extend(subtasks)
        
            logger.info(f"🔗 Found {len(subtasks)} subtasks for parent issues")
        
            # Could also fetch linked issues here if needed
            # linked_jql = f"issue in linkedIssues({keys_str})"
        
        except Exception as e:
            logger.warning(f"⚠️ Failed to fetch related issues: {str(e)}")
    
        return related_issues
    
    def _fetch_batch_directly(self, jql_query: str, max_results: int) -> List[Dict]:
        """
        Fetch issues directly without duplicate logging.
        
        Args:
            jql_query (str): JQL query string
            max_results (int): Maximum number of results to fetch
            
        Returns:
            List[Dict]: List of issue dictionaries
        """
        issues = []
        current_start = 0
        
        while True:
            try:
                params = {
                    'jql': jql_query,
                    'startAt': current_start,
                    'maxResults': min(200, max_results - len(issues)),
                    'expand': 'changelog',
                    'fields': 'key,summary,status,created,resolutiondate,assignee,priority,issuetype'
                }
                
                response = self.session.get(
                    f'{self.base_url}/rest/api/2/search',
                    params=params
                )
                response.raise_for_status()
                
                data = response.json()
                batch_issues = data.get('issues', [])
                
                if not batch_issues:
                    break
                
                for issue in batch_issues:
                    processed_issue = self._process_issue(issue)
                    if processed_issue:
                        issues.append(processed_issue)
                
                current_start += len(batch_issues)
                
                if current_start >= data.get('total', 0) or len(issues) >= max_results:
                    break
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"🚩 API request failed: {str(e)}")
                break
        
        return issues
    
    def get_issue_comments(self, issue_key: str) -> List[Dict]:
        """
        Get all comments for a specific issue.
        
        Args:
            issue_key (str): The issue key to get comments for
            
        Returns:
            List[Dict]: List of comment dictionaries
        """
        try:
            response = self.session.get(
                f'{self.base_url}/rest/api/2/issue/{issue_key}/comment',
                timeout=self.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            return data.get('comments', [])
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to get comments for {issue_key}: {str(e)}")
            return []