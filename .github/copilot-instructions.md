<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# Copilot Instructions for Nimble Streamer Log Analyzer

This is a Python project for analyzing large log files (100+ MB) from Nimble Streamer and generating comprehensive reports.

## Project Context
- **Purpose**: Analyze Nimble Streamer log files and create detailed reports
- **Target Log Size**: 130 MB+ files
- **Output**: CSV reports, Excel files, and visualizations

## Code Guidelines
- Use pandas for efficient data processing with chunking for large files
- Implement memory-efficient file reading techniques
- Create clear, structured reports with statistics and visualizations
- Handle various log formats (Apache, Nginx, IIS, custom formats)
- Use tqdm for progress tracking on large files
- Generate both programmatic (CSV/Excel) and visual (PNG/charts) outputs

## Key Features to Maintain
- Chunk-based file reading for memory efficiency
- Multiple log format support with regex parsing
- Comprehensive error handling for malformed log entries
- Time-based analysis (hourly, daily patterns)
- IP address and status code analysis
- Export capabilities to multiple formats
- Visualization generation with matplotlib/plotly

## Performance Considerations
- Always use chunked reading for files over 100MB
- Implement progress indicators for long-running operations
- Optimize pandas operations for large datasets
- Handle encoding issues gracefully

When suggesting improvements or new features, prioritize:
1. Memory efficiency for large files
2. Processing speed optimization
3. Report accuracy and completeness
4. User-friendly output formats
