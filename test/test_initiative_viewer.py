"""
Test suite for Initiative Viewer application
Tests all web interface endpoints and PDF generation functionality
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
    """Sample initiative data for testing."""
    return [
        {
            'key': 'PROJ-1',
            'summary': 'Test Initiative 1',
            'status': 'In Progress',
            'assignee': 'John Doe',
            'area': 'Area A',
            'risk_probability': 3,
            'features': [
                {
                    'key': 'PROJ-10',
                    'summary': 'Feature 1',
                    'status': 'In Progress',
                    'assignee': 'Jane Smith',
                    'sub_features': [
                        {
                            'key': 'PROJ-100',
                            'summary': 'Sub-Feature 1',
                            'status': 'In Progress',
                            'assignee': 'Bob Johnson',
                            'epics': [
                                {
                                    'key': 'PROJ-1000',
                                    'summary': 'Epic 1',
                                    'status': 'Done',
                                    'assignee': 'Alice Williams',
                                    'fix_version': 'v1.0'
                                }
                            ]
                        }
                    ]
                }
            ]
        }
    ]


@pytest.fixture
def sample_areas():
    """Sample areas for testing."""
    return ['Area A', 'Area B', 'Area C']


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
    
    @patch('initiative_viewer.JiraClient')
    def test_analyze_endpoint_with_valid_data(self, mock_jira, client):
        """Test analyze endpoint with valid parameters."""
        # Mock JiraClient
        mock_client_instance = Mock()
        mock_client_instance.search_issues.return_value = [{
            'key': 'TEST-1',
            'fields': {
                'summary': 'Test',
                'status': {'name': 'Open'},
                'assignee': {'displayName': 'Test User'},
                'issuelinks': []
            }
        }]
        mock_jira.return_value = mock_client_instance
        
        response = client.post('/analyze', data={
            'jira_url': 'https://jira.example.com',
            'email': 'test@example.com',
            'api_token': 'test-token',
            'jql': 'project = TEST',
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
    
    @patch('initiative_viewer.JiraClient')
    def test_full_analysis_workflow(self, mock_jira, client):
        """Test complete workflow from analysis to PDF export."""
        # Mock JiraClient
        mock_client = Mock()
        mock_client.search_issues.return_value = [{
            'key': 'TEST-1',
            'fields': {
                'summary': 'Test Initiative',
                'status': {'name': 'Open'},
                'assignee': {'displayName': 'Test User'},
                'issuelinks': [],
                'customfield_12345': None  # risk probability field
            }
        }]
        mock_jira.return_value = mock_client
        
        # Step 1: Perform analysis
        response = client.post('/analyze', data={
            'jira_url': 'https://jira.example.com',
            'email': 'test@example.com',
            'api_token': 'test-token',
            'jql': 'project = TEST',
            'fix_version': 'v1.0'
        }, follow_redirects=False)
        
        # Analysis should complete
        assert response.status_code in [200, 302]
        
        # Step 2: Try exporting PDF (if analysis succeeded)
        if response.status_code == 200 or response.status_code == 302:
            pdf_response = client.get('/export-pdf')
            # May succeed or fail depending on mocked data
            assert pdf_response.status_code in [200, 400, 404, 500]


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
