"""
Static fixtures and mock data for Initiative Viewer testing
Provides realistic Jira responses without requiring actual Jira connection
"""

import json
from typing import Dict, List


class MockJiraResponses:
    """Static mock responses simulating Jira API behavior."""
    
    @staticmethod
    def authentication_error():
        """Simulate authentication failure (401)."""
        return {
            'errorMessages': ['Client must be authenticated to access this resource.'],
            'errors': {}
        }
    
    @staticmethod
    def authorization_error():
        """Simulate authorization failure (403)."""
        return {
            'errorMessages': ["You do not have the permission to see the specified issue."],
            'errors': {}
        }
    
    @staticmethod
    def jql_syntax_error():
        """Simulate JQL syntax error (400)."""
        return {
            'errorMessages': [
                "Error in the JQL Query: The character '\"' is a reserved JQL character."
            ],
            'errors': {}
        }
    
    @staticmethod
    def valid_business_initiative():
        """Mock a complete Business Initiative with full hierarchy."""
        return {
            'key': 'PROJ-1',
            'id': '10001',
            'self': 'https://jira.example.com/rest/api/2/issue/10001',
            'fields': {
                'summary': 'Customer Portal Modernization',
                'description': 'Modernize the customer portal with new UI/UX',
                'status': {
                    'name': 'In Progress',
                    'id': '3',
                    'statusCategory': {'name': 'In Progress', 'key': 'indeterminate'}
                },
                'assignee': {
                    'displayName': 'John Doe',
                    'emailAddress': 'john.doe@example.com',
                    'key': 'jdoe'
                },
                'reporter': {
                    'displayName': 'Jane Smith',
                    'emailAddress': 'jane.smith@example.com'
                },
                'priority': {'name': 'High', 'id': '2'},
                'project': {'key': 'PROJ', 'name': 'Project Alpha'},
                'issuetype': {'name': 'Business Initiative', 'subtask': False},
                'created': '2025-01-15T10:30:00.000+0000',
                'updated': '2025-02-10T14:20:00.000+0000',
                'fixVersions': [{'name': 'v1.0', 'id': '10100'}],
                'labels': ['customer-facing', 'strategic'],
                'customfield_12345': 3,  # Risk probability
                'issuelinks': [
                    {
                        'id': '10201',
                        'type': {
                            'name': 'Feature',
                            'inward': 'has feature',
                            'outward': 'is feature of'
                        },
                        'outwardIssue': {
                            'key': 'PROJ-10',
                            'fields': {
                                'summary': 'New Login System',
                                'status': {'name': 'In Progress'},
                                'assignee': {'displayName': 'Bob Wilson'}
                            }
                        }
                    }
                ]
            }
        }
    
    @staticmethod
    def valid_feature():
        """Mock a Feature issue."""
        return {
            'key': 'PROJ-10',
            'id': '10010',
            'fields': {
                'summary': 'New Login System',
                'description': 'Implement OAuth2 login',
                'status': {'name': 'In Progress'},
                'assignee': {'displayName': 'Bob Wilson'},
                'issuetype': {'name': 'Feature'},
                'project': {'key': 'PROJ', 'name': 'Project Alpha'},
                'fixVersions': [{'name': 'v1.0'}],
                'customfield_12345': 2,  # Risk probability
                'issuelinks': [
                    {
                        'type': {'name': 'Sub-Feature'},
                        'outwardIssue': {
                            'key': 'PROJ-100',
                            'fields': {
                                'summary': 'OAuth Provider Integration',
                                'status': {'name': 'In Progress'},
                                'assignee': {'displayName': 'Alice Brown'}
                            }
                        }
                    }
                ]
            }
        }
    
    @staticmethod
    def valid_sub_feature():
        """Mock a Sub-Feature issue."""
        return {
            'key': 'PROJ-100',
            'id': '10100',
            'fields': {
                'summary': 'OAuth Provider Integration',
                'description': 'Integrate with Google and Microsoft OAuth',
                'status': {'name': 'In Progress'},
                'assignee': {'displayName': 'Alice Brown'},
                'issuetype': {'name': 'Sub-Feature'},
                'project': {'key': 'PROJ'},
                'fixVersions': [{'name': 'v1.0'}],
                'customfield_12345': 1,  # Risk probability
                'issuelinks': [
                    {
                        'type': {'name': 'Epic'},
                        'outwardIssue': {
                            'key': 'PROJ-1000',
                            'fields': {
                                'summary': 'Google OAuth Integration',
                                'status': {'name': 'Done'},
                                'assignee': {'displayName': 'Charlie Davis'}
                            }
                        }
                    },
                    {
                        'type': {'name': 'Epic'},
                        'outwardIssue': {
                            'key': 'PROJ-1001',
                            'fields': {
                                'summary': 'Microsoft OAuth Integration',
                                'status': {'name': 'In Progress'},
                                'assignee': {'displayName': 'Diana Evans'}
                            }
                        }
                    }
                ]
            }
        }
    
    @staticmethod
    def valid_epic():
        """Mock an Epic issue."""
        return {
            'key': 'PROJ-1000',
            'id': '11000',
            'fields': {
                'summary': 'Google OAuth Integration',
                'description': 'Complete Google OAuth 2.0 integration',
                'status': {'name': 'Done'},
                'assignee': {'displayName': 'Charlie Davis'},
                'issuetype': {'name': 'Epic'},
                'project': {'key': 'PROJ'},
                'fixVersions': [{'name': 'v1.0'}],
                'issuelinks': []
            }
        }
    
    @staticmethod
    def business_initiative_with_area():
        """Mock initiative with area/component."""
        initiative = MockJiraResponses.valid_business_initiative()
        initiative['fields']['components'] = [{'name': 'Customer Portal'}]
        initiative['fields']['customfield_area'] = 'Area A'
        return initiative
    
    @staticmethod
    def initiative_high_risk():
        """Mock high-risk initiative (risk = 5)."""
        initiative = MockJiraResponses.valid_business_initiative()
        initiative['key'] = 'PROJ-2'
        initiative['fields']['summary'] = 'Critical Security Upgrade'
        initiative['fields']['customfield_12345'] = 5  # High risk
        initiative['fields']['priority'] = {'name': 'Critical'}
        return initiative
    
    @staticmethod
    def initiative_completed():
        """Mock completed initiative."""
        initiative = MockJiraResponses.valid_business_initiative()
        initiative['key'] = 'PROJ-3'
        initiative['fields']['summary'] = 'Q4 2025 Improvements'
        initiative['fields']['status'] = {'name': 'Done'}
        return initiative
    
    @staticmethod
    def empty_search_result():
        """Mock empty search result (no issues found)."""
        return {
            'startAt': 0,
            'maxResults': 50,
            'total': 0,
            'issues': []
        }
    
    @staticmethod
    def search_result_with_initiatives(count=3):
        """Mock search result with multiple initiatives."""
        initiatives = [
            MockJiraResponses.valid_business_initiative(),
            MockJiraResponses.initiative_high_risk(),
            MockJiraResponses.initiative_completed()
        ]
        
        return {
            'startAt': 0,
            'maxResults': 50,
            'total': count,
            'issues': initiatives[:count]
        }


