# Backward Check Feature - Documentation

## Overview

The **Backward Check** feature is a new analysis mode in the Initiative Viewer that helps identify features and sub-features that should be marked with a specific Fix Version (PI) based on active development work.

## Problem Statement

Many features and sub-features don't have their Fix Version set correctly. However, if their child epics have stories/tasks in active sprints, this indicates ongoing development work that should be tracked in the current PI.

## How It Works

### Analysis Flow

1. **Start from Query**: Uses the input JQL query to retrieve all initiatives
2. **Find Not-Done Items**: Retrieves all features and sub-features that are NOT DONE (regardless of Fix Version)
3. **Retrieve Epics**: For each not-done sub-feature, fetches all child epics
4. **Check Active Sprints**: For each epic, checks if it has any children (stories/tasks) in ACTIVE sprints
5. **Mark Items**: 
   - Epics with active sprint work are marked **GREEN** (Risk = 1 - Low Risk)
   - Features and sub-features containing these epics are flagged to be marked with the target PI

### Key Differences from Normal Mode

| Feature | Normal Mode | Backward Check Mode |
|---------|-------------|---------------------|
| **Filtering** | Uses Fix Version to filter Features/Sub-features | Ignores Fix Version, finds all NOT DONE items |
| **Epic Risk** | Uses Risk Probability field from Jira | Sets Risk = 1 (GREEN) if epic has active sprint work |
| **Purpose** | Show current PI progress | Find items that SHOULD BE in the PI |
| **Caching** | Supports cached data | Always fetches fresh data |
| **Limits** | Supports initiative limits | No limits (analyzes all) |

## Usage

### 1. Enable Backward Check Mode

On the Initiative Viewer homepage:

1. Check the **"🔍 Backward Check Mode"** checkbox
2. Fill in all required fields:
   - Jira Server URL
   - Access Token
   - Initiative Query (JQL)
   - Fix Version (the target PI to mark items with)
3. Click **"🔍 Run Backward Check"**

> **Note**: When Backward Check is enabled, Cache and Limit options are automatically disabled.

### 2. Review Results

The analysis results page shows:

- **Summary Statistics**:
  - Total Features/Sub-Features analyzed
  - Features/Sub-Features with active work
  - Number of epics in active sprints
  
- **Hierarchical View**: Same as normal mode, but:
  - Only shows NOT DONE features/sub-features
  - Epics with active sprint work are GREEN
  - Features/sub-features are visually flagged if they contain active work

### 3. Export Reports

Four export options are available:

#### A. Export Jira Keys (📋 Export Jira Keys)
**NEW: Backward Check Only**

Generates a text file containing:
- Summary statistics
- List of all Features to mark with the PI
- List of all Sub-Features to mark with the PI
- **Bulk update JQL queries** ready to use in Jira
- Instructions for updating Fix Versions

**Example Output**:
```
================================================================================
BACKWARD CHECK ANALYSIS - JIRA KEYS TO MARK
================================================================================
Target Fix Version: PI 2025.1
Generated: 2026-02-11 10:30:00

SUMMARY
--------------------------------------------------------------------------------
Total Features Analyzed: 45
Features with Active Work: 12
Total Sub-Features Analyzed: 156
Sub-Features with Active Work: 34
Epics in Active Sprints: 67

================================================================================
FEATURES TO MARK WITH PI 2025.1
================================================================================
1. ISDOP-1234 - Payment Gateway Integration
2. ISDOP-1235 - User Authentication Module
...

================================================================================
BULK UPDATE JQL QUERIES
================================================================================
Use these JQL queries to bulk-update items in Jira:

Features:
  issuekey in (ISDOP-1234, ISDOP-1235, ISDOP-1236)

Sub-Features:
  issuekey in (ISDOP-2001, ISDOP-2002, ISDOP-2003)

All Items Combined:
  issuekey in (ISDOP-1234, ISDOP-1235, ISDOP-2001, ISDOP-2002)
```

#### B. Export to PDF (📄 Export to PDF)
Standard A4 format PDF report with backward check results.

