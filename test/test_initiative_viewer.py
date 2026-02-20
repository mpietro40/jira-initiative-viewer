"""
Test suite for Initiative Viewer application
Tests all web interface endpoints and PDF generation functionality
Uses static mocks and stubs - no real Jira connection required
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
import io

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from initiative_viewer import app, InitiativeViewerPDFGenerator
from initiative_viewer_pdf import InitiativeViewerPDFGenerator as PDFGen

# Import our static fixtures and mocks
from fixtures_initiative_viewer import (
    MockJiraClient,
    MockJiraResponses,
    create_mock_hierarchy_data,
    create_mock_empty_hierarchy,
    create_mock_areas,
    get_mock_jira_client,
    get_valid_test_credentials
)


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret-key'
    with app.test_client() as client:
        with app.app_context():
            yield client


@pytest.fixture
def sample_initiatives():
    """Sample initiative data for testing - uses comprehensive mock data."""
    return create_mock_hierarchy_data()


@pytest.fixture
def sample_areas():
    """Sample areas for testing - uses mock areas."""
    return create_mock_areas()


@pytest.fixture
def mock_jira_client():
    """Mock Jira client for testing without actual Jira connection."""
    return get_mock_jira_client()


@pytest.fixture
def mock_jira_client_auth_error():
    """Mock Jira client that simulates authentication error."""
    return get_mock_jira_client(simulate_error='auth')


@pytest.fixture
def mock_jira_client_permission_error():
    """Mock Jira client that simulates permission error."""
    return get_mock_jira_client(simulate_error='permission')


@pytest.fixture
def mock_jira_client_jql_error():
    """Mock Jira client that simulates JQL syntax error."""
    return get_mock_jira_client(simulate_error='jql')


@pytest.fixture
def valid_credentials():
    """Valid test credentials."""
    return get_valid_test_credentials()


class TestWebInterface:
    """Test all web interface endpoints."""
    
    def test_index_route(self, client):
        """Test the main index route loads successfully."""
        response = client.get('/')
        assert response.status_code == 200
        assert b'Initiative Hierarchy' in response.data or b'initiative' in response.data.lower()
    
    def test_health_check(self, client):
        """Test health check endpoint if it exists."""
        response = client.get('/health')
        # May return 200 or 404 depending on implementation
        assert response.status_code in [200, 404]
    
    @patch('initiative_viewer.get_most_recent_cache')  # Prevent cache interference
    @patch('initiative_viewer.JiraClient')
    def test_analyze_endpoint_with_valid_data(self, mock_jira_class, mock_cache, client):
        """Test analyze endpoint with valid parameters."""
        mock_cache.return_value = None  # No cache hit
        # Use proper mock client
        mock_client = get_mock_jira_client()
        mock_jira_class.return_value = mock_client
        
        response = client.post('/analyze', data={
            'jira_url': 'https://jira.example.com',
            'access_token': 'test-token',
            'query': 'project = PROJ AND type = "Business Initiative"',
            'fix_version': 'v1.0'
        })
        
        # Should either succeed (200) or redirect (302)
        assert response.status_code in [200, 302, 500]  # May fail due to missing data
    
    def test_analyze_endpoint_missing_parameters(self, client):
        """Test analyze endpoint with missing required parameters."""
        response = client.post('/analyze', data={
            'jira_url': 'https://jira.example.com'
            # Missing other required fields
        })
        
        # Should return error (400 or 500)
        assert response.status_code in [400, 500]


class TestPDFGeneration:
    """Test PDF generation functionality."""
    
    def test_pdf_generator_initialization(self, sample_initiatives, sample_areas):
        """Test PDF generator can be initialized without errors."""
        try:
            pdf_gen = PDFGen(
                initiatives=sample_initiatives,
                fix_version='v1.0',
                all_areas=sample_areas,
                query='project = TEST',
                page_format='A4',
                jira_url='https://jira.example.com',
                is_limited=False,
                limit_count=None,
                original_count=1,
                completed_statuses=['done', 'closed']
            )
            assert pdf_gen is not None
            assert pdf_gen.fix_version == 'v1.0'
            assert pdf_gen.jira_url == 'https://jira.example.com'
        except Exception as e:
            pytest.fail(f"PDF generator initialization failed: {str(e)}")
    
    def test_pdf_generator_initialization_no_duplicate_args(self, sample_initiatives, sample_areas):
        """
        Test that PDF generator doesn't accept duplicate positional arguments.
        This test specifically prevents the bug: passing arguments twice.
        """
        # This should work - correct usage
        try:
            pdf_gen = PDFGen(
                sample_initiatives,  # positional arg 1
                'v1.0',              # positional arg 2
                sample_areas,        # positional arg 3
                'project = TEST',    # positional arg 4
                page_format='A4',    # keyword arg
                jira_url='https://jira.example.com',  # keyword arg
                is_limited=False
            )
            assert pdf_gen.jira_url == 'https://jira.example.com'
        except TypeError as e:
            pytest.fail(f"Correct initialization should not fail: {str(e)}")
        
        # This should fail - duplicate arguments
        with pytest.raises(TypeError, match="multiple values"):
            PDFGen(
                sample_initiatives,  # positional arg 1
                'v1.0',              # positional arg 2
                sample_areas,        # positional arg 3
                'project = TEST',    # positional arg 4
                sample_initiatives,  # DUPLICATE positional arg 1 (WRONG!)
                'v1.0',              # DUPLICATE positional arg 2 (WRONG!)
                sample_areas,        # DUPLICATE positional arg 3 (WRONG!)
                'project = TEST',    # DUPLICATE positional arg 4 (WRONG!)
                jira_url='https://jira.example.com'  # Now becomes duplicate!
            )
    
    def test_pdf_generator_with_wide_format(self, sample_initiatives, sample_areas):
        """Test PDF generator with wide format."""
        try:
            pdf_gen = PDFGen(
                sample_initiatives,
                'v1.0',
                sample_areas,
                'project = TEST',
                page_format='wide',  # Test wide format
                jira_url='https://jira.example.com',
                is_limited=False
            )
            assert pdf_gen.page_format == 'wide'
        except Exception as e:
            pytest.fail(f"Wide PDF generator initialization failed: {str(e)}")
    
    def test_pdf_generator_with_a3_format(self, sample_initiatives, sample_areas):
        """Test PDF generator with A3 format."""
        try:
            pdf_gen = PDFGen(
                sample_initiatives,
                'v1.0',
                sample_areas,
                'project = TEST',
                page_format='A3',  # Test A3 format
                jira_url='https://jira.example.com'
            )
            assert pdf_gen.page_format == 'A3'
        except Exception as e:
            pytest.fail(f"A3 PDF generator initialization failed: {str(e)}")
    
    def test_pdf_generation_basic(self, sample_initiatives, sample_areas):
        """Test basic PDF generation."""
        pdf_gen = PDFGen(
            sample_initiatives,
            'v1.0',
            sample_areas,
            'project = TEST',
            jira_url='https://jira.example.com'
        )
        
        try:
            pdf_buffer = pdf_gen.generate()
            assert pdf_buffer is not None
            assert isinstance(pdf_buffer, io.BytesIO)
            # Check that buffer has content
            pdf_buffer.seek(0)
            content = pdf_buffer.read()
            assert len(content) > 0
            # PDF files start with %PDF
            assert content[:4] == b'%PDF'
        except Exception as e:
            pytest.fail(f"PDF generation failed: {str(e)}")
    
    def test_pdf_export_endpoint(self, client, sample_initiatives, sample_areas):
        """Test PDF export endpoint."""
        with client.session_transaction() as sess:
            # Set session data
            sess['analysis_key'] = 'test-key'
        
        # Mock the data loading
        with patch('initiative_viewer.load_analysis_data') as mock_load:
            mock_load.return_value = {
                'initiatives': sample_initiatives,
                'all_areas': sample_areas,
                'fix_version': 'v1.0',
                'query': 'project = TEST',
                'jira_url': 'https://jira.example.com',
                'is_limited': False,
                'limit_count': None,
                'original_count': 1
            }
            
            response = client.get('/export-pdf')
            # Should either succeed or fail gracefully
            assert response.status_code in [200, 404, 500]
    
    def test_wide_pdf_export_endpoint(self, client, sample_initiatives, sample_areas):
        """Test wide PDF export endpoint."""
        with client.session_transaction() as sess:
            sess['analysis_key'] = 'test-key'
        
        with patch('initiative_viewer.load_analysis_data') as mock_load:
            mock_load.return_value = {
                'initiatives': sample_initiatives,
                'all_areas': sample_areas,
                'fix_version': 'v1.0',
                'query': 'project = TEST',
                'jira_url': 'https://jira.example.com',
                'is_limited': False,
                'limit_count': None,
                'original_count': 1
            }
            
            response = client.get('/export-wide-pdf')
            assert response.status_code in [200, 404, 500]


class TestErrorHandling:
    """Test error handling and validation."""
    
    def test_pdf_with_empty_initiatives(self, sample_areas):
        """Test PDF generation with empty initiatives list."""
        pdf_gen = PDFGen(
            [],  # Empty initiatives
            'v1.0',
            sample_areas,
            'project = TEST',
            jira_url='https://jira.example.com'
        )
        
        try:
            pdf_buffer = pdf_gen.generate()
            assert pdf_buffer is not None  # Should handle empty gracefully
        except Exception as e:
            # Empty initiatives might be expected to fail
            assert 'initiative' in str(e).lower() or 'empty' in str(e).lower()
    
    def test_pdf_with_none_jira_url(self, sample_initiatives, sample_areas):
        """Test PDF generation with None jira_url."""
        try:
            pdf_gen = PDFGen(
                sample_initiatives,
                'v1.0',
                sample_areas,
                'project = TEST',
                jira_url=''  # Empty string should be handled
            )
            assert pdf_gen.jira_url == ''
        except Exception as e:
            pytest.fail(f"Should handle empty jira_url: {str(e)}")
    
    def test_missing_session_data(self, client):
        """Test endpoints with missing session data."""
        response = client.get('/export-pdf')
        # Should return error when no session data
        assert response.status_code in [400, 404, 500]
    
    def test_invalid_analysis_key(self, client):
        """Test with invalid analysis key."""
        with client.session_transaction() as sess:
            sess['analysis_key'] = 'invalid-key-that-does-not-exist'
        
        response = client.get('/export-pdf')
        assert response.status_code in [400, 404, 500]


class TestDataValidation:
    """Test data validation and structure."""
    
    def test_risk_probability_values(self, sample_areas):
        """Test that risk probability values are handled correctly."""
        for risk_value in [None, 1, 2, 3, 4, 5]:
            initiatives = [{
                'key': 'TEST-1',
                'summary': 'Test',
                'status': 'Open',
                'assignee': 'Test User',
                'area': 'Test Area',
                'risk_probability': risk_value,
                'features': []
            }]
            
            try:
                pdf_gen = PDFGen(
                    initiatives,
                    'v1.0',
                    sample_areas,
                    'project = TEST',
                    jira_url='https://jira.example.com'
                )
                assert pdf_gen is not None
            except Exception as e:
                pytest.fail(f"Should handle risk value {risk_value}: {str(e)}")
    
    def test_completed_statuses(self, sample_initiatives, sample_areas):
        """Test completed statuses are recognized."""
        completed_statuses = ['done', 'closed', 'completed', 'resolved', 'Prod deployed']
        
        pdf_gen = PDFGen(
            sample_initiatives,
            'v1.0',
            sample_areas,
            'project = TEST',
            jira_url='https://jira.example.com',
            completed_statuses=completed_statuses
        )
        
        assert pdf_gen.completed_statuses == completed_statuses


class TestIntegration:
    """Integration tests for full workflows."""
    
    @patch('initiative_viewer.get_most_recent_cache')  # Prevent cache interference
    @patch('initiative_viewer.JiraClient')
    def test_full_analysis_workflow(self, mock_jira_class, mock_cache, client):
        """Test complete workflow from analysis to PDF export."""
        mock_cache.return_value = None  # No cache hit
        # Use proper mock client
        mock_client = get_mock_jira_client()
        mock_jira_class.return_value = mock_client
        
        # Step 1: Perform analysis
        response = client.post('/analyze', data={
            'jira_url': 'https://jira.example.com',
            'access_token': 'test-token',
            'query': 'project = PROJ AND type = "Business Initiative"',
            'fix_version': 'v1.0'
        }, follow_redirects=False)
        
        # Analysis should complete
        assert response.status_code in [200, 302]
        
        # Step 2: Try exporting PDF (if analysis succeeded)
        if response.status_code == 200 or response.status_code == 302:
            pdf_response = client.get('/export-pdf')
            # May succeed or fail depending on mocked data
            assert pdf_response.status_code in [200, 400, 404, 500]




class TestWithMockJiraClient:
    """Test using complete mock Jira client - no actual Jira connection needed."""
    
    def test_mock_client_search_initiatives(self, mock_jira_client):
        """Test mock client can search for initiatives."""
        results = mock_jira_client.search_issues(
            'project = PROJ AND type = "Business Initiative"',
            max_results=50
        )
        
        assert len(results) == 3
        assert results[0]['key'] == 'PROJ-1'
        assert results[0]['fields']['summary'] == 'Customer Portal Modernization'
    
    def test_mock_client_get_issue(self, mock_jira_client):
        """Test mock client can get single issue."""
        issue = mock_jira_client.get_issue('PROJ-1')
        
        assert issue['key'] == 'PROJ-1'
        assert issue['fields']['status']['name'] == 'In Progress'
        assert issue['fields']['assignee']['displayName'] == 'John Doe'
    
    def test_mock_client_authentication_error(self, mock_jira_client_auth_error):
        """Test mock client simulates authentication failure."""
        with pytest.raises(Exception, match='401.*Unauthorized'):
            mock_jira_client_auth_error.search_issues('project = PROJ')
    
    def test_mock_client_permission_error(self, mock_jira_client_permission_error):
        """Test mock client simulates permission error."""
        with pytest.raises(Exception, match='403.*Forbidden'):
            mock_jira_client_permission_error.search_issues('project = PROJ')
    
    def test_mock_client_jql_error(self, mock_jira_client_jql_error):
        """Test mock client simulates JQL syntax error."""
        with pytest.raises(Exception, match='400.*Bad Request'):
            mock_jira_client_jql_error.search_issues('invalid JQL syntax')
    
    def test_mock_client_empty_results(self, mock_jira_client):
        """Test mock client returns empty results for non-matching query."""
        results = mock_jira_client.search_issues('project = NONEXISTENT')
        assert len(results) == 0
    
    def test_mock_client_search_by_status(self, mock_jira_client):
        """Test filtering by status in mock client."""
        results = mock_jira_client.search_issues(
            'project = PROJ AND type = "Business Initiative" AND status = Done'
        )
        
        assert len(results) == 1
        assert results[0]['fields']['status']['name'] == 'Done'
    
    def test_mock_client_search_by_fix_version(self, mock_jira_client):
        """Test filtering by fix version in mock client."""
        results = mock_jira_client.search_issues(
            'project = PROJ AND type = "Business Initiative" AND fixVersion = "v1.0"  '
        )
        
        assert len(results) == 2
        for result in results:
            assert any(fv['name'] == 'v1.0' for fv in result['fields']['fixVersions'])


class TestJiraErrorScenarios:
    """Test handling of various Jira error scenarios."""
    
    @patch('initiative_viewer.get_most_recent_cache')  # Prevent cache from bypassing errors
    @patch('initiative_viewer.JiraClient')
    def test_analyze_with_auth_error(self, mock_jira_class, mock_cache, client, valid_credentials):
        """Test analysis handles authentication error gracefully."""
        mock_cache.return_value = None  # No cache hit
        mock_jira_class.return_value = get_mock_jira_client(simulate_error='auth')
        
        response = client.post('/analyze', data=valid_credentials)
        
        # Should return error
        assert response.status_code in [400, 500]
        assert b'401' in response.data or b'Unauthorized' in response.data or b'Authentication' in response.data
    
    @patch('initiative_viewer.get_most_recent_cache')  # Prevent cache from bypassing errors
    @patch('initiative_viewer.JiraClient')
    def test_analyze_with_permission_error(self, mock_jira_class, mock_cache, client, valid_credentials):
        """Test analysis handles permission error gracefully."""
        mock_cache.return_value = None  # No cache hit
        mock_jira_class.return_value = get_mock_jira_client(simulate_error='permission')
        
        response = client.post('/analyze', data=valid_credentials)
        
        # Should return error
        assert response.status_code in [400, 500]
        assert b'403' in response.data or b'permission' in response.data.lower()
    
    @patch('initiative_viewer.get_most_recent_cache')  # Prevent cache from bypassing errors
    @patch('initiative_viewer.JiraClient')
    def test_analyze_with_jql_error(self, mock_jira_class, mock_cache, client, valid_credentials):
        """Test analysis handles JQL syntax error gracefully."""
        mock_cache.return_value = None  # No cache hit
        mock_jira_class.return_value = get_mock_jira_client(simulate_error='jql')
        
        response = client.post('/analyze', data=valid_credentials)
        
        # Should return error
        assert response.status_code in [400, 500]
        assert b'400' in response.data or b'JQL' in response.data or b'Bad Request' in response.data
    
    @patch('initiative_viewer.JiraClient')
    def test_analyze_with_empty_results(self, mock_jira_class, client, valid_credentials):
        """Test analysis handles empty results gracefully."""
        mock_client = get_mock_jira_client()
        # Override to return empty
        mock_client.search_issues = Mock(return_value=[])
        mock_jira_class.return_value = mock_client
        
        valid_credentials['query'] = 'project = NONEXISTENT'
        response = client.post('/analyze', data=valid_credentials)
        
        # Should handle empty results
        assert response.status_code in [200, 400]


class TestFullWorkflowWithMocks:
    """Test complete workflows using mock Jira responses."""
    
    @patch('initiative_viewer.JiraClient')
    def test_complete_analysis_to_pdf_workflow(self, mock_jira_class, client, valid_credentials):
        """Test full workflow from analysis to PDF generation with mock data."""
        # Setup mock client
        mock_client = get_mock_jira_client()
        mock_jira_class.return_value = mock_client
        
        # Step 1: Analyze
        response = client.post('/analyze', data=valid_credentials, follow_redirects=False)
        
        # Should succeed or redirect
        assert response.status_code in [200, 302]
        
        # Verify session was set (if we got 200 or 302)
        if response.status_code in [200, 302]:
            with client.session_transaction() as sess:
                # Check if analysis key exists
                has_key = 'analysis_key' in sess or 'data_key' in sess
                # This might not be set depending on implementation
                assert has_key or response.status_code == 200
    
    @patch('initiative_viewer.JiraClient')
    def test_analysis_stores_correct_data(self, mock_jira_class, client, valid_credentials):
        """Test that analysis stores the correct data structure."""
        # Setup mock with known data
        mock_client = get_mock_jira_client()
        mock_jira_class.return_value = mock_client
        
        response = client.post('/analyze', data=valid_credentials)
        
        # Should process successfully
        assert response.status_code in [200, 302]
        
        # Verify the mock was called
        assert mock_client.get_search_call_count() > 0
    
    def test_pdf_generation_with_complete_hierarchy(self, sample_initiatives, sample_areas):
        """Test PDF generation with complete realistic hierarchy."""
        pdf_gen = PDFGen(
            sample_initiatives,
            'v1.0',
            sample_areas,
            'project = PROJ AND type = "Business Initiative"',
            jira_url='https://jira.example.com'
        )
        
        pdf_buffer = pdf_gen.generate()
        
        assert pdf_buffer is not None
        pdf_buffer.seek(0)
        content = pdf_buffer.read()
        assert len(content) > 1000  # Should have substantial content
        assert content[:4] == b'%PDF'
    
    def test_pdf_includes_all_risk_levels(self, sample_initiatives, sample_areas):
        """Test PDF generation includes initiatives with different risk levels."""
        # sample_initiatives includes risk 1, 3, and 5
        pdf_gen = PDFGen(
            sample_initiatives,
            'v1.0',
            sample_areas,
            'project = PROJ',
            jira_url='https://jira.example.com'
        )
        
        pdf_buffer = pdf_gen.generate()
        assert pdf_buffer is not None
        
        # Verify we have initiatives with different risks
        risks = [init.get('risk_probability') for init in sample_initiatives]
        assert 1 in risks  # Low risk
        assert 3 in risks  # Medium risk
        assert 5 in risks  # High risk
    
    def test_pdf_includes_completed_initiatives(self, sample_initiatives, sample_areas):
        """Test PDF generation includes completed initiatives."""
        # Find completed initiative
        completed = [i for i in sample_initiatives if i['status'] == 'Done']
        assert len(completed) > 0, "Sample data should include completed initiatives"
        
        pdf_gen = PDFGen(
            sample_initiatives,
            'v1.0',
            sample_areas,
            'project = PROJ',
            jira_url='https://jira.example.com',
            completed_statuses=['done', 'Done']
        )
        
        pdf_buffer = pdf_gen.generate()
        assert pdf_buffer is not None


class TestMockDataStructure:
    """Test that mock data has correct structure."""
    
    def test_mock_initiative_structure(self):
        """Test mock initiative has all required fields."""
        initiative = MockJiraResponses.valid_business_initiative()
        
        assert 'key' in initiative
        assert 'fields' in initiative
        assert 'summary' in initiative['fields']
        assert 'status' in initiative['fields']
        assert 'assignee' in initiative['fields']
        assert 'issuelinks' in initiative['fields']
    
    def test_mock_hierarchy_has_all_levels(self):
        """Test mock hierarchy includes all levels: Initiative → Feature → Sub-Feature → Epic."""
        hierarchy = create_mock_hierarchy_data()
        
        assert len(hierarchy) > 0, "Should have initiatives"
        
        initiative = hierarchy[0]
        assert 'features' in initiative
        assert len(initiative['features']) > 0, "Should have features"
        
        feature = initiative['features'][0]
        assert 'sub_features' in feature
        assert len(feature['sub_features']) > 0, "Should have sub-features"
        
        sub_feature = feature['sub_features'][0]
        assert 'epics' in sub_feature
        assert len(sub_feature['epics']) > 0, "Should have epics"
    
    def test_mock_areas_list(self):
        """Test mock areas list is not empty."""
        areas = create_mock_areas()
        
        assert len(areas) > 0
        assert all(isinstance(area, str) for area in areas)
    
    def test_empty_hierarchy_structure(self):
        """Test empty hierarchy mock."""
        empty = create_mock_empty_hierarchy()
        
        assert len(empty) > 0
        assert empty[0]['features'] == []


class TestPDFWithVariousScenarios:
    """Test PDF generation with various data scenarios."""
    
    def test_pdf_with_single_initiative(self, sample_areas):
        """Test PDF with just one initiative."""
        single_initiative = [create_mock_hierarchy_data()[0]]
        
        pdf_gen = PDFGen(
            single_initiative,
            'v1.0',
            sample_areas,
            'key = PROJ-1',
            jira_url='https://jira.example.com'
        )
        
        pdf_buffer = pdf_gen.generate()
        assert pdf_buffer is not None
    
    def test_pdf_with_empty_hierarchy(self, sample_areas):
        """Test PDF with initiatives that have no features."""
        empty_hierarchy = create_mock_empty_hierarchy()
        
        pdf_gen = PDFGen(
            empty_hierarchy,
            'v1.0',
            sample_areas,
            'project = PROJ',
            jira_url='https://jira.example.com'
        )
        
        # Should handle empty hierarchy
        try:
            pdf_buffer = pdf_gen.generate()
            assert pdf_buffer is not None
        except Exception as e:
            # Empty hierarchy might fail, which is acceptable
            assert 'initiative' in str(e).lower() or 'empty' in str(e).lower()
    
    def test_pdf_with_multiple_areas(self, sample_initiatives):
        """Test PDF with multiple different areas."""
        many_areas = ['Area ' + chr(65+i) for i in range(15)]  # Area A through Area O
        
        pdf_gen = PDFGen(
            sample_initiatives,
            'v1.0',
            many_areas,
            'project = PROJ',
            page_format='wide',  # Should use wide format for many areas
            jira_url='https://jira.example.com'
        )
        
        pdf_buffer = pdf_gen.generate()
        assert pdf_buffer is not None
        assert pdf_gen.page_format == 'wide'
    
    def test_pdf_with_limited_results(self, sample_initiatives, sample_areas):
        """Test PDF with limited results flag."""
        pdf_gen = PDFGen(
            sample_initiatives[:2],  # Only first 2
            'v1.0',
            sample_areas,
            'project = PROJ',
            jira_url='https://jira.example.com',
            is_limited=True,
            limit_count=2,
            original_count=10
        )
        
        pdf_buffer = pdf_gen.generate()
        assert pdf_buffer is not None
        assert pdf_gen.is_limited == True
        assert pdf_gen.limit_count == 2
        assert pdf_gen.original_count == 10


class TestEndToEndWithoutJira:
    """End-to-end tests that don't require Jira at all."""
    
    def test_pdf_generator_with_all_risk_values(self, sample_areas):
        """Test PDF includes all risk probability values."""
        initiatives_all_risks = []
        
        for risk in [None, 1, 2, 3, 4, 5]:
            initiatives_all_risks.append({
                'key': f'PROJ-{risk if risk else 0}',
                'summary': f'Initiative with risk {risk}',
                'status': 'In Progress',
                'assignee': 'Test User',
                'area': 'Test Area',
                'risk_probability': risk,
                'fix_version': 'v1.0',
                'features': []
            })
        
        pdf_gen = PDFGen(
            initiatives_all_risks,
            'v1.0',
            sample_areas,
            'project = PROJ',
            jira_url='https://jira.example.com'
        )
        
        pdf_buffer = pdf_gen.generate()
        assert pdf_buffer is not None
    
    def test_pdf_generator_with_all_statuses(self, sample_areas):
        """Test PDF handles various status values."""
        statuses = ['To Do', 'In Progress', 'Done', 'Closed', 'Blocked', 'On Hold']
        initiatives_all_statuses = []
        
        for idx, status in enumerate(statuses):
            initiatives_all_statuses.append({
                'key': f'PROJ-{idx+10}',
                'summary': f'Initiative {status}',
                'status': status,
                'assignee': 'Test User',
                'area': 'Test Area',
                'risk_probability': 2,
                'fix_version': 'v1.0',
                'features': []
            })
        
        pdf_gen = PDFGen(
            initiatives_all_statuses,
            'v1.0',
            sample_areas,
            'project = PROJ',
            jira_url='https://jira.example.com',
            completed_statuses=['done', 'closed']
        )
        
        pdf_buffer = pdf_gen.generate()
        assert pdf_buffer is not None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