class MockJiraClient:
    """
    Mock Jira client for testing without actual Jira connection.
    Simulates JiraClient behavior with predefined responses.
    """
    
    def __init__(self, jira_url, email, api_token, simulate_error=None):
        """
        Initialize mock client.
        
        Args:
            jira_url: Jira URL (not actually used)
            email: Email (not actually used)
            api_token: API token (not actually used)
            simulate_error: Type of error to simulate ('auth', 'permission', 'jql', None)
        """
        self.jira_url = jira_url
        self.email = email
        self.api_token = api_token
        self.simulate_error = simulate_error
        self._search_call_count = 0
    
    def search_issues(self, jql, max_results=50, fields=None):
        """
        Mock search_issues method.
        
        Args:
            jql: JQL query string
            max_results: Maximum results to return
            fields: Fields to include
            
        Returns:
            List of mock issue dictionaries
            
        Raises:
            Exception: If simulate_error is set
        """
        self._search_call_count += 1
        
        # Simulate authentication error
        if self.simulate_error == 'auth':
            raise Exception('401 Client Error: Unauthorized. Authentication failed.')
        
        # Simulate permission error
        if self.simulate_error == 'permission':
            raise Exception('403 Forbidden: You do not have permission.')
        
        # Simulate JQL syntax error
        if self.simulate_error == 'jql':
            raise Exception('400 Bad Request: Error in JQL Query')
        
        # Parse JQL to determine what to return
        if 'type = "Business Initiative"' in jql or "type = 'Business Initiative'" in jql:
            # Return initiatives
            if 'key = PROJ-1' in jql:
                return [MockJiraResponses.valid_business_initiative()]
            elif 'status = Done' in jql:
                return [MockJiraResponses.initiative_completed()]
            elif 'fixVersion = "v1.0"' in jql:
                return [
                    MockJiraResponses.valid_business_initiative(),
                    MockJiraResponses.initiative_high_risk()
                ]
            else:
                return MockJiraResponses.search_result_with_initiatives(3)['issues']
        
        elif 'type = Feature' in jql or "type = 'Feature'" in jql:
            return [MockJiraResponses.valid_feature()]
        
        elif 'type = "Sub-Feature"' in jql:
            return [MockJiraResponses.valid_sub_feature()]
        
        elif 'type = Epic' in jql:
            return [MockJiraResponses.valid_epic()]
        
        # Default: return empty
        return []
    
    def get_issue(self, issue_key):
        """
        Mock get_issue method.
        
        Args:
            issue_key: Issue key to retrieve
            
        Returns:
            Mock issue dictionary
        """
        if self.simulate_error == 'auth':
            raise Exception('401 Unauthorized')
        
        # Return appropriate mock based on key
        if issue_key.startswith('PROJ-1') and len(issue_key) == 6:
            return MockJiraResponses.valid_business_initiative()
        elif issue_key.startswith('PROJ-10'):
            return MockJiraResponses.valid_feature()
        elif issue_key.startswith('PROJ-100'):
            return MockJiraResponses.valid_sub_feature()
        elif issue_key.startswith('PROJ-1000'):
            return MockJiraResponses.valid_epic()
        else:
            raise Exception(f'404 Not Found: Issue {issue_key} does not exist')
    
    def get_search_call_count(self):
        """Get number of times search_issues was called."""
        return self._search_call_count


