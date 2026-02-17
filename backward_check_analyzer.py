"""
Backward Check Analyzer
Analyzes features/sub-features without fixVersion that have epics with children in active sprints.

Author: Pietro Maffi
"""

import logging
from typing import List, Dict, Optional, Set
from collections import defaultdict
from jira_client import JiraClient

logger = logging.getLogger('BackwardCheckAnalyzer')


class BackwardCheckAnalyzer:
    """
    Analyzes features and sub-features that don't have fixVersion set
    but have epics with children in active sprints.
    """
    
    def __init__(self, jira_client: JiraClient):
        """Initialize with Jira client."""
        self.jira_client = jira_client
    
    def analyze(self, query: str, target_fix_version: str, limit: Optional[int] = None) -> Dict:
        """
        Perform TRUE backward check analysis.
        Start from children in active sprints, trace backwards to find unmarked Features/Sub-Features.
        
        Args:
            query (str): JQL query to find parent initiatives
            target_fix_version (str): The PI/fixVersion to mark items with
            limit (int, optional): Maximum number of initiatives to analyze
            
        Returns:
            Dict: Analysis results with features/sub-features to be marked
        """
        logger.info(f"🔄 Starting TRUE Backward Check Analysis")
        logger.info(f"📋 Target Fix Version: {target_fix_version}")
        if limit:
            logger.info(f"🔢 Initiative Limit: {limit}")
        
        results = {
            'target_fix_version': target_fix_version,
            'initiatives': [],
            'features_to_mark': [],
            'sub_features_to_mark': [],
            'is_limited': False,
            'original_count': 0,
            'summary': {
                'total_features': 0,
                'total_sub_features': 0,
                'features_with_active_work': 0,
                'sub_features_with_active_work': 0,
                'epics_in_active_sprints': 0
            }
        }
        
        # Step 1: Get initiatives from query (with limit)
        logger.info("⏳ Step 1: Fetching initiatives...")
        initiatives = self._fetch_initiatives(query, limit=limit)
        results['original_count'] = len(initiatives)
        
        # Apply limit if specified
        if limit and len(initiatives) > limit:
            results['is_limited'] = True
            results['original_count'] = len(initiatives)
            initiatives = initiatives[:limit]
            logger.info(f"⚠️ Limited to first {limit} of {results['original_count']} initiatives")
        
        logger.info(f"✅ Processing {len(initiatives)} initiatives")
        
        # Step 2: Find ALL children in active sprints for these initiatives (TRUE BACKWARD START)
        logger.info("⏳ Step 2: Finding ALL children in active sprints (BACKWARD START)...")
        initiative_keys = [init['key'] for init in initiatives]
        children_in_sprints = self._find_children_in_active_sprints(initiative_keys)
        logger.info(f"✅ Found {len(children_in_sprints)} children in active sprints")
        
        # Step 3: Trace backwards from children to find Epics, Sub-Features, Features
        logger.info("⏳ Step 3: Tracing backwards from children to hierarchy...")
        epics_with_active_work = set()
        sub_features_with_active_work = {}  # key -> details
        features_with_active_work = {}  # key -> details
        
        for child in children_in_sprints:
            # Get Epic (parent of child)
            epic_key = child.get('parent_key')
            if epic_key:
                epics_with_active_work.add(epic_key)
                logger.info(f"  ← Child {child['key']} → Epic {epic_key}")
        
        logger.info(f"✅ Found {len(epics_with_active_work)} unique epics with active work")
        results['summary']['epics_in_active_sprints'] = len(epics_with_active_work)
        
        # Step 4: For each epic, trace to Sub-Feature and Feature
        logger.info("⏳ Step 4: Tracing epics back to Sub-Features and Features...")
        logger.info(f"   Processing {len(epics_with_active_work)} epics with active work...")
        
        trace_success = 0
        trace_failed = 0
        
        for epic_key in epics_with_active_work:
            hierarchy = self._trace_epic_to_hierarchy(epic_key)
            if hierarchy:
                trace_success += 1
                sub_feature = hierarchy.get('sub_feature')
                feature = hierarchy.get('feature')
                
                if sub_feature:
                    # Check if sub-feature has target fixVersion
                    if not self._has_fix_version(sub_feature['key'], target_fix_version):
                        sub_features_with_active_work[sub_feature['key']] = sub_feature
                        logger.info(f"  ✅ Epic {epic_key} → Sub-Feature {sub_feature['key']} → NEEDS {target_fix_version}")
                    else:
                        logger.info(f"  ℹ️  Epic {epic_key} → Sub-Feature {sub_feature['key']} → already has {target_fix_version}")
                
                if feature:
                    # Check if feature has target fixVersion
                    if not self._has_fix_version(feature['key'], target_fix_version):
                        features_with_active_work[feature['key']] = feature
                        logger.info(f"  ✅ Feature {feature['key']} → NEEDS {target_fix_version}")
                    else:
                        logger.info(f"  ℹ️  Feature {feature['key']} → already has {target_fix_version}")
            else:
                trace_failed += 1
                logger.error(f"  ❌ Failed to trace Epic {epic_key} - could not find parent hierarchy")
        
        logger.info(f"✅ Trace Summary: {trace_success} successful, {trace_failed} failed")
        logger.info(f"📊 Result: {len(sub_features_with_active_work)} sub-features and {len(features_with_active_work)} features need {target_fix_version}")
        
        # Step 5: Build the display hierarchy (for UI)
        logger.info("⏳ Step 5: Building display hierarchy...")
        for initiative in initiatives:
            logger.info(f"🔍 Building hierarchy for Initiative: {initiative['key']}")
            
            # Get all features for this initiative
            features = self._fetch_features_not_done(initiative['key'])
            
            for feature in features:
                feature_has_active_work = feature['key'] in features_with_active_work
                
                # Get sub-features
                sub_features = self._fetch_sub_features_not_done(feature['key'])
                
                for sub_feature in sub_features:
                    sub_feature_has_active_work = sub_feature['key'] in sub_features_with_active_work
                    
                    # Get epics and mark those with active work
                    epics = self._fetch_epics(sub_feature['key'])
                    epics_by_area = defaultdict(list)
                    
                    for epic in epics:
                        if epic['key'] in epics_with_active_work:
                            epic['risk_probability'] = 1  # GREEN - active work
                            epic['has_active_sprint'] = True
                            logger.info(f"      ✓ Epic {epic['key']} marked GREEN (active sprint work)")
                        else:
                            epic['has_active_sprint'] = False
                        
                        area = epic.get('project_key', 'Unknown')
                        epics_by_area[area].append(epic)
                    
                    sub_feature['epics_by_area'] = dict(epics_by_area)
                    sub_feature['has_active_work'] = sub_feature_has_active_work
                    sub_feature['marked_fix_version'] = target_fix_version if sub_feature_has_active_work else None
                    
                    if sub_feature_has_active_work:
                        results['sub_features_to_mark'].append({
                            'key': sub_feature['key'],
                            'summary': sub_feature['summary'],
                            'target_fix_version': target_fix_version
                        })
                        results['summary']['sub_features_with_active_work'] += 1
                
                feature['sub_features'] = sub_features
                feature['has_active_work'] = feature_has_active_work
                feature['marked_fix_version'] = target_fix_version if feature_has_active_work else None
                
                if feature_has_active_work:
                    results['features_to_mark'].append({
                        'key': feature['key'],
                        'summary': feature['summary'],
                        'target_fix_version': target_fix_version
                    })
                    results['summary']['features_with_active_work'] += 1
                
                results['summary']['total_sub_features'] += len(sub_features)
            
            initiative['features'] = features
            results['initiatives'].append(initiative)
            results['summary']['total_features'] += len(features)
        
        logger.info("✅ Backward Check Analysis Complete")
        logger.info(f"📊 Summary: {results['summary']}")
        
        return results
    
    def _find_children_in_active_sprints(self, initiative_keys: List[str]) -> List[Dict]:
        """
        TRUE BACKWARD CHECK: Find ALL children (stories/tasks) in active sprints
        that are connected to the given initiatives.
        
        Args:
            initiative_keys: List of initiative keys to search within
            
        Returns:
            List of children (with parent epic key) that are in active sprints
        """
        logger.info(f"🔍 BACKWARD CHECK - Finding children in active sprints for {len(initiative_keys)} initiatives")
        
        # JQL doesn't support multiple childIssuesOfRecursive in one query
        # We need to query each initiative separately and combine results
        all_children = []
        seen_keys = set()  # Deduplicate
        
        for init_key in initiative_keys:
            try:
                # Walk hierarchy manually: Get Features, then Sub-Features, then Epics
                # Get all Features under this Initiative
                features_jql = f'issuekey in childIssuesOf("{init_key}") AND issuetype = Feature'
                
                features = self.jira_client.fetch_issues(features_jql, max_results=200)
                logger.info(f"   📍 {init_key}: Found {len(features)} features")
                
                for feature in features:
                    feature_key = feature['key']
                    
                    # Get Sub-Features under this Feature
                    sf_jql = f'issuekey in childIssuesOf("{feature_key}") AND issuetype = "Sub-Feature"'
                    sub_features = self.jira_client.fetch_issues(sf_jql, max_results=200)
                    
                    for sub_feature in sub_features:
                        sf_key = sub_feature['key']
                        
                        # Get Epics under this Sub-Feature
                        epics_jql = f'issuekey in childIssuesOf("{sf_key}") AND issuetype = Epic'
                        epics = self.jira_client.fetch_issues(epics_jql, max_results=500)
                        
                        for epic in epics:
                            epic_key = epic['key']
                            
                            # Check if epic has children OR subtasks in active sprints
                            # Query: Stories/Tasks linked to epic + their subtasks
                            children_jql = f'("Epic Link" = {epic_key} OR issue IN subtasksOf(\'"Epic Link" = {epic_key}\')) AND sprint IN openSprints()'
                            children = self.jira_client.fetch_issues(children_jql, max_results=100)
                            
                            if children:
                                logger.info(f"      ✓ Epic {epic_key}: {len(children)} children in active sprints")
                                
                                for child in children:
                                    child_key = child['key']
                                    if child_key in seen_keys:
                                        continue
                                    seen_keys.add(child_key)
                                    
                                    all_children.append({
                                        'key': child_key,
                                        'summary': child['fields'].get('summary', 'N/A'),
                                        'parent_key': epic_key
                                    })
                    
            except Exception as e:
                logger.error(f"   ❌ Failed for {init_key}: {str(e)}")
                continue
        
        logger.info(f"✅ Total: Found {len(all_children)} unique children in active sprints")
        return all_children
    
    def _trace_epic_to_hierarchy(self, epic_key: str) -> Optional[Dict]:
        """
        Trace an epic backwards to its Sub-Feature and Feature.
        
        Args:
            epic_key: The epic key to trace
            
        Returns:
            Dict with 'sub_feature' and 'feature' details, or None if not found
        """
        try:
            # Get epic details to find its parent (Sub-Feature)
            logger.info(f"🔍 Tracing Epic {epic_key} back to hierarchy...")
            epic_response = self.jira_client.session.get(
                f"{self.jira_client.base_url}/rest/api/2/issue/{epic_key}",
                params={'fields': 'parent,issuetype,summary'}
            )
            
            if epic_response.status_code != 200:
                logger.error(f"❌ Could not fetch epic {epic_key} (HTTP {epic_response.status_code})")
                return None
            
            epic_data = epic_response.json()
            parent = epic_data['fields'].get('parent')
            
            if not parent:
                logger.warning(f"⚠️ Epic {epic_key} has NO parent field (orphaned epic)")
                # Try to find parent via JQL as fallback
                try:
                    parent_jql = f'issue IN parentIssuesOf("{epic_key}")'
                    parents = self.jira_client.fetch_issues(parent_jql, max_results=1)
                    if parents:
                        parent_key = parents[0]['key']
                        parent_type = parents[0]['fields'].get('issuetype', {}).get('name', '')
                        logger.info(f"   ✓ Found parent via JQL: {parent_key} ({parent_type})")
                        
                        if parent_type == 'Sub-Feature':
                            sub_feature_data = self._fetch_issue_details(parent_key)
                            # Now get the feature (parent of sub-feature)
                            return self._trace_sub_feature_to_feature(parent_key, sub_feature_data)
                        else:
                            logger.warning(f"   Parent {parent_key} is {parent_type}, not Sub-Feature")
                            return None
                    else:
                        logger.error(f"   No parent found via JQL either")
                        return None
                except Exception as e:
                    logger.error(f"   Failed to find parent via JQL: {e}")
                    return None
            
            sub_feature_key = parent.get('key')
            sub_feature_type = parent['fields'].get('issuetype', {}).get('name', '')
            
            if sub_feature_type != 'Sub-Feature':
                logger.warning(f"⚠️ Epic {epic_key} parent is '{sub_feature_type}', not 'Sub-Feature'")
                return None
            
            logger.info(f"   ✓ Epic {epic_key} → Sub-Feature {sub_feature_key}")
            
            # Get Sub-Feature details
            sub_feature_data = self._fetch_issue_details(sub_feature_key)
            
            # Now get the feature (parent of sub-feature)
            return self._trace_sub_feature_to_feature(sub_feature_key, sub_feature_data)
            
        except Exception as e:
            logger.error(f"❌ Failed to trace epic {epic_key} to hierarchy: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    def _trace_sub_feature_to_feature(self, sub_feature_key: str, sub_feature_data: Dict) -> Dict:
        """
        Trace a sub-feature to its parent feature.
        
        Args:
            sub_feature_key: The sub-feature key
            sub_feature_data: Already fetched sub-feature details
            
        Returns:
            Dict with 'sub_feature' and 'feature' details
        """
        try:
            # Get Feature (parent of Sub-Feature)
            sub_feature_response = self.jira_client.session.get(
                f"{self.jira_client.base_url}/rest/api/2/issue/{sub_feature_key}",
                params={'fields': 'parent,issuetype'}
            )
            
            if sub_feature_response.status_code != 200:
                logger.warning(f"⚠️ Could not fetch sub-feature {sub_feature_key}")
                return {'sub_feature': sub_feature_data, 'feature': None}
            
            sub_feature_full = sub_feature_response.json()
            sf_parent = sub_feature_full['fields'].get('parent')
            
            if not sf_parent:
                logger.warning(f"⚠️ Sub-Feature {sub_feature_key} has NO parent")
                # Try JQL fallback
                try:
                    parent_jql = f'issue IN parentIssuesOf("{sub_feature_key}")'
                    parents = self.jira_client.fetch_issues(parent_jql, max_results=1)
                    if parents:
                        feature_key = parents[0]['key']
                        feature_type = parents[0]['fields'].get('issuetype', {}).get('name', '')
                        logger.info(f"   ✓ Found feature via JQL: {feature_key} ({feature_type})")
                        
                        if feature_type == 'Feature':
                            feature_data = self._fetch_issue_details(feature_key)
                            logger.info(f"   ✓ Sub-Feature {sub_feature_key} → Feature {feature_key}")
                            return {'sub_feature': sub_feature_data, 'feature': feature_data}
                except Exception as e:
                    logger.error(f"   Failed to find feature via JQL: {e}")
                
                return {'sub_feature': sub_feature_data, 'feature': None}
            
            feature_key = sf_parent.get('key')
            feature_type = sf_parent['fields'].get('issuetype', {}).get('name', '')
            
            if feature_type != 'Feature':
                logger.warning(f"⚠️ Sub-Feature {sub_feature_key} parent is '{feature_type}', not 'Feature'")
                return {'sub_feature': sub_feature_data, 'feature': None}
            
            logger.info(f"   ✓ Sub-Feature {sub_feature_key} → Feature {feature_key}")
            
            # Get Feature details
            feature_data = self._fetch_issue_details(feature_key)
            
            return {
                'sub_feature': sub_feature_data,
                'feature': feature_data
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to trace sub-feature {sub_feature_key} to feature: {str(e)}")
            return {'sub_feature': sub_feature_data, 'feature': None}
    
    def _has_fix_version(self, issue_key: str, target_fix_version: str) -> bool:
        """
        Check if an issue already has the target fix version.
        
        Args:
            issue_key: The issue key to check
            target_fix_version: The fix version to look for
            
        Returns:
            bool: True if issue has the target fix version
        """
        try:
            response = self.jira_client.session.get(
                f"{self.jira_client.base_url}/rest/api/2/issue/{issue_key}",
                params={'fields': 'fixVersions'}
            )
            
            if response.status_code != 200:
                return False
            
            data = response.json()
            fix_versions = data['fields'].get('fixVersions', [])
            
            for fv in fix_versions:
                if fv.get('name', '').strip() == target_fix_version.strip():
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to check fixVersion for {issue_key}: {str(e)}")
            return False
    
    def _fetch_initiatives(self, query: str, limit: Optional[int] = None) -> List[Dict]:
        """Fetch initiatives based on query.
        
        Args:
            query (str): JQL query to find initiatives
            limit (int, optional): Maximum number of initiatives to fetch
        """
        try:
            # Use the limit as max_results to avoid fetching unnecessary data
            max_results = limit if limit else 100
            logger.info(f"🔍 Fetching max {max_results} initiatives from Jira")
            issues = self.jira_client.fetch_issues(query, max_results=max_results)
            logger.info(f"📥 Received {len(issues)} initiatives from Jira")
            
            initiatives = []
            for issue in issues:
                initiative_data = self._fetch_issue_details(issue['key'])
                if initiative_data:
                    initiatives.append(initiative_data)
            
            return initiatives
        except Exception as e:
            logger.error(f"Failed to fetch initiatives: {str(e)}")
            return []
    
    def _fetch_features_not_done(self, initiative_key: str) -> List[Dict]:
        """Fetch features that are not done (regardless of fixVersion)."""
        # More permissive query - just get all Features under the initiative
        # Status filter is more flexible
        jql = (f'issuekey in childIssuesOf("{initiative_key}") '
               f'AND issuetype = Feature')
        
        try:
            logger.info(f"🔍 Backward Check Features JQL: {jql}")
            issues = self.jira_client.fetch_issues(jql, max_results=200)
            logger.info(f"   Found {len(issues)} features (all statuses)")
            
            # Filter out done statuses manually to be more flexible
            features = []
            done_statuses = ['done', 'closed', 'resolved', 'completed', 'prod deployed']
            
            for issue in issues:
                feature_data = self._fetch_issue_details(issue['key'])
                if feature_data:
                    # Check if status is not done
                    status = feature_data.get('status', '').lower()
                    if status not in done_statuses:
                        features.append(feature_data)
                        logger.info(f"   ✓ Including Feature {feature_data['key']} (status: {feature_data['status']})")
                    else:
                        logger.info(f"   ✗ Skipping Feature {feature_data['key']} (status: {feature_data['status']} - DONE)")
            
            logger.info(f"   Result: {len(features)} not-done features")
            return features
        except Exception as e:
            logger.error(f"Failed to fetch not-done features for {initiative_key}: {str(e)}")
            return []
    
    def _fetch_sub_features_not_done(self, feature_key: str) -> List[Dict]:
        """Fetch sub-features that are not done (regardless of fixVersion)."""
        # More permissive query
        jql = (f'issuekey in childIssuesOf("{feature_key}") '
               f'AND issuetype = "Sub-Feature"')
        
        try:
            logger.debug(f"🔍 Backward Check Sub-Features JQL: {jql}")
            issues = self.jira_client.fetch_issues(jql, max_results=200)
            logger.debug(f"   Found {len(issues)} sub-features (all statuses)")
            
            # Filter out done statuses manually
            sub_features = []
            done_statuses = ['done', 'closed', 'resolved', 'completed', 'prod deployed']
            
            for issue in issues:
                sub_feature_data = self._fetch_issue_details(issue['key'])
                if sub_feature_data:
                    status = sub_feature_data.get('status', '').lower()
                    if status not in done_statuses:
                        sub_features.append(sub_feature_data)
                        logger.debug(f"   ✓ Including Sub-Feature {sub_feature_data['key']} (status: {sub_feature_data['status']})")
                    else:
                        logger.debug(f"   ✗ Skipping Sub-Feature {sub_feature_data['key']} (status: {sub_feature_data['status']} - DONE)")
            
            logger.debug(f"   Result: {len(sub_features)} not-done sub-features")
            return sub_features
        except Exception as e:
            logger.error(f"Failed to fetch not-done sub-features for {feature_key}: {str(e)}")
            return []
            
            return sub_features
        except Exception as e:
            logger.error(f"Failed to fetch not-done sub-features for {feature_key}: {str(e)}")
            return []
    
    def _fetch_epics(self, sub_feature_key: str) -> List[Dict]:
        """Fetch all epics under a sub-feature."""
        jql = f'issuekey in childIssuesOf("{sub_feature_key}") AND issuetype = Epic'
        
        try:
            issues = self.jira_client.fetch_issues(jql, max_results=500)
            
            epics = []
            for issue in issues:
                epic_data = self._fetch_issue_details(issue['key'])
                if epic_data:
                    epics.append(epic_data)
            
            return epics
        except Exception as e:
            logger.error(f"Failed to fetch epics for {sub_feature_key}: {str(e)}")
            return []
    
    def _has_children_in_active_sprint(self, epic_key: str) -> bool:
        """
        Check if an epic has any children (stories/tasks via Epic Link) or their subtasks in an active sprint.
        Uses the correct query: "Epic Link" = epic OR subtasks of items with that Epic Link.
        
        Returns:
            bool: True if epic has children or subtasks in active sprints
        """
        # Query for:
        # 1. Items with Epic Link = this epic
        # 2. Subtasks of items with Epic Link = this epic
        # Both filtered by openSprints()
        jql = f'("Epic Link" = {epic_key} OR issue IN subtasksOf(\'"Epic Link" = {epic_key}\')) AND sprint IN openSprints()'
        
        try:
            logger.debug(f"  🔍 Checking active sprints for Epic {epic_key}")
            logger.debug(f"      JQL: {jql}")
            
            children_in_active_sprints = self.jira_client.fetch_issues(jql, max_results=1)
            
            if children_in_active_sprints:
                logger.info(f"      ✅ Epic {epic_key} has {len(children_in_active_sprints)} children/subtasks in ACTIVE sprints")
                # Log first few children
                for child in children_in_active_sprints[:3]:
                    logger.info(f"         → {child['key']}: {child['fields'].get('summary', 'N/A')}")
                return True
            else:
                logger.debug(f"      ✗ Epic {epic_key} has NO children/subtasks in active sprints")
                return False
            
        except Exception as e:
            logger.error(f"Failed to check active sprints for epic {epic_key}: {str(e)}")
            logger.error(f"   JQL used: {jql}")
            # Try alternative approach: check for any children first
            try:
                logger.info(f"   Trying alternative: Check if epic has any children...")
                jql_any_children = f'"Epic Link" = {epic_key}'
                any_children = self.jira_client.fetch_issues(jql_any_children, max_results=5)
                if any_children:
                    logger.info(f"   Epic {epic_key} has {len(any_children)} children (but sprint check failed)")
                    logger.info(f"   First child: {any_children[0]['key']}")
                else:
                    logger.info(f"   Epic {epic_key} has NO children at all")
            except:
                pass
            return False
    
    def _fetch_issue_details(self, issue_key: str) -> Optional[Dict]:
        """Fetch detailed information for a single issue."""
        try:
            response = self.jira_client.session.get(
                f"{self.jira_client.base_url}/rest/api/2/issue/{issue_key}",
                params={'expand': 'names'}
            )
            
            if response.status_code != 200:
                logger.warning(f"Failed to fetch details for {issue_key}")
                return None
            
            data = response.json()
            fields = data.get('fields', {})
            
            assignee = fields.get('assignee')
            assignee_name = assignee.get('displayName', 'Unassigned') if assignee else 'Unassigned'
            
            status = fields.get('status', {})
            status_name = status.get('name', 'Unknown')
            
            project = fields.get('project', {})
            project_key = project.get('key', 'Unknown')
            
            return {
                'key': issue_key,
                'summary': fields.get('summary', 'No summary'),
                'assignee': assignee_name,
                'status': status_name,
                'project_key': project_key,
                'risk_probability': None  # Will be set later if needed
            }
        except Exception as e:
            logger.error(f"Failed to fetch details for {issue_key}: {str(e)}")
            return {
                'key': issue_key,
                'summary': 'Error fetching details',
                'assignee': 'Unknown',
                'status': 'Unknown',
                'project_key': 'Unknown',
                'risk_probability': None
            }
