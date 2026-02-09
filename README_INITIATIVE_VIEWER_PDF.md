# Initiative Viewer - PDF Export Feature

## Overview
The Initiative Viewer application now includes a modern PDF export feature that generates comprehensive reports with statistics and visualizations.

## Features

### PDF Report Contents

1. **Title Page**
   - Program Increment (PI) / Fix Version
   - Generation date and time
   - High-level statistics cards showing:
     - Total number of Initiatives
     - Total Features
     - Total Sub-Features
     - Total Epics

2. **Statistical Summary Page**
   - **Initiative Completion Statistics Table**
     - Per-initiative breakdown showing:
       - Number of Features
       - Number of Sub-Features
       - Number of Epics
       - Number of Completed Epics
       - Completion Percentage
       - Average Risk Score
     - Overall totals row
   
   - **Epic Status Distribution**
     - Count and percentage of epics by status
     - Shows Done, In Progress, To Do, etc.

3. **Detailed Initiative Pages**
   - Full hierarchy for each initiative:
     - Initiative → Features → Sub-Features → Epics
   - Epic tables organized by area/project
   - Color-coded risk indicators (1-5 scale):
     - 1 (Green) = Low Risk
     - 2 (Light Green) = Low-Medium Risk
     - 3 (Yellow/Orange) = Medium Risk
     - 4 (Orange) = Medium-High Risk
     - 5 (Red) = High Risk
     - Gray = No risk defined

## Usage

### Running the Application

1. **Start the Initiative Viewer**
   ```bash
   python initiative_viewer.py
   ```
   Or use the batch file:
   ```bash
   run_initiative_viewer.bat
   ```

2. **Access the Application**
   - Open browser to `http://localhost:5001`
   - Enter your Jira credentials and query parameters:
     - Jira URL (e.g., `https://your-jira-instance.com`)
     - Access Token
     - JQL Query (e.g., `issuetype = "Business Initiative" AND project = "YourProject"`)
     - Fix Version / PI (e.g., `PI 2024.1`)

3. **View Results**
   - The application displays the hierarchical view of initiatives
   - All initiatives are expandable to show features, sub-features, and epics

4. **Export to PDF**
   - Click the **"📄 Export to PDF"** button in the top-right corner
   - The PDF will be automatically downloaded to your browser's download folder
   - Filename format: `Initiative_Report_{PI}_{timestamp}.pdf`
   - Example: `Initiative_Report_PI2024.1_20260202_143025.pdf`

## PDF Report Statistics

The PDF includes comprehensive statistics:

### Initiative-Level Metrics
- Total count of initiatives analyzed
- Per-initiative completion percentage
- Average risk score per initiative
- Breakdown of features, sub-features, and epics

### Epic-Level Metrics
- Total epic count across all initiatives
- Completed epic count
- Overall completion percentage
- Status distribution (Done, In Progress, To Do, etc.)
- Risk distribution across all epics

### Visual Elements
- Modern color-coded design
- Risk-based color highlighting for epics
- Professional tables with clear headers
- Landscape orientation for better readability
- Multi-page layout with automatic page breaks

## Requirements

The PDF export functionality requires:
- `reportlab==4.0.4` (automatically included in requirements_initiative_viewer.txt)
- Flask session storage for temporary data

## Technical Details

### PDF Generation
- Uses ReportLab library for PDF creation
- Landscape A4 format for optimal table viewing
- Custom styling with modern color scheme
- Automatic calculation of statistics from Jira data
- Session-based data storage for export

### Data Flow
1. User submits analysis request
2. Application fetches data from Jira
3. Data is stored in Flask session
4. User clicks export button
5. PDF generator retrieves data from session
6. PDF is generated in-memory
7. PDF is sent to browser for download

## Troubleshooting

### PDF Export Button Not Visible
- Ensure you've run an analysis first
- Check that the hierarchy page loaded successfully

### "No data available for export" Error
- Run a new analysis before attempting to export
- Ensure your Jira query returned results

### PDF Generation Failed
- Check that reportlab is installed: `pip install reportlab==4.0.4`
- Verify that your browser allows PDF downloads
- Check application logs for detailed error messages

### Empty or Missing Data in PDF
- Verify that your Jira query is correct
- Ensure the Fix Version exists and has associated data
- Check that epics have the required custom fields (risk, status)

## Customization

To customize the PDF output, edit [initiative_viewer_pdf.py](initiative_viewer_pdf.py):

- **Colors**: Modify `RISK_COLORS` dictionary for different risk color schemes
- **Styles**: Adjust `_setup_custom_styles()` method for fonts and colors
- **Layout**: Modify table widths and spacing in respective methods
- **Statistics**: Add new calculations in `_calculate_statistics()` method

## Future Enhancements

Potential improvements:
- Add charts/graphs for visual statistics
- Include trend analysis over multiple PIs
- Add filtering options for PDF export
- Include assignee workload distribution
- Add timeline/Gantt chart views
- Export to Excel/CSV formats

## Support

For issues or questions:
- Check application logs for detailed error messages
- Verify Jira connectivity and permissions
- Ensure all required fields are available in your Jira instance
- Contact: Pietro Maffi

---
**Author**: Pietro Maffi  
**Version**: 1.0  
**Last Updated**: February 2, 2026