def create_mock_hierarchy_data():
    """
    Create a complete mock hierarchy structure for testing.
    Returns data in the format expected by InitiativeViewerPDFGenerator.
    """
    return [
        {
            'key': 'PROJ-1',
            'summary': 'Customer Portal Modernization',
            'status': 'In Progress',
            'assignee': 'John Doe',
            'area': 'Customer Experience',
            'risk_probability': 3,
            'fix_version': 'v1.0',
            'features': [
                {
                    'key': 'PROJ-10',
                    'summary': 'New Login System',
                    'status': 'In Progress',
                    'assignee': 'Bob Wilson',
                    'risk_probability': 2,
                    'sub_features': [
                        {
                            'key': 'PROJ-100',
                            'summary': 'OAuth Provider Integration',
                            'status': 'In Progress',
                            'assignee': 'Alice Brown',
                            'risk_probability': 1,
                            'epics': [
                                {
                                    'key': 'PROJ-1000',
                                    'summary': 'Google OAuth Integration',
                                    'status': 'Done',
                                    'assignee': 'Charlie Davis',
                                    'fix_version': 'v1.0'
                                },
                                {
                                    'key': 'PROJ-1001',
                                    'summary': 'Microsoft OAuth Integration',
                                    'status': 'In Progress',
                                    'assignee': 'Diana Evans',
                                    'fix_version': 'v1.0'
                                }
                            ]
                        }
                    ]
                },
                {
                    'key': 'PROJ-11',
                    'summary': 'User Profile Management',
                    'status': 'To Do',
                    'assignee': 'Frank Green',
                    'risk_probability': 2,
                    'sub_features': [
                        {
                            'key': 'PROJ-110',
                            'summary': 'Profile Edit Feature',
                            'status': 'To Do',
                            'assignee': 'Grace Hall',
                            'risk_probability': 1,
                            'epics': [
                                {
                                    'key': 'PROJ-1100',
                                    'summary': 'Profile UI Components',
                                    'status': 'To Do',
                                    'assignee': 'Henry Irving',
                                    'fix_version': 'v1.0'
                                }
                            ]
                        }
                    ]
                }
            ]
        },
        {
            'key': 'PROJ-2',
            'summary': 'Critical Security Upgrade',
            'status': 'In Progress',
            'assignee': 'Sarah Johnson',
            'area': 'Security',
            'risk_probability': 5,
            'fix_version': 'v1.0',
            'features': [
                {
                    'key': 'PROJ-20',
                    'summary': 'Encryption Enhancement',
                    'status': 'In Progress',
                    'assignee': 'Tom Lee',
                    'risk_probability': 5,
                    'sub_features': [
                        {
                            'key': 'PROJ-200',
                            'summary': 'TLS 1.3 Implementation',
                            'status': 'In Progress',
                            'assignee': 'Uma Patel',
                            'risk_probability': 4,
                            'epics': [
                                {
                                    'key': 'PROJ-2000',
                                    'summary': 'Certificate Management',
                                    'status': 'In Progress',
                                    'assignee': 'Victor Moore',
                                    'fix_version': 'v1.0'
                                }
                            ]
                        }
                    ]
                }
            ]
        },
        {
            'key': 'PROJ-3',
            'summary': 'Q4 2025 Improvements',
            'status': 'Done',
            'assignee': 'William Brown',
            'area': 'Platform',
            'risk_probability': 1,
            'fix_version': 'v1.0',
            'features': [
                {
                    'key': 'PROJ-30',
                    'summary': 'Performance Optimization',
                    'status': 'Done',
                    'assignee': 'Xavier Chen',
                    'risk_probability': 1,
                    'sub_features': [
                        {
                            'key': 'PROJ-300',
                            'summary': 'Database Query Optimization',
                            'status': 'Done',
                            'assignee': 'Yara Kim',
                            'risk_probability': 1,
                            'epics': [
                                {
                                    'key': 'PROJ-3000',
                                    'summary': 'Index Optimization',
                                    'status': 'Done',
                                    'assignee': 'Zack White',
                                    'fix_version': 'v1.0'
                                }
                            ]
                        }
                    ]
                }
            ]
        }
    ]


def create_mock_empty_hierarchy():
    """Create initiatives with no features/epics."""
    return [
        {
            'key': 'PROJ-99',
            'summary': 'Empty Initiative',
            'status': 'To Do',
            'assignee': 'Test User',
            'area': 'Test Area',
            'risk_probability': None,
            'fix_version': 'v1.0',
            'features': []
        }
    ]


def create_mock_areas():
    """Create mock areas list."""
    return ['Customer Experience', 'Security', 'Platform', 'Infrastructure']


# Export convenience functions
def get_mock_jira_client(simulate_error=None):
    """
    Get a configured mock Jira client.
    
    Args:
        simulate_error: 'auth', 'permission', 'jql', or None
    
    Returns:
        MockJiraClient instance
    """
    return MockJiraClient(
        jira_url='https://jira.example.com',
        email='test@example.com',
        api_token='mock-token-12345',
        simulate_error=simulate_error
    )


def get_valid_test_credentials():
    """Get valid credentials for testing (don't need to be real)."""
    return {
        'jira_url': 'https://jira.example.com',
        'email': 'test@example.com',
        'api_token': 'mock-token-12345',
        'jql': 'project = PROJ AND type = "Business Initiative"',
        'fix_version': 'v1.0'
    }
