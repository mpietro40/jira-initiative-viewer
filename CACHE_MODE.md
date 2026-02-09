# Cache Mode - Quick Reference Guide

## Overview
The Initiative Viewer supports a **smart cache mode** that allows you to reload previous analysis results without fetching from Jira again. Cache is automatically validated against the JQL query to ensure data relevance.

## Two Ways to Enable Cache

### 1. Frontend Checkbox (Recommended) ✅
**No restart needed!** Simply check the "Use Cached Data" checkbox on the form:
- Cache is used only if JQL query matches the cached query
- If query changes, a fresh scan is automatically performed
- Dynamic button text shows "Load from Cache" when checked
- Visual feedback with cache age indicator in results

### 2. Command-Line Flag (Advanced)
```bash
python initiative_viewer.py --cached
```
Always attempts to use cache regardless of form checkbox (useful for development)

## Smart Query Matching

The cache system automatically validates the JQL query:

**Cache HIT** ✅ (Uses cached data):
- Checkbox is checked
- JQL query exactly matches cached query
- Results load instantly from disk

**Cache MISS** ❌ (Fresh Jira scan):
- Checkbox is checked BUT query is different
- System automatically fetches fresh data
- New cache is created with updated query

### Example Flow:
```
First run: "project = ISDOP ORDER BY Rank"
  → Fresh scan, results cached

Second run (cache checked): "project = ISDOP ORDER BY Rank"  
  → Cache HIT ✅ Instant load

Third run (cache checked): "project = NEWPROJ ORDER BY Rank"
  → Cache MISS ❌ Fresh scan (query changed)
```

## Benefits

✅ **No Restart Required**: Toggle cache mode in the UI, not the command line
✅ **Smart Validation**: Automatic fresh scan when query changes
✅ **Faster Development**: Instant reload for same query
✅ **Visual Feedback**: Button changes to "Load from Cache" when enabled
✅ **Cache Age Display**: See how old the cached data is
✅ **Offline Work**: Review previous results without Jira connection

1. **Data Storage**: Every analysis is saved to a temporary file in your system's temp directory
2. **Cache Duration**: Files are automatically cleaned up after 1 hour
3. **Cache Indicator**: When viewing cached data, you'll see a badge showing "Cached Data (loaded X minutes ago)"
4. **PDF Export**: Works seamlessly with both cached and fresh data

## Technical Details

- **Storage Location**: `%TEMP%\initiative_viewer_data\` (Windows) or `/tmp/initiative_viewer_data/` (Linux/Mac)
- **Format**: Pickle files with UUID names (e.g., `a1b2c3d4-e5f6-7890.pkl`)
- **Cleanup**: Automatic removal of files older than 1 hour on each new analysis
- **Session Persistence**: Uses file-based storage instead of session cookies (no 4KB limit)

## Console Output

When cache is checked in UI:
```
🔄 CACHE MODE: Checking for cached data...
📦 Found cached data from 2026-02-02 15:04:22
```

**Cache HIT** (query matches):
```
✅ Cache HIT: Query matches! Loaded 5 initiatives (age: 3 minutes)
```

**Cache MISS** (query changed):
```
⚠️ Cache MISS: Query changed!
   Cached query: project = ISDOP ORDER BY Rank...
   Current query: project = NEWPROJ ORDER BY Rank...
   → Fetching fresh data from Jira
```

## UI Features

### Form Page:
- 🔄 Checkbox: "Use Cached Data (if available)"
- Hint text: "Load most recent analysis instead of fetching from Jira. Cache is used only if JQL query matches."
- Dynamic button: Changes from "🚀 Analyze Initiatives" to "📂 Load from Cache"
- Visual highlight: Checkbox area turns teal when checked

### Results Page:
- Cache badge shows: "Cached Data (loaded 3 minutes ago)"
- Only appears when data was loaded from cache

## Technical Details

## Technical Details

- **Storage Location**: `%TEMP%\initiative_viewer_data\` (Windows) or `/tmp/initiative_viewer_data/` (Linux/Mac)
- **Format**: Pickle files with UUID names (e.g., `a1b2c3d4-e5f6-7890.pkl`)
- **Cleanup**: Automatic removal of files older than 1 hour on each new analysis
- **Query Comparison**: Exact string match (whitespace-insensitive) between current and cached JQL
- **Session Independence**: Cache persists across browser sessions and app restarts
- **No Size Limit**: Files stored on disk, not in session cookies (no 4KB limit)

## Notes

- Cache is machine-specific (not shared across users or machines)
- Query must match exactly for cache hit
- Form fields (URL, token, fix version) are ignored when using cache
- PDF export works identically with cached or fresh data
- Command-line `--cached` flag overrides form checkbox (always attempts cache)