#### C. Wide PDF (📄 Wide PDF)
A3/Wide format PDF for viewing all areas at once.

#### D. Export to HTML (📄 Export to HTML)
Confluence-compatible HTML export.

## Updating Jira

### Method 1: Bulk Update via JQL (Recommended)

1. Export the Jira Keys report (📋 button)
2. Open the exported text file
3. Copy the JQL query from the "BULK UPDATE JQL QUERIES" section
4. In Jira:
   - Go to Issues → Search for Issues
   - Paste the JQL query
   - Click "Tools" (⚙️) → "Bulk Change"
   - Select all issues
   - Choose "Edit Issues" → "Change Fix Version"
   - Select your target PI (e.g., "PI 2025.1")
   - Confirm changes

### Method 2: Manual Update

1. Review the exported Jira Keys report
2. Manually update each Feature/Sub-Feature in Jira
3. Set the Fix Version field to the target PI

## Technical Implementation

### New Files Created

1. **backward_check_analyzer.py**: 
   - `BackwardCheckAnalyzer` class
   - Handles the backward check logic
   - Queries Jira for not-done items
   - Checks sprint status of epic children

### Modified Files

1. **initiative_viewer.py**:
   - Added `analyze_backward_check()` function
   - Added `/export_jira_keys` route
   - Modified `/analyze` to route to backward check when enabled

2. **templates/initiative_form.html**:
   - Added backward check checkbox
   - Added JavaScript to disable cache/limit when backward check is enabled

3. **templates/initiative_hierarchy.html**:
   - Added backward check summary section
   - Added Export Jira Keys button (conditional)
   - Updated header to show backward check mode

## Important Notes

### Sprint Status Detection

The analyzer checks for **ACTIVE** sprints only. A sprint is considered active when:
- Sprint state = "ACTIVE" (not CLOSED, not FUTURE)
- The story/task is currently assigned to that sprint

### Status Filtering

Items with the following statuses are excluded (considered DONE):
- Done
- Closed
- Resolved
- Completed
- Prod deployed

### Risk Color Coding

In Backward Check mode:
- **GREEN (Risk = 1)**: Epic has children in active sprints → Should be tracked
- **No Color**: Epic has NO children in active sprints → May be inactive

## Example Use Case

**Scenario**: Planning for PI 2025.2

**Problem**: Many features were started in PI 2025.1 but weren't marked with Fix Version. Teams are actively working on epics, but management has no visibility.

**Solution**:
1. Run Backward Check with:
   - Query: `project = ISDOP AND issuetype = "Business Initiative"`
   - Fix Version: `PI 2025.2`
2. Review the 67 epics found with active sprint work
3. Export the Jira Keys report
4. Use the bulk update JQL to mark 45 features and 156 sub-features with `PI 2025.2`
5. Now the PI dashboard shows accurate progress

## Troubleshooting

### No epics found with active work

**Possible causes**:
- Teams haven't started sprint planning
- Sprint field is not populated correctly
- Items are in CLOSED or FUTURE sprints (not ACTIVE)

### Too many items to mark

**Solution**: Review the exported report carefully. Some items may have minimal active work. Consider:
- Checking the number of epics per feature/sub-feature
- Reviewing with product owners before bulk updating

### Export Jira Keys button not visible

**Cause**: This button only appears in Backward Check mode. Run the analysis with the backward check checkbox enabled.

## Performance Considerations

Backward Check mode:
- Queries ALL not-done features/sub-features (no Fix Version filter)
- Checks sprint status for every epic's children
- May take longer than normal mode for large projects
- Does not support caching or limiting

**Recommendation**: Use more specific JQL queries (e.g., filter by specific projects or teams) to reduce analysis time.

## Future Enhancements

Potential improvements for future versions:
- [ ] Filter by sprint name pattern (e.g., only "2025 Q1" sprints)
- [ ] Confidence scoring (number of active stories per epic)
- [ ] Historical sprint analysis (track trends)
- [ ] Auto-suggest Fix Version based on sprint dates
- [ ] Dry-run mode with impact analysis

---

**Version**: 1.0  
**Author**: Pietro Maffi  
**Date**: February 2026
