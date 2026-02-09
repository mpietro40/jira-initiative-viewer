# 🎯 Initiative Viewer - Hierarchical Jira Analysis

A Flask web application for visualizing Jira hierarchies with expandable initiatives, features, sub-features, and epics organized by area with risk-based color coding.

## 📋 Features

- **Hierarchical View**: Business Initiative → Feature → Sub-Feature → Epic
- **Fix Version Filtering**: Filter features and sub-features by specific fix version
- **Area Organization**: Epics grouped by project/area in table format
- **Risk Color Coding**: Visual distinction by Risk Probability levels:
  - 🟢 Low (Green)
  - 🟡 Medium (Orange)
  - 🔴 High (Red)
  - ⚫ Critical (Dark Red)
  - ⚪ None/Unknown (Gray)
- **Expandable Interface**: Click to expand/collapse initiatives and features
- **Responsive Design**: Modern, clean UI with gradient styling

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements_initiative_viewer.txt
```

### 2. Run the Application

```bash
python initiative_viewer.py
```

The application will start on `http://localhost:5001`

### 3. Configure Analysis

Open your browser and navigate to `http://localhost:5001`

Fill in the form:
- **Jira Server URL**: Your Jira instance (e.g., `https://yourcompany.atlassian.net`)
- **Access Token**: Your Jira API token (generate from Account Settings → Security → API Tokens)
- **Initiative Query**: JQL to filter initiatives (e.g., `project = ISDOP`)
- **Fix Version**: The fix version to filter features/sub-features (e.g., `PI 2025.1`)

### 4. View Results

Click "Analyze Initiatives" to see the hierarchical view with:
- Ordered list of initiatives with assignees
- Expandable features showing sub-features
- Epics organized by area/project
- Color-coded risk levels
- Status and assignee information

## 🎨 Risk Probability Mapping

The application automatically color-codes epics based on the `Risk Probability` custom field:

| Risk Level | Color | Background |
|------------|-------|------------|
| None/Unknown | Gray | `#f0f0f0` |
| Low | Green | `#c6f6d5` |
| Medium | Orange | `#feebc8` |
| High | Red | `#fed7d7` |
| Critical | Dark Red | `#fbb6ce` |

## 📊 Hierarchy Structure

```
Business Initiative (ISDOP-XXX)
├── Feature (filtered by fixVersion)
│   ├── Sub-Feature (filtered by fixVersion)
│   │   └── Epics by Area
│   │       ├── Area 1 (Project A)
│   │       │   ├── Epic 1
│   │       │   └── Epic 2
│   │       ├── Area 2 (Project B)
│   │       │   └── Epic 3
│   │       └── Area 3 (Project C)
│   │           └── Epic 4
```

## ⚙️ Configuration

### Custom Field Mapping

If your Jira instance uses different custom field IDs for Risk Probability, update line 126 in `initiative_viewer.py`:

```python
# Change this to match your custom field ID
risk_probability = fields.get('customfield_10100') or fields.get('customfield_11200')
```

To find your custom field ID:
1. Open a Jira issue in your browser
2. Add `?expand=names` to the URL
3. Search for "Risk Probability" in the JSON response

### Port Configuration

To change the port (default 5001), modify the last line in `initiative_viewer.py`:

```python
app.run(debug=True, host='0.0.0.0', port=5001)  # Change port here
```

## 🔧 Troubleshooting

### "All fields are required" Error
Ensure all form fields are filled in, especially the access token.

### "Analysis failed" Error
- Verify your Jira URL is correct (no trailing slash)
- Check that your access token is valid
- Ensure your JQL query is syntactically correct
- Verify the fix version name matches exactly (case-sensitive)

### No Epics Showing
- Verify the parent/child relationships in Jira
- Check that epics are properly linked to sub-features
- Ensure the fix version is set on features/sub-features

### Wrong Risk Colors
- Update the custom field ID in the code (see Configuration section)
- Check that Risk Probability field values match: "Low", "Medium", "High", "Critical"

## 📁 Project Structure

```
PerseusLeadTime/
├── initiative_viewer.py          # Main Flask application
├── jira_client.py                # Existing Jira client (reused)
├── requirements_initiative_viewer.txt
├── README_INITIATIVE_VIEWER.md
└── templates/
    ├── initiative_form.html      # Input form
    └── initiative_hierarchy.html # Hierarchical view
```

## 🔐 Security Notes

- Access tokens are not stored; they're only used during the session
- Use HTTPS in production
- Consider implementing authentication for production use
- Never commit access tokens to version control

## 📝 Usage Example

1. **Input Form**:
   ```
   Jira URL: https://mycompany.atlassian.net
   Access Token: [your-token]
   Query: project = ISDOP AND labels = "Strategic"
   Fix Version: PI 2025.1
   ```

2. **Result**: Expandable view showing all ISDOP Strategic initiatives with their features (PI 2025.1), sub-features, and epics organized by area with risk-based colors.

## 🤝 Integration with PI Analyzer

This application reuses the `jira_client.py` from the PI Analyzer, ensuring consistent Jira connectivity and authentication.

## 📄 License

Created by Pietro Maffi - Initiative Viewer Tool

---

**Need Help?** Check the console output for detailed logging of the data fetching process.
