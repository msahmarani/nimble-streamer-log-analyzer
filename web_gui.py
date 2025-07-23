"""
Web GUI for Nimble Streamer Log Analyzer
A Dash-based web interface for analyzing log files and viewing reports.
"""

# Fix matplotlib backend issues on Windows
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend

import dash
from dash import dcc, html, Input, Output, State, dash_table, callback
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import os
import base64
import io
from datetime import datetime
import json
from typing import Any, Dict, List, Optional, Union
from log_analyzer import NimbleLogAnalyzer
from json_log_analyzer import JSONNimbleLogAnalyzer
from enhanced_ipinfo_service import enhanced_ipinfo_service, set_enhanced_ipinfo_token

# Initialize Dash app
app = dash.Dash(__name__, title="Nimble Streamer Log Analyzer")

# Global variables to store analysis results
current_analyzer = None
current_data = None

# App layout
app.layout = html.Div([
    # Header
    html.Div([
        html.H1("🚀 Nimble Streamer Log Analyzer", 
                style={'textAlign': 'center', 'color': '#2c3e50', 'marginBottom': '10px'}),
        html.P("Upload and analyze large log files with interactive visualizations", 
               style={'textAlign': 'center', 'color': '#7f8c8d', 'fontSize': '18px'})
    ], style={'padding': '20px', 'backgroundColor': '#ecf0f1', 'marginBottom': '20px'}),
    
    # Upload section
    html.Div([
        html.H3("📁 Upload Log File"),
        dcc.Upload(
            id='upload-data',
            children=html.Div([
                'Drag and Drop or ',
                html.A('Select Files', style={'color': '#3498db', 'textDecoration': 'underline'})
            ]),
            style={
                'width': '100%',
                'height': '60px',
                'lineHeight': '60px',
                'borderWidth': '2px',
                'borderStyle': 'dashed',
                'borderRadius': '10px',
                'textAlign': 'center',
                'margin': '10px 0',
                'backgroundColor': '#f8f9fa',
                'borderColor': '#3498db'
            },
            multiple=False
        ),
        html.Div(id='upload-status', style={'margin': '10px 0'}),
        html.Button('Analyze Log File', id='analyze-button', n_clicks=0,
                    style={'backgroundColor': '#27ae60', 'color': 'white', 'border': 'none',
                           'padding': '10px 20px', 'borderRadius': '5px', 'cursor': 'pointer',
                           'fontSize': '16px', 'marginTop': '10px'}),
        dcc.Loading(id="loading", children=[html.Div(id="loading-output")], type="default"),
    ], style={'padding': '20px', 'backgroundColor': 'white', 'borderRadius': '10px',
              'boxShadow': '0 2px 10px rgba(0,0,0,0.1)', 'marginBottom': '20px'}),
    
    # IPinfo Configuration Section
    html.Div([
        html.H3("🌍 IP Geolocation Configuration"),
        html.Div([
            html.Div([
                html.Label("🔑 IPinfo API Token (Optional):", style={'fontWeight': 'bold'}),
                dcc.Input(
                    id='ipinfo-token',
                    type='password',
                    placeholder='Enter your IPinfo API token for enhanced features',
                    style={'width': '100%', 'padding': '8px', 'borderRadius': '5px', 'border': '1px solid #ddd'}
                ),
                html.P("💡 Get a free token at https://ipinfo.io to enable country and ISP analysis", 
                       style={'color': '#7f8c8d', 'fontSize': '14px', 'margin': '5px 0'})
            ], style={'width': '60%', 'display': 'inline-block', 'margin': '10px'}),
            
            html.Div([
                html.Button('Set Token', id='set-token-button', n_clicks=0,
                           style={'backgroundColor': '#3498db', 'color': 'white', 'border': 'none',
                                  'padding': '10px 20px', 'borderRadius': '5px', 'cursor': 'pointer',
                                  'fontSize': '14px', 'margin': '10px'}),
                dcc.Checklist(
                    id='enable-ipinfo',
                    options=[{'label': ' Enable IP Geolocation Analysis', 'value': 'enabled'}],
                    value=['enabled'],
                    style={'margin': '10px'}
                )
            ], style={'width': '35%', 'display': 'inline-block', 'verticalAlign': 'top'})
        ]),
        html.Div(id='ipinfo-status', style={'margin': '10px 0'})
    ], style={'padding': '20px', 'backgroundColor': 'white', 'borderRadius': '10px',
              'boxShadow': '0 2px 10px rgba(0,0,0,0.1)', 'marginBottom': '20px'}),
    
    # Advanced Filters Section
    html.Div([
        html.H3("🎛️ Advanced Filters & Controls"),
        html.Div([
            # Date Range Picker
            html.Div([
                html.Label("📅 Date Range:", style={'fontWeight': 'bold'}),
                dcc.DatePickerRange(
                    id='date-range-picker',
                    display_format='YYYY-MM-DD',
                    style={'width': '100%'}
                )
            ], style={'width': '30%', 'display': 'inline-block', 'margin': '10px'}),
            
            # Status Filter
            html.Div([
                html.Label("🔍 Status Filter:", style={'fontWeight': 'bold'}),
                dcc.Dropdown(
                    id='status-filter',
                    placeholder="Select status types...",
                    multi=True,
                    style={'width': '100%'}
                )
            ], style={'width': '30%', 'display': 'inline-block', 'margin': '10px'}),
            
            # Protocol Filter
            html.Div([
                html.Label("🌐 Protocol Filter:", style={'fontWeight': 'bold'}),
                dcc.Dropdown(
                    id='protocol-filter',
                    placeholder="Select protocols...",
                    multi=True,
                    style={'width': '100%'}
                )
            ], style={'width': '30%', 'display': 'inline-block', 'margin': '10px'}),
        ], style={'display': 'flex', 'flexWrap': 'wrap', 'justifyContent': 'space-between'}),
        
        html.Div([
            # IP Address Filter
            html.Div([
                html.Label("🌍 IP Address Filter:", style={'fontWeight': 'bold'}),
                dcc.Input(
                    id='ip-filter',
                    type='text',
                    placeholder='Enter IP address or range...',
                    style={'width': '100%', 'padding': '8px', 'borderRadius': '4px', 'border': '1px solid #ddd'}
                )
            ], style={'width': '45%', 'display': 'inline-block', 'margin': '10px'}),
            
            # Stream Filter
            html.Div([
                html.Label("🎬 Stream Alias Filter:", style={'fontWeight': 'bold'}),
                dcc.Dropdown(
                    id='stream-filter',
                    placeholder="Select streams...",
                    multi=True,
                    style={'width': '100%'}
                )
            ], style={'width': '45%', 'display': 'inline-block', 'margin': '10px'}),
        ], style={'display': 'flex', 'justifyContent': 'space-between'}),
        
        html.Div([
            html.Button('Apply Filters', id='apply-filters-btn', n_clicks=0,
                       style={'backgroundColor': '#3498db', 'color': 'white', 'border': 'none',
                              'padding': '10px 20px', 'borderRadius': '5px', 'cursor': 'pointer',
                              'fontSize': '14px', 'margin': '10px'}),
            html.Button('Clear Filters', id='clear-filters-btn', n_clicks=0,
                       style={'backgroundColor': '#95a5a6', 'color': 'white', 'border': 'none',
                              'padding': '10px 20px', 'borderRadius': '5px', 'cursor': 'pointer',
                              'fontSize': '14px', 'margin': '10px'}),
            html.Div(id='filter-status', style={'display': 'inline-block', 'margin': '10px', 'fontStyle': 'italic'})
        ])
    ], id='filter-section', style={'padding': '20px', 'backgroundColor': 'white', 'borderRadius': '10px',
                                   'boxShadow': '0 2px 10px rgba(0,0,0,0.1)', 'marginBottom': '20px',
                                   'display': 'none'}),  # Initially hidden
    
    # Analysis Results Tabs
    html.Div([
        dcc.Tabs(id='main-tabs', value='summary-tab', children=[
            dcc.Tab(label='📊 Summary Report', value='summary-tab'),
            dcc.Tab(label='📈 Time Analysis', value='time-tab'),
            dcc.Tab(label='🌐 IP Analysis', value='ip-tab'),
            dcc.Tab(label='� Error Analysis', value='error-tab'),
            dcc.Tab(label='📱 User Behavior', value='behavior-tab'),
            dcc.Tab(label='🎬 Content Performance', value='content-tab'),
            dcc.Tab(label='�📋 Data Table', value='data-tab'),
            dcc.Tab(label='📥 Export', value='export-tab'),
        ], style={'marginBottom': '20px'}),
        
        html.Div(id='tab-content')
    ], style={'padding': '20px', 'backgroundColor': 'white', 'borderRadius': '10px',
              'boxShadow': '0 2px 10px rgba(0,0,0,0.1)'}),
    
    # Store components for data
    dcc.Store(id='analysis-data'),
    dcc.Store(id='uploaded-filename'),
    dcc.Store(id='filtered-data'),
    dcc.Store(id='filter-options'),
], style={'fontFamily': 'Arial, sans-serif', 'margin': '20px', 'backgroundColor': '#f4f4f4'})

# Callback for file upload
@app.callback(
    [Output('upload-status', 'children'),
     Output('uploaded-filename', 'data')],
    [Input('upload-data', 'contents')],
    [State('upload-data', 'filename')]
)
def update_upload_status(contents, filename):
    if contents is not None:
        # Save uploaded file
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        
        # Create logs directory if it doesn't exist
        os.makedirs('logs', exist_ok=True)
        file_path = f'logs/{filename}'
        
        try:
            with open(file_path, 'wb') as f:
                f.write(decoded)
            
            file_size = len(decoded) / (1024 * 1024)  # Size in MB
            
            return [
                html.Div([
                    html.P(f"✅ File uploaded successfully: {filename}", 
                           style={'color': '#27ae60', 'fontWeight': 'bold'}),
                    html.P(f"📏 File size: {file_size:.2f} MB"),
                    html.P(f"💾 Saved to: {file_path}")
                ])
            ], filename
        except Exception as e:
            return [
                html.Div([
                    html.P(f"❌ Error uploading file: {str(e)}", 
                           style={'color': '#e74c3c', 'fontWeight': 'bold'})
                ])
            ], None
    
    return [html.P("No file uploaded yet.", style={'color': '#7f8c8d'})], None

# Callback for analysis
@app.callback(
    [Output('analysis-data', 'data'),
     Output('loading-output', 'children')],
    [Input('analyze-button', 'n_clicks')],
    [State('uploaded-filename', 'data')],
    prevent_initial_call=True
)
def analyze_log_file(n_clicks, filename):
    if n_clicks == 0 or filename is None:
        return None, ""
    
    try:
        global current_analyzer, current_data
        
        file_path = f'logs/{filename}'
        
        if not os.path.exists(file_path):
            return None, html.Div([
                html.P(f"❌ File not found: {file_path}", 
                       style={'color': '#e74c3c', 'fontWeight': 'bold'})
            ])
        
        # Initialize enhanced JSON analyzer (falls back to traditional if needed)
        current_analyzer = JSONNimbleLogAnalyzer(file_path)
        
        # Run analysis with error handling for each step
        try:
            current_analyzer.read_log_file()
        except Exception as e:
            print(f"Read log file error: {str(e)}")
            return None, html.Div([
                html.P(f"❌ Error reading log file: {str(e)}", 
                       style={'color': '#e74c3c', 'fontWeight': 'bold'}),
                html.P("This might be due to file encoding or format issues."),
                html.P("💡 Try using a smaller sample of your log file first.")
            ])
        
        if current_analyzer.data is None or current_analyzer.data.empty:
            return None, html.Div([
                html.P("❌ No data could be parsed from the log file.", 
                       style={'color': '#e74c3c', 'fontWeight': 'bold'}),
                html.P("Please check if the file format is supported."),
                html.P("Supported formats: JSON (one per line), Apache, Nginx, IIS logs")
            ])
        
        # Generate reports
        current_analyzer.generate_summary_report()
        current_analyzer.generate_time_analysis()
        
        # Generate streaming-specific analytics if JSON format detected
        if hasattr(current_analyzer, 'format_detected') and current_analyzer.format_detected == 'json':
            current_analyzer.generate_streaming_analytics()
        
        current_analyzer.create_visualizations()
        
        current_data = current_analyzer.data.copy()  # Make a copy to avoid reference issues
        
        # Calculate statistics safely
        total_entries = len(current_data)
        parsed_entries = len(current_data[current_data['parsed'] == True]) if 'parsed' in current_data.columns else total_entries
        
        # Determine format info
        format_info = ""
        if hasattr(current_analyzer, 'format_detected') and current_analyzer.format_detected:
            format_info = f" (Format: {current_analyzer.format_detected.upper()})"
        
        # Prepare data for storage (convert to dict for JSON serialization)
        analysis_result = {
            'total_entries': total_entries,
            'parsed_entries': parsed_entries,
            'filename': filename,
            'analysis_timestamp': datetime.now().isoformat(),
            'format': getattr(current_analyzer, 'format_detected', 'traditional'),
            'status': 'success'
        }
        
        return analysis_result, html.Div([
            html.P(f"✅ Analysis completed successfully!{format_info}", 
                   style={'color': '#27ae60', 'fontWeight': 'bold'}),
            html.P(f"📊 Processed {analysis_result['total_entries']:,} log entries"),
            html.P(f"✓ Successfully parsed {analysis_result['parsed_entries']:,} entries"),
            html.P(f"🎯 Log format detected: {analysis_result['format'].upper()}", 
                   style={'color': '#3498db', 'fontStyle': 'italic'}) if analysis_result.get('format') else html.Span()
        ])
        
    except Exception as e:
        print(f"Analysis error: {str(e)}")  # Log to console for debugging
        return None, html.Div([
            html.P(f"❌ Analysis failed: {str(e)}", 
                   style={'color': '#e74c3c', 'fontWeight': 'bold'}),
            html.P("Check the console for more details.", 
                   style={'color': '#7f8c8d', 'fontSize': '14px'}),
            html.P("💡 Tip: Ensure your log file is either JSON format (one JSON object per line) or traditional log format", 
                   style={'color': '#f39c12', 'fontSize': '12px', 'fontStyle': 'italic'})
        ])

# Callback to show/hide filter section and populate filter options
@app.callback(
    [Output('filter-section', 'style'),
     Output('filter-options', 'data'),
     Output('status-filter', 'options'),
     Output('protocol-filter', 'options'),
     Output('stream-filter', 'options'),
     Output('date-range-picker', 'start_date'),
     Output('date-range-picker', 'end_date')],
    [Input('analysis-data', 'data')]
)
def update_filter_options(analysis_data):
    if analysis_data is None:
        return {'display': 'none'}, None, [], [], [], None, None
    
    try:
        global current_data
        if current_data is None or current_data.empty:
            return {'display': 'none'}, None, [], [], [], None, None
        
        # Show filter section
        filter_style = {'padding': '20px', 'backgroundColor': 'white', 'borderRadius': '10px',
                       'boxShadow': '0 2px 10px rgba(0,0,0,0.1)', 'marginBottom': '20px',
                       'display': 'block'}
        
        # Prepare filter options
        filter_options = {}
        
        # Status options
        status_options = []
        if 'status' in current_data.columns:
            unique_statuses = current_data['status'].dropna().unique()
            status_options = [{'label': status, 'value': status} for status in sorted(unique_statuses)]
            filter_options['statuses'] = unique_statuses.tolist()
        
        # Protocol options
        protocol_options = []
        if 'protocol' in current_data.columns:
            unique_protocols = current_data['protocol'].dropna().unique()
            protocol_options = [{'label': protocol, 'value': protocol} for protocol in sorted(unique_protocols)]
            filter_options['protocols'] = unique_protocols.tolist()
        
        # Stream options
        stream_options = []
        if 'stream_alias' in current_data.columns:
            unique_streams = current_data['stream_alias'].dropna().unique()
            # Limit to top 100 streams for performance
            stream_counts = current_data['stream_alias'].value_counts().head(100)
            stream_options = [{'label': f"{stream} ({count})", 'value': stream} 
                             for stream, count in stream_counts.items()]
            filter_options['streams'] = stream_counts.index.tolist()
        
        # Date range
        start_date = None
        end_date = None
        if 'timestamp' in current_data.columns:
            try:
                # Try to use datetime column first if available, otherwise parse timestamp
                if 'datetime' in current_data.columns and not current_data['datetime'].isna().all():
                    timestamps = pd.to_datetime(current_data['datetime'], errors='coerce')
                else:
                    timestamps = pd.to_datetime(current_data['timestamp'], errors='coerce')
                start_date = timestamps.min().date()
                end_date = timestamps.max().date()
                filter_options['date_range'] = [start_date.isoformat(), end_date.isoformat()]
            except Exception as e:
                print(f"Date range error: {str(e)}")
        
        return filter_style, filter_options, status_options, protocol_options, stream_options, start_date, end_date
        
    except Exception as e:
        print(f"Filter options error: {str(e)}")
        return {'display': 'none'}, None, [], [], [], None, None

# Callback for tab content
@app.callback(
    Output('tab-content', 'children'),
    [Input('main-tabs', 'value'),
     Input('analysis-data', 'data')],
    prevent_initial_call=True
)
def render_tab_content(active_tab, analysis_data):
    if analysis_data is None:
        return html.Div([
            html.P("📤 Please upload and analyze a log file first.", 
                   style={'textAlign': 'center', 'color': '#7f8c8d', 'fontSize': '18px',
                          'margin': '50px'})
        ])
    
    try:
        global current_data
        
        if current_data is None or current_data.empty:
            return html.Div([
                html.P("⚠️ No analysis data available. Please run the analysis again.", 
                       style={'textAlign': 'center', 'color': '#e67e22', 'fontSize': '18px',
                              'margin': '50px'})
            ])
        
        if active_tab == 'summary-tab':
            return render_summary_tab(analysis_data)
        elif active_tab == 'time-tab':
            return render_time_tab()
        elif active_tab == 'ip-tab':
            return render_ip_tab()
        elif active_tab == 'http-errors-tab':
            return render_http_errors_tab()
        elif active_tab == 'error-tab':
            return render_error_tab()
        elif active_tab == 'behavior-tab':
            return render_behavior_tab()
        elif active_tab == 'content-tab':
            return render_content_tab()
        elif active_tab == 'streaming-tab':
            return render_streaming_tab()
        elif active_tab == 'data-tab':
            return render_data_tab()
        elif active_tab == 'export-tab':
            return render_export_tab()
        
        return html.Div("Select a tab to view content")
        
    except Exception as e:
        print(f"Tab rendering error: {str(e)}")  # Log to console
        return html.Div([
            html.P(f"❌ Error loading tab content: {str(e)}", 
                   style={'color': '#e74c3c', 'fontWeight': 'bold', 'textAlign': 'center',
                          'margin': '50px'})
        ])

def render_summary_tab(analysis_data):
    """Render the summary report tab."""
    global current_data
    
    try:
        if current_data is None or current_data.empty:
            return html.P("No data available for summary.")
        
        # Calculate statistics safely
        total_entries = analysis_data.get('total_entries', 0)
        parsed_entries = analysis_data.get('parsed_entries', 0)
        parse_rate = (parsed_entries / total_entries * 100) if total_entries > 0 else 0
        
        # Status code analysis
        status_stats = []
        if 'status_code' in current_data.columns:
            try:
                status_counts = current_data['status_code'].value_counts()
                for status, count in status_counts.head(10).items():
                    if status and str(status).strip():  # Check if status is valid
                        status_stats.append(html.Tr([
                            html.Td(str(status)),
                            html.Td(f"{count:,}"),
                            html.Td(f"{(count/total_entries)*100:.2f}%" if total_entries > 0 else "0%")
                        ]))
            except Exception as e:
                print(f"Status code analysis error: {str(e)}")
                status_stats = [html.Tr([
                    html.Td("N/A", colSpan=3, style={'textAlign': 'center', 'color': '#7f8c8d'})
                ])]
        
        # If no status stats, show N/A row
        if not status_stats:
            status_stats = [html.Tr([
                html.Td("No status code data available", colSpan=3, 
                       style={'textAlign': 'center', 'color': '#7f8c8d'})
            ])]
        
        return html.Div([
            # Key metrics
            html.Div([
                html.Div([
                    html.H4(f"{total_entries:,}", style={'margin': '0', 'color': 'white'}),
                    html.P("Total Entries", style={'margin': '0', 'color': 'white'})
                ], className='metric-box', style={'textAlign': 'center', 'padding': '20px', 
                                                 'backgroundColor': '#3498db', 'color': 'white',
                                                 'borderRadius': '10px', 'margin': '10px'}),
                
                html.Div([
                    html.H4(f"{parsed_entries:,}", style={'margin': '0', 'color': 'white'}),
                    html.P("Parsed Successfully", style={'margin': '0', 'color': 'white'})
                ], className='metric-box', style={'textAlign': 'center', 'padding': '20px', 
                                                 'backgroundColor': '#27ae60', 'color': 'white',
                                                 'borderRadius': '10px', 'margin': '10px'}),
                
                html.Div([
                    html.H4(f"{parse_rate:.1f}%", style={'margin': '0', 'color': 'white'}),
                    html.P("Parse Success Rate", style={'margin': '0', 'color': 'white'})
                ], className='metric-box', style={'textAlign': 'center', 'padding': '20px', 
                                                 'backgroundColor': '#e67e22', 'color': 'white',
                                                 'borderRadius': '10px', 'margin': '10px'}),
            ], style={'display': 'flex', 'justifyContent': 'space-around', 'marginBottom': '30px'}),
            
            # Status code table
            html.H4("📊 Status Code Distribution"),
            html.Table([
                html.Thead([
                    html.Tr([
                        html.Th("Status Code", style={'padding': '10px', 'borderBottom': '2px solid #3498db'}),
                        html.Th("Count", style={'padding': '10px', 'borderBottom': '2px solid #3498db'}),
                        html.Th("Percentage", style={'padding': '10px', 'borderBottom': '2px solid #3498db'})
                    ])
                ]),
                html.Tbody(status_stats)
            ], style={'width': '100%', 'borderCollapse': 'collapse', 'margin': '20px 0',
                     'boxShadow': '0 2px 10px rgba(0,0,0,0.1)'}),
        ])
        
    except Exception as e:
        print(f"Summary tab error: {str(e)}")
        return html.Div([
            html.P(f"❌ Error generating summary: {str(e)}", 
                   style={'color': '#e74c3c', 'fontWeight': 'bold'})
        ])

def render_time_tab():
    """Render the time analysis tab."""
    global current_data
    
    try:
        if current_data is None or 'timestamp' not in current_data.columns:
            return html.Div([
                html.P("No timestamp data available for time analysis.", 
                       style={'textAlign': 'center', 'color': '#7f8c8d', 'margin': '50px'})
            ])
        
        charts = []
        
        # Hourly distribution chart
        if 'hour' in current_data.columns:
            try:
                hourly_counts = current_data['hour'].value_counts().sort_index()
                
                if not hourly_counts.empty:
                    fig_hourly = px.bar(
                        x=hourly_counts.index,
                        y=hourly_counts.values,
                        title="Request Distribution by Hour",
                        labels={'x': 'Hour of Day', 'y': 'Number of Requests'}
                    )
                    fig_hourly.update_layout(showlegend=False, height=400)
                    charts.append(dcc.Graph(figure=fig_hourly))
                    
            except Exception as e:
                print(f"Hourly chart error: {str(e)}")
                charts.append(html.P(f"Error creating hourly chart: {str(e)}", 
                                    style={'color': '#e74c3c'}))
        
        # Daily timeline
        try:
            # Create date column if it doesn't exist
            if 'date' not in current_data.columns:
                if 'datetime' in current_data.columns and not current_data['datetime'].isna().all():
                    current_data['date'] = pd.to_datetime(current_data['datetime'], errors='coerce').dt.date
                else:
                    current_data['date'] = pd.to_datetime(current_data['timestamp'], errors='coerce').dt.date
            
            # Filter out null dates
            valid_dates = current_data.dropna(subset=['date'])
            
            if not valid_dates.empty:
                daily_counts = valid_dates['date'].value_counts().sort_index()
                
                if not daily_counts.empty:
                    fig_timeline = px.line(
                        x=daily_counts.index,
                        y=daily_counts.values,
                        title="Daily Request Volume Over Time",
                        labels={'x': 'Date', 'y': 'Number of Requests'}
                    )
                    fig_timeline.update_layout(height=400)
                    
                    if charts:  # Add separator if there are other charts
                        charts.append(html.Hr())
                    charts.append(dcc.Graph(figure=fig_timeline))
                    
        except Exception as e:
            print(f"Timeline chart error: {str(e)}")
            charts.append(html.P(f"Error creating timeline chart: {str(e)}", 
                                style={'color': '#e74c3c'}))
        
        if not charts:
            return html.Div([
                html.P("Time analysis data could not be processed.", 
                       style={'textAlign': 'center', 'color': '#7f8c8d', 'margin': '50px'})
            ])
            
        return html.Div(charts)
        
    except Exception as e:
        print(f"Time tab error: {str(e)}")
        return html.Div([
            html.P(f"❌ Error loading time analysis: {str(e)}", 
                   style={'color': '#e74c3c', 'fontWeight': 'bold', 'textAlign': 'center',
                          'margin': '50px'})
        ])

def render_error_tab():
    """Render the error analysis tab."""
    global current_data
    
    try:
        if current_data is None or current_data.empty:
            return html.Div([
                html.P("No data available for error analysis.", 
                       style={'textAlign': 'center', 'color': '#7f8c8d', 'margin': '50px'})
            ])
        
        charts = []
        
        # Error analysis
        if 'status_code' in current_data.columns:
            try:
                # Filter errors (4xx and 5xx)
                errors = current_data[current_data['status_code'] >= 400]
                
                if not errors.empty:
                    # Error distribution chart
                    error_counts = errors['status_code'].value_counts().sort_index()
                    
                    fig_errors = px.bar(
                        x=error_counts.index,
                        y=error_counts.values,
                        title="Error Status Code Distribution",
                        labels={'x': 'Status Code', 'y': 'Number of Errors'},
                        color=error_counts.values,
                        color_continuous_scale='Reds'
                    )
                    fig_errors.update_layout(showlegend=False, height=400)
                    charts.append(dcc.Graph(figure=fig_errors))
                    
                    # Error timeline
                    if 'hour' in errors.columns:
                        hourly_errors = errors.groupby('hour').size()
                        
                        fig_error_timeline = px.line(
                            x=hourly_errors.index,
                            y=hourly_errors.values,
                            title="Error Distribution by Hour",
                            labels={'x': 'Hour of Day', 'y': 'Number of Errors'}
                        )
                        fig_error_timeline.update_traces(line_color='red')
                        fig_error_timeline.update_layout(height=400)
                        charts.append(html.Hr())
                        charts.append(dcc.Graph(figure=fig_error_timeline))
                    
                    # Top error sources
                    if 'ip_address' in errors.columns:
                        error_ips = errors['ip_address'].value_counts().head(10)
                        
                        if not error_ips.empty:
                            charts.append(html.Hr())
                            charts.append(html.H4("🚨 Top Error Sources"))
                            charts.append(dash_table.DataTable(
                                data=[{'IP Address': ip, 'Error Count': count, 
                                      'Percentage': f"{(count/len(errors))*100:.2f}%"} 
                                      for ip, count in error_ips.items()],  # type: ignore
                                columns=[
                                    {'name': 'IP Address', 'id': 'IP Address'},
                                    {'name': 'Error Count', 'id': 'Error Count'},
                                    {'name': 'Percentage', 'id': 'Percentage'}
                                ],
                                style_header={'backgroundColor': '#e74c3c', 'color': 'white', 'fontWeight': 'bold'},
                                style_data={'backgroundColor': '#ffeaa7'}
                            ))
                else:
                    charts.append(html.Div([
                        html.H3("🎉 No Errors Found!", style={'color': '#27ae60', 'textAlign': 'center'}),
                        html.P("Your server is running smoothly with no 4xx or 5xx errors!", 
                               style={'textAlign': 'center', 'color': '#7f8c8d'})
                    ]))
                    
            except Exception as e:
                print(f"Error analysis error: {str(e)}")
                charts.append(html.P(f"Error analyzing errors: {str(e)}", 
                                    style={'color': '#e74c3c'}))
        
        if not charts:
            charts.append(html.P("No status code data available for error analysis.", 
                                style={'textAlign': 'center', 'color': '#7f8c8d', 'margin': '50px'}))
            
        return html.Div(charts)
        
    except Exception as e:
        print(f"Error tab error: {str(e)}")
        return html.Div([
            html.P(f"❌ Error loading error analysis: {str(e)}", 
                   style={'color': '#e74c3c', 'fontWeight': 'bold', 'textAlign': 'center',
                          'margin': '50px'})
        ])

def render_behavior_tab():
    """Render the user behavior analysis tab."""
    global current_data
    
    try:
        if current_data is None or current_data.empty:
            return html.Div([
                html.P("No data available for behavior analysis.", 
                       style={'textAlign': 'center', 'color': '#7f8c8d', 'margin': '50px'})
            ])
        
        charts = []
        
        # User agent analysis
        if 'user_agent' in current_data.columns:
            try:
                # Basic device type detection
                mobile_count = len(current_data[current_data['user_agent'].str.contains('Mobile|Android|iPhone', case=False, na=False)])
                desktop_count = len(current_data) - mobile_count
                
                # Device type pie chart
                fig_devices = px.pie(
                    values=[desktop_count, mobile_count],
                    names=['Desktop/Other', 'Mobile'],
                    title="Device Type Distribution",
                    color_discrete_sequence=['#3498db', '#e67e22']
                )
                charts.append(dcc.Graph(figure=fig_devices))
                
            except Exception as e:
                print(f"User agent analysis error: {str(e)}")
        
        # Request size analysis
        if 'bytes_sent' in current_data.columns:
            try:
                # Convert to MB for better readability
                current_data['mb_sent'] = current_data['bytes_sent'] / (1024 * 1024)
                
                fig_bandwidth = px.histogram(
                    current_data, 
                    x='mb_sent',
                    title="Bandwidth Usage Distribution (MB per request)",
                    labels={'mb_sent': 'MB Sent', 'count': 'Number of Requests'},
                    nbins=30
                )
                charts.append(html.Hr())
                charts.append(dcc.Graph(figure=fig_bandwidth))
                
            except Exception as e:
                print(f"Bandwidth analysis error: {str(e)}")
        
        # Geographic insights (if available)
        if 'ip_address' in current_data.columns:
            try:
                unique_ips = current_data['ip_address'].nunique()
                total_requests = len(current_data)
                avg_requests_per_ip = total_requests / unique_ips if unique_ips > 0 else 0
                
                charts.append(html.Hr())
                charts.append(html.Div([
                    html.H4("👥 User Engagement Metrics"),
                    html.Div([
                        html.Div([
                            html.H5(f"{unique_ips:,}", style={'margin': '0', 'color': '#2c3e50'}),
                            html.P("Unique Visitors", style={'margin': '0', 'color': '#7f8c8d'})
                        ], style={'textAlign': 'center', 'padding': '20px', 'backgroundColor': '#ecf0f1', 
                                 'borderRadius': '10px', 'margin': '10px'}),
                        
                        html.Div([
                            html.H5(f"{avg_requests_per_ip:.1f}", style={'margin': '0', 'color': '#2c3e50'}),
                            html.P("Avg Requests/User", style={'margin': '0', 'color': '#7f8c8d'})
                        ], style={'textAlign': 'center', 'padding': '20px', 'backgroundColor': '#ecf0f1', 
                                 'borderRadius': '10px', 'margin': '10px'}),
                    ], style={'display': 'flex', 'justifyContent': 'space-around'})
                ]))
                
            except Exception as e:
                print(f"User metrics error: {str(e)}")
        
        if not charts:
            charts.append(html.P("No user behavior data available for analysis.", 
                                style={'textAlign': 'center', 'color': '#7f8c8d', 'margin': '50px'}))
            
        return html.Div(charts)
        
    except Exception as e:
        print(f"Behavior tab error: {str(e)}")
        return html.Div([
            html.P(f"❌ Error loading behavior analysis: {str(e)}", 
                   style={'color': '#e74c3c', 'fontWeight': 'bold', 'textAlign': 'center',
                          'margin': '50px'})
        ])

def render_content_tab():
    """Render the content performance analysis tab."""
    global current_data
    
    try:
        if current_data is None or current_data.empty:
            return html.Div([
                html.P("No data available for content analysis.", 
                       style={'textAlign': 'center', 'color': '#7f8c8d', 'margin': '50px'})
            ])
        
        charts = []
        
        # URL/Content analysis
        if 'url' in current_data.columns or 'request' in current_data.columns:
            try:
                url_column = 'url' if 'url' in current_data.columns else 'request'
                
                # Most requested content
                popular_content = current_data[url_column].value_counts().head(15)
                
                if not popular_content.empty:
                    fig_content = px.bar(
                        x=popular_content.values,
                        y=[str(url)[:50] + '...' if len(str(url)) > 50 else str(url) 
                           for url in popular_content.index],
                        orientation='h',
                        title="Most Requested Content (Top 15)",
                        labels={'x': 'Request Count', 'y': 'Content/URL'}
                    )
                    fig_content.update_layout(height=600)
                    charts.append(dcc.Graph(figure=fig_content))
                    
                    # Content success rates
                    if 'status_code' in current_data.columns:
                        success_rates = current_data.groupby(url_column).apply(
                            lambda x: (x['status_code'] == 200).sum() / len(x) * 100
                        ).sort_values(ascending=False)
                        
                        top_performing = success_rates.head(10)
                        
                        charts.append(html.Hr())
                        charts.append(html.H4("🏆 Top Performing Content (Success Rate)"))
                        charts.append(dash_table.DataTable(
                            data=[{'Content': str(content)[:80] + ('...' if len(str(content)) > 80 else ''), 
                                  'Success Rate': f"{rate:.1f}%", 
                                  'Total Requests': current_data[current_data[url_column] == content].shape[0]} 
                                  for content, rate in top_performing.items()],
                            columns=[
                                {'name': 'Content/URL', 'id': 'Content'},
                                {'name': 'Success Rate', 'id': 'Success Rate'},
                                {'name': 'Total Requests', 'id': 'Total Requests'}
                            ],
                            style_header={'backgroundColor': '#27ae60', 'color': 'white', 'fontWeight': 'bold'},
                            style_data={'backgroundColor': '#d5f4e6'}
                        ))
                
            except Exception as e:
                print(f"Content analysis error: {str(e)}")
                charts.append(html.P(f"Error analyzing content: {str(e)}", 
                                    style={'color': '#e74c3c'}))
        
        # File type analysis
        if 'url' in current_data.columns or 'request' in current_data.columns:
            try:
                url_column = 'url' if 'url' in current_data.columns else 'request'
                
                # Extract file extensions
                file_extensions = current_data[url_column].str.extract(r'\.([a-zA-Z0-9]+)(?:\?|$)')[0].fillna('no-extension')
                extension_counts = file_extensions.value_counts().head(10)
                
                if not extension_counts.empty:
                    fig_extensions = px.pie(
                        values=extension_counts.values,
                        names=extension_counts.index,
                        title="Content Type Distribution (by file extension)"
                    )
                    charts.append(html.Hr())
                    charts.append(dcc.Graph(figure=fig_extensions))
                
            except Exception as e:
                print(f"File type analysis error: {str(e)}")
        
        if not charts:
            charts.append(html.P("No content/URL data available for analysis.", 
                                style={'textAlign': 'center', 'color': '#7f8c8d', 'margin': '50px'}))
            
        return html.Div(charts)
        
    except Exception as e:
        print(f"Content tab error: {str(e)}")
        return html.Div([
            html.P(f"❌ Error loading content analysis: {str(e)}", 
                   style={'color': '#e74c3c', 'fontWeight': 'bold', 'textAlign': 'center',
                          'margin': '50px'})
        ])

def render_ip_tab():
    """Render the IP analysis tab with IPinfo integration."""
    global current_data
    
    try:
        if current_data is None or 'ip_address' not in current_data.columns:
            return html.Div([
                html.P("No IP address data available.", 
                       style={'textAlign': 'center', 'color': '#7f8c8d', 'margin': '50px'})
            ])
        
        # Filter out null/empty IP addresses
        valid_ips = current_data[current_data['ip_address'].notna() & (current_data['ip_address'] != '')]
        
        if valid_ips.empty:
            return html.Div([
                html.P("No valid IP addresses found in the data.", 
                       style={'textAlign': 'center', 'color': '#7f8c8d', 'margin': '50px'})
            ])
        
        # Get top IPs
        top_ips = valid_ips['ip_address'].value_counts().head(20)
        
        # Try to enrich with IPinfo data
        ipinfo_enabled = True
        enriched_data = None
        
        try:
            # Use the enhanced IPinfo service for faster offline lookups
            sample_ips = valid_ips['ip_address'].unique()[:100]  # Increased limit since offline is faster
            enriched_sample_dict = enhanced_ipinfo_service.bulk_lookup(sample_ips.tolist())
            
            # Convert to DataFrame format
            enriched_list = []
            for ip, info in enriched_sample_dict.items():
                enriched_list.append({
                    'ip': ip,
                    'country': info.get('country', 'Unknown'),
                    'country_name': info.get('country_name', 'Unknown'),
                    'country_code': info.get('country_code', 'XX'),
                    'region': info.get('region', 'Unknown'),
                    'city': info.get('city', 'Unknown'),
                    'org': info.get('org', 'Unknown'),
                    'asn': info.get('asn', 'Unknown'),
                    'as_name': info.get('as_name', 'Unknown'),
                    'as_domain': info.get('as_domain', 'unknown'),
                    'continent': info.get('continent', 'Unknown'),
                    'continent_code': info.get('continent_code', 'XX'),
                    'is_private': info.get('country') == 'Private',
                    'source': info.get('source', 'unknown')
                })
            
            enriched_sample = pd.DataFrame(enriched_list)
            
            # Merge back with original data
            enriched_data = valid_ips.merge(
                enriched_sample[['ip', 'country', 'country_name', 'country_code', 'region', 'city', 'org', 'asn', 'as_name', 'as_domain', 'continent', 'continent_code', 'is_private', 'source']], 
                left_on='ip_address', 
                right_on='ip', 
                how='left'
            )
            
        except Exception as e:
            print(f"Enhanced IPinfo enrichment failed: {e}")
            ipinfo_enabled = False
        
        # Create components list
        components = []
        
        # Top IPs Chart
        if not top_ips.empty:
            fig_ips = px.bar(
                x=top_ips.values,
                y=top_ips.index,
                orientation='h',
                title="Top 20 IP Addresses by Request Count",
                labels={'x': 'Number of Requests', 'y': 'IP Address'}
            )
            fig_ips.update_layout(height=600)
            components.append(dcc.Graph(figure=fig_ips))
            components.append(html.Hr())
        
        # Country Analysis (if IPinfo data available)
        if enriched_data is not None and 'country' in enriched_data.columns:
            country_data = enriched_data[enriched_data['country'].notna() & (enriched_data['country'] != 'Unknown')]
            if not country_data.empty:
                country_stats = country_data['country'].value_counts().head(15)
                
                if len(country_stats) > 0:
                    # Country pie chart
                    fig_countries = px.pie(
                        values=country_stats.values,
                        names=country_stats.index,
                        title="🌍 Requests by Country"
                    )
                    fig_countries.update_layout(height=500)
                    components.extend([
                        html.H4("🌍 Geographic Analysis", style={'color': '#2980b9'}),
                        dcc.Graph(figure=fig_countries),
                        html.Hr()
                    ])
        
        # ISP/Organization Analysis (if IPinfo data available)
        if enriched_data is not None and 'org' in enriched_data.columns:
            org_data = enriched_data[enriched_data['org'].notna() & (enriched_data['org'] != 'Unknown')]
            if not org_data.empty:
                org_stats = org_data['org'].value_counts().head(10)
                
                if len(org_stats) > 0:
                    fig_orgs = px.bar(
                        x=org_stats.values,
                        y=org_stats.index,
                        orientation='h',
                        title="🏢 Top ISPs/Organizations",
                        labels={'x': 'Number of Requests', 'y': 'Organization'}
                    )
                    fig_orgs.update_layout(height=400)
                    components.extend([
                        html.H4("🏢 ISP/Organization Analysis", style={'color': '#2980b9'}),
                        dcc.Graph(figure=fig_orgs),
                        html.Hr()
                    ])
        
        # Top IP Addresses Table (enhanced with geo data if available)
        table_data = []
        total_requests = len(current_data)
        
        for ip, count in top_ips.head(10).items():
            percentage = f"{(count/total_requests)*100:.2f}%" if total_requests > 0 else "0%"
            
            row = {
                'IP Address': str(ip),
                'Requests': f"{count:,}",
                'Percentage': percentage
            }
            
            # Add geographic info if available
            if enriched_data is not None:
                ip_info = enriched_data[enriched_data['ip_address'] == ip]
                if not ip_info.empty:
                    first_match = ip_info.iloc[0]
                    row['Country'] = first_match.get('country', 'Unknown')
                    row['City'] = first_match.get('city', 'Unknown')
                    row['ISP/Org'] = first_match.get('org', 'Unknown')
            
            table_data.append(row)
        
        # Table columns
        table_columns = [
            {'name': 'IP Address', 'id': 'IP Address'},
            {'name': 'Requests', 'id': 'Requests'},
            {'name': 'Percentage', 'id': 'Percentage'}
        ]
        
        if enriched_data is not None:
            table_columns.extend([
                {'name': 'Country', 'id': 'Country'},
                {'name': 'City', 'id': 'City'},
                {'name': 'ISP/Org', 'id': 'ISP/Org'}
            ])
        
        components.extend([
            html.H4("📋 Top IP Addresses Table"),
            dash_table.DataTable(
                data=table_data,
                columns=table_columns,  # type: ignore
                style_cell={'textAlign': 'left', 'padding': '10px'},
                style_header={'backgroundColor': '#3498db', 'color': 'white', 'fontWeight': 'bold'},
                style_data={'backgroundColor': '#f8f9fa'}
            )
        ])
        
        # Add IPinfo status message
        if not ipinfo_enabled:
            components.insert(0, html.Div([
                html.P("ℹ️ Enhanced geographic analysis not available. Configure IPinfo token for country and ISP details.", 
                       style={'backgroundColor': '#e8f4f8', 'color': '#2980b9', 'padding': '10px', 
                              'borderRadius': '5px', 'margin': '10px 0', 'border': '1px solid #3498db'})
            ]))
        
        return html.Div(components)
                
    except Exception as e:
        print(f"IP analysis error: {str(e)}")
        return html.Div([
            html.P(f"❌ Error loading IP analysis: {str(e)}", 
                   style={'color': '#e74c3c', 'fontWeight': 'bold', 'textAlign': 'center',
                          'margin': '50px'})
        ])

def render_http_errors_tab():
    """Render the HTTP errors and streaming analysis tab."""
    global current_data
    
    try:
        if current_data is None or current_data.empty:
            return html.Div([
                html.P("📄 No data available for HTTP error analysis.", 
                       style={'textAlign': 'center', 'color': '#7f8c8d', 'fontSize': '18px',
                              'margin': '50px'})
            ])
        
        # Filter data with HTTP errors
        http_errors_df = current_data[current_data.get('has_http_error', False) == True]
        streaming_df = current_data[current_data.get('has_stream_info', False) == True]
        server_ips_df = current_data[current_data.get('has_server_ip', False) == True]
        error_streaming_df = current_data[(current_data.get('has_http_error', False) == True) & (current_data.get('has_stream_info', False) == True)]
        
        # HTTP Error Statistics
        error_stats = []
        if not http_errors_df.empty:
            total_errors = len(http_errors_df)
            error_codes = http_errors_df['http_error_code'].value_counts()
            
            error_stats.extend([
                html.H4("🚨 HTTP Error Summary", style={'color': '#e74c3c'}),
                html.P(f"Total HTTP Errors: {total_errors:,}"),
                html.H5("Top Error Codes:", style={'marginTop': '20px'}),
            ])
            
            for code, count in error_codes.head(10).items():
                error_type = http_errors_df[http_errors_df['http_error_code'] == code]['error_type'].iloc[0] if 'error_type' in http_errors_df.columns else f"HTTP {code}"
                percentage = (count / total_errors) * 100
                error_stats.append(
                    html.P(f"🔴 {code} ({error_type}): {count:,} ({percentage:.1f}%)", 
                           style={'margin': '5px 0', 'paddingLeft': '20px'})
                )
        
        # Server IP Statistics
        server_stats = []
        if not server_ips_df.empty:
            total_server_requests = len(server_ips_df)
            unique_servers = server_ips_df['server_ip'].nunique()
            top_servers = server_ips_df['server_ip'].value_counts()
            
            server_stats.extend([
                html.H4("�️ Server IP Analysis", style={'color': '#2980b9'}),
                html.P(f"Total Server Requests: {total_server_requests:,}"),
                html.P(f"Unique Server IPs: {unique_servers:,}"),
                html.H5("Top Server IPs:", style={'marginTop': '20px'}),
            ])
            
            for server_ip, count in top_servers.head(10).items():
                percentage = (count / total_server_requests) * 100
                server_stats.append(
                    html.P(f"🌐 {server_ip}: {count:,} requests ({percentage:.1f}%)", 
                           style={'margin': '5px 0', 'paddingLeft': '20px'})
                )
        
        # Streaming Statistics  
        streaming_stats = []
        if not streaming_df.empty:
            total_streams = len(streaming_df)
            unique_streams = streaming_df['stream_name'].nunique()
            top_streams = streaming_df['stream_name'].value_counts()
            
            streaming_stats.extend([
                html.H4("📺 Stream Analysis", style={'color': '#3498db'}),
                html.P(f"Total Stream Events: {total_streams:,}"),
                html.P(f"Unique Streams: {unique_streams:,}"),
                html.H5("Top Streams:", style={'marginTop': '20px'}),
            ])
            
            for stream, count in top_streams.head(15).items():
                percentage = (count / total_streams) * 100
                streaming_stats.append(
                    html.P(f"🎬 {stream}: {count:,} ({percentage:.1f}%)", 
                           style={'margin': '5px 0', 'paddingLeft': '20px'})
                )
        
        # Error + Streaming Combined
        combined_stats = []
        if not error_streaming_df.empty:
            total_stream_errors = len(error_streaming_df)
            error_streams = error_streaming_df['stream_name'].value_counts()
            error_servers = error_streaming_df['server_ip'].value_counts() if 'server_ip' in error_streaming_df.columns else None
            
            combined_stats.extend([
                html.H4("⚠️ Stream Error Analysis", style={'color': '#f39c12'}),
                html.P(f"Total Stream-Related Errors: {total_stream_errors:,}"),
                html.H5("Most Problematic Streams:", style={'marginTop': '20px'}),
            ])
            
            for stream, count in error_streams.head(10).items():
                percentage = (count / total_stream_errors) * 100
                combined_stats.append(
                    html.P(f"� {stream}: {count:,} errors ({percentage:.1f}%)", 
                           style={'margin': '5px 0', 'paddingLeft': '20px', 'color': '#e67e22'})
                )
            
            # Add server IP analysis for errors if available
            if error_servers is not None and not error_servers.empty:
                combined_stats.extend([
                    html.H5("Most Problematic Server IPs:", style={'marginTop': '20px'}),
                ])
                
                for server_ip, count in error_servers.head(10).items():
                    percentage = (count / total_stream_errors) * 100
                    combined_stats.append(
                        html.P(f"� {server_ip}: {count:,} errors ({percentage:.1f}%)", 
                               style={'margin': '5px 0', 'paddingLeft': '20px', 'color': '#e67e22'})
                    )
        
        # Server:Stream combination analysis
        server_stream_stats = []
        server_stream_df = current_data[(current_data.get('has_server_ip', False) == True) & (current_data.get('has_stream_info', False) == True)]
        if not server_stream_df.empty:
            # Create server:stream combinations  
            server_stream_df['server_stream'] = server_stream_df['server_ip'] + ':' + server_stream_df['stream_name']
            top_combinations = server_stream_df['server_stream'].value_counts()
            
            server_stream_stats.extend([
                html.H4("🔗 Server:Stream Combinations", style={'color': '#8e44ad'}),
                html.P(f"Total Server:Stream Events: {len(server_stream_df):,}"),
                html.P(f"Unique Combinations: {server_stream_df['server_stream'].nunique():,}"),
                html.H5("Top Server:Stream Pairs:", style={'marginTop': '20px'}),
            ])
            
            for combo, count in top_combinations.head(15).items():
                if isinstance(combo, str) and ':' in combo:
                    server_ip, stream_name = combo.split(':', 1)
                else:
                    server_ip, stream_name = str(combo), "unknown"
                percentage = (count / len(server_stream_df)) * 100
                server_stream_stats.append(
                    html.P([
                        html.Span(f"🖥️ {server_ip}", style={'color': '#2980b9', 'fontWeight': 'bold'}),
                        html.Span(" → ", style={'color': '#7f8c8d'}),
                        html.Span(f"🎬 {stream_name}", style={'color': '#27ae60', 'fontWeight': 'bold'}),
                        html.Span(f": {count:,} ({percentage:.1f}%)", style={'color': '#2c3e50'})
                    ], style={'margin': '5px 0', 'paddingLeft': '20px'})
                )
                
        # Sample error messages
        sample_errors = []
        if not error_streaming_df.empty:
            sample_errors.extend([
                html.H4("📋 Sample Error Messages", style={'color': '#8e44ad', 'marginTop': '30px'}),
            ])
            
            for i, (_, row) in enumerate(error_streaming_df.head(5).iterrows()):
                sample_errors.append(
                    html.Div([
                        html.P(f"Error {i+1}:", style={'fontWeight': 'bold', 'margin': '10px 0 5px 0'}),
                        html.P(f"🔢 Code: {row.get('http_error_code', 'N/A')}", style={'margin': '2px 0', 'paddingLeft': '15px'}),
                        html.P([
                            html.Span("�️ Server IP: ", style={'color': '#7f8c8d'}),
                            html.Span(f"{row.get('server_ip', 'N/A')}", style={'color': '#2980b9', 'fontWeight': 'bold'})
                        ], style={'margin': '2px 0', 'paddingLeft': '15px'}),
                        html.P([
                            html.Span("🎬 Stream: ", style={'color': '#7f8c8d'}),
                            html.Span(f"{row.get('stream_name', 'N/A')}", style={'color': '#27ae60', 'fontWeight': 'bold'})
                        ], style={'margin': '2px 0', 'paddingLeft': '15px'}),
                        html.P(f"🌐 URL: {row.get('error_url', 'N/A')[:100]}...", style={'margin': '2px 0', 'paddingLeft': '15px', 'fontSize': '12px', 'color': '#7f8c8d'}),
                    ], style={'backgroundColor': '#f8f9fa', 'padding': '10px', 'borderRadius': '5px', 'marginBottom': '10px'})
                )
        
        # Combine all sections
        content = []
        if error_stats:
            content.extend(error_stats)
        if server_stats:
            content.extend([html.Hr()] + server_stats)
        if streaming_stats:
            content.extend([html.Hr()] + streaming_stats)
        if combined_stats:
            content.extend([html.Hr()] + combined_stats)
        if server_stream_stats:
            content.extend([html.Hr()] + server_stream_stats)
        if sample_errors:
            content.extend(sample_errors)
            
        if not content:
            content = [
                html.Div([
                    html.H4("ℹ️ No HTTP Errors or Streaming Data Found"),
                    html.P("This tab shows HTTP error codes and streaming URL details from Nimble logs."),
                    html.P("Expected log format: [timestamp] [component] E: http error code=404 for url='...'"),
                    html.P("No matching entries found in the current log file."),
                ], style={'textAlign': 'center', 'margin': '50px', 'color': '#7f8c8d'})
            ]
        
        return html.Div(content, style={'padding': '20px'})
        
    except Exception as e:
        print(f"HTTP errors tab error: {str(e)}")
        return html.Div([
            html.P(f"❌ Error loading HTTP errors analysis: {str(e)}", 
                   style={'color': '#e74c3c', 'fontWeight': 'bold', 'textAlign': 'center',
                          'margin': '50px'})
        ])

def render_streaming_tab():
    """Render the streaming analytics tab for Nimble Streamer specific metrics."""
    global current_data
    
    try:
        if current_data is None or current_data.empty:
            return html.Div([
                html.P("No data available for streaming analytics.", 
                       style={'textAlign': 'center', 'color': '#7f8c8d', 'margin': '50px'})
            ])
        
        charts = []
        
        # Session Analysis
        if 'session_id' in current_data.columns:
            try:
                # Session statistics
                total_sessions = current_data['session_id'].nunique()
                avg_requests_per_session = len(current_data) / total_sessions if total_sessions > 0 else 0
                
                # Session distribution
                session_counts = current_data['session_id'].value_counts()
                
                fig_sessions = px.histogram(
                    x=session_counts.values,
                    title="Session Activity Distribution",
                    labels={'x': 'Requests per Session', 'y': 'Number of Sessions'},
                    nbins=30
                )
                charts.append(dcc.Graph(figure=fig_sessions))
                
                # Session metrics
                charts.append(html.Div([
                    html.H4("📊 Session Metrics"),
                    html.Div([
                        html.Div([
                            html.H5(f"{total_sessions:,}", style={'margin': '0', 'color': '#2c3e50'}),
                            html.P("Total Sessions", style={'margin': '0', 'color': '#7f8c8d'})
                        ], style={'textAlign': 'center', 'padding': '20px', 'backgroundColor': '#e8f4fd', 
                                 'borderRadius': '10px', 'margin': '10px'}),
                        
                        html.Div([
                            html.H5(f"{avg_requests_per_session:.1f}", style={'margin': '0', 'color': '#2c3e50'}),
                            html.P("Avg Requests/Session", style={'margin': '0', 'color': '#7f8c8d'})
                        ], style={'textAlign': 'center', 'padding': '20px', 'backgroundColor': '#e8f4fd', 
                                 'borderRadius': '10px', 'margin': '10px'}),
                    ], style={'display': 'flex', 'justifyContent': 'space-around'})
                ]))
                
            except Exception as e:
                print(f"Session analysis error: {str(e)}")
        
        # Stream Analysis
        if 'stream_alias' in current_data.columns:
            try:
                popular_streams = current_data['stream_alias'].value_counts().head(15)
                
                if not popular_streams.empty:
                    fig_streams = px.bar(
                        x=popular_streams.values,
                        y=[str(stream)[:30] + '...' if len(str(stream)) > 30 else str(stream) 
                           for stream in popular_streams.index],
                        orientation='h',
                        title="Most Popular Streams",
                        labels={'x': 'Request Count', 'y': 'Stream Alias'}
                    )
                    fig_streams.update_layout(height=500)
                    charts.append(html.Hr())
                    charts.append(dcc.Graph(figure=fig_streams))
                    
            except Exception as e:
                print(f"Stream analysis error: {str(e)}")
        
        # Protocol Analysis
        if 'protocol' in current_data.columns:
            try:
                protocol_usage = current_data['protocol'].value_counts()
                
                if not protocol_usage.empty:
                    fig_protocols = px.pie(
                        values=protocol_usage.values,
                        names=protocol_usage.index,
                        title="Protocol Usage Distribution"
                    )
                    charts.append(html.Hr())
                    charts.append(dcc.Graph(figure=fig_protocols))
                    
            except Exception as e:
                print(f"Protocol analysis error: {str(e)}")
        
        # Connection Events Analysis
        if 'status' in current_data.columns:
            try:
                # Filter for streaming events
                streaming_events = current_data[current_data['status'].str.contains(
                    'connect|disconnect|play|publish', case=False, na=False)]
                
                if not streaming_events.empty:
                    event_counts = streaming_events['status'].value_counts()
                    
                    fig_events = px.bar(
                        x=event_counts.index,
                        y=event_counts.values,
                        title="Streaming Events Distribution",
                        labels={'x': 'Event Type', 'y': 'Count'},
                        color=event_counts.values,
                        color_continuous_scale='viridis'
                    )
                    charts.append(html.Hr())
                    charts.append(dcc.Graph(figure=fig_events))
                    
                    # Play to Publish ratio
                    play_events = len(streaming_events[streaming_events['status'].str.contains('play', case=False, na=False)])
                    publish_events = len(streaming_events[streaming_events['status'].str.contains('publish', case=False, na=False)])
                    
                    if publish_events > 0:
                        play_publish_ratio = play_events / publish_events
                        charts.append(html.Div([
                            html.H4("🎯 Streaming Metrics"),
                            html.P(f"Play to Publish Ratio: {play_publish_ratio:.2f}", 
                                   style={'fontSize': '18px', 'fontWeight': 'bold', 'color': '#2c3e50'}),
                            html.P("Higher ratios indicate more viewers per stream", 
                                   style={'color': '#7f8c8d', 'fontStyle': 'italic'})
                        ], style={'padding': '20px', 'backgroundColor': '#f8f9fa', 'borderRadius': '10px'}))
                    
            except Exception as e:
                print(f"Events analysis error: {str(e)}")
        
        if not charts:
            charts.append(html.P("No streaming-specific data available for analysis.", 
                                style={'textAlign': 'center', 'color': '#7f8c8d', 'margin': '50px'}))
            
        return html.Div(charts)
        
    except Exception as e:
        print(f"Streaming tab error: {str(e)}")
        return html.Div([
            html.P(f"❌ Error loading streaming analytics: {str(e)}", 
                   style={'color': '#e74c3c', 'fontWeight': 'bold', 'textAlign': 'center',
                          'margin': '50px'})
        ])

def render_data_tab():
    """Render the data table tab."""
    global current_data
    
    try:
        if current_data is None or current_data.empty:
            return html.Div([
                html.P("No data available.", 
                       style={'textAlign': 'center', 'color': '#7f8c8d', 'margin': '50px'})
            ])
        
        # Display first 1000 rows for performance
        display_data = current_data.head(1000)
        
        # Prepare columns - exclude problematic columns or handle them
        columns = []
        for col in display_data.columns:
            try:
                # Check if column has reasonable data types
                if display_data[col].dtype in ['object', 'int64', 'float64', 'bool', 'datetime64[ns]']:
                    columns.append({'name': col, 'id': col})
            except Exception as e:
                print(f"Column {col} skipped: {str(e)}")
                continue
        
        if not columns:
            return html.Div([
                html.P("No suitable columns found for display.", 
                       style={'textAlign': 'center', 'color': '#7f8c8d', 'margin': '50px'})
            ])
        
        # Convert data to records, handling potential issues
        try:
            table_data = display_data[[col['id'] for col in columns]].fillna('').to_dict('records')
            
            # Convert all values to strings to avoid serialization issues
            for record in table_data:
                for key, value in record.items():
                    if pd.isna(value) or value is None:
                        record[key] = ''
                    else:
                        record[key] = str(value)[:100]  # Limit string length
                        
        except Exception as e:
            print(f"Data preparation error: {str(e)}")
            return html.Div([
                html.P(f"Error preparing data for display: {str(e)}", 
                       style={'color': '#e74c3c', 'textAlign': 'center', 'margin': '50px'})
            ])
        
        return html.Div([
            html.H4(f"📋 Data Table (showing first 1,000 of {len(current_data):,} rows)"),
            html.Div([
                dash_table.DataTable(
                    data=table_data,  # type: ignore
                    columns=columns,
                    page_size=25,
                    style_cell={
                        'textAlign': 'left', 
                        'overflow': 'hidden', 
                        'textOverflow': 'ellipsis', 
                        'maxWidth': 200,
                        'padding': '10px'
                    },
                    style_header={
                        'backgroundColor': '#3498db', 
                        'color': 'white', 
                        'fontWeight': 'bold'
                    },
                    style_data={
                        'whiteSpace': 'normal', 
                        'height': 'auto',
                        'backgroundColor': '#f8f9fa'
                    },
                    filter_action="native",
                    sort_action="native",
                    page_action="native"
                )
            ], style={'overflowX': 'auto'})
        ])
        
    except Exception as e:
        print(f"Data tab error: {str(e)}")
        return html.Div([
            html.P(f"❌ Error loading data table: {str(e)}", 
                   style={'color': '#e74c3c', 'fontWeight': 'bold', 'textAlign': 'center',
                          'margin': '50px'})
        ])

def render_export_tab():
    """Render the export options tab."""
    reports_dir = "reports"
    
    if not os.path.exists(reports_dir):
        return html.P("No reports directory found. Run analysis first.")
    
    # List available files
    report_files = []
    if os.path.exists(reports_dir):
        for file in os.listdir(reports_dir):
            if file.endswith(('.csv', '.xlsx', '.png')):
                file_path = os.path.join(reports_dir, file)
                file_size = os.path.getsize(file_path)
                report_files.append({
                    'name': file,
                    'size': f"{file_size / 1024:.1f} KB",
                    'modified': datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d %H:%M:%S')
                })
    
    return html.Div([
        html.H4("📥 Export & Download Reports"),
        html.P("Your analysis reports have been saved to the 'reports' directory:"),
        
        dash_table.DataTable(
            data=report_files,
            columns=[
                {'name': 'File Name', 'id': 'name'},
                {'name': 'Size', 'id': 'size'},
                {'name': 'Modified', 'id': 'modified'}
            ],
            style_header={'backgroundColor': '#3498db', 'color': 'white', 'fontWeight': 'bold'},
            style_cell={'textAlign': 'left'}
        ),
        
        html.Hr(),
        html.Div([
            html.H5("📊 Report Types Generated:"),
            html.Ul([
                html.Li("📄 CSV files - Complete parsed log data for further analysis"),
                html.Li("📊 Excel files - Multi-sheet reports with summaries and statistics"),
                html.Li("📈 PNG files - Visualizations and charts")
            ])
        ]),
        
        html.Div([
            html.P("💡 Tip: You can find all generated reports in the 'reports' folder of your project directory.", 
                   style={'fontStyle': 'italic', 'color': '#7f8c8d'})
        ])
    ])

def find_available_port(start_port=8050, max_attempts=10):
    """Find an available port starting from start_port"""
    import socket
    
    for port in range(start_port, start_port + max_attempts):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('127.0.0.1', port))
            sock.close()
            if result != 0:  # Port is available
                return port
        except Exception:
            continue
    return None

# Apply Filters Callback
@app.callback(
    Output('analysis-data', 'data', allow_duplicate=True),
    Input('apply-filters-btn', 'n_clicks'),
    [State('date-range-picker', 'start_date'),
     State('date-range-picker', 'end_date'),
     State('status-filter', 'value'),
     State('protocol-filter', 'value'),
     State('stream-filter', 'value'),
     State('analysis-data', 'data')],
    prevent_initial_call=True
)
def apply_filters(n_clicks, start_date, end_date, status_filter, protocol_filter, stream_filter, analysis_data):
    """Apply filters to the current data and update the analysis results."""
    global current_data
    
    if n_clicks == 0 or current_data is None:
        return analysis_data
    
    try:
        print(f"Applying filters: start_date={start_date}, end_date={end_date}, status={status_filter}, protocol={protocol_filter}, stream={stream_filter}")
        
        # Start with original data
        filtered_data = current_data.copy()
        
        # Apply date range filter
        if start_date and end_date and 'timestamp' in filtered_data.columns:
            try:
                # Convert timestamp to datetime - use datetime column if available
                if 'datetime' in filtered_data.columns and not filtered_data['datetime'].isna().all():
                    filtered_data['timestamp_dt'] = pd.to_datetime(filtered_data['datetime'], errors='coerce')
                else:
                    filtered_data['timestamp_dt'] = pd.to_datetime(filtered_data['timestamp'], errors='coerce')
                
                # Convert filter dates to datetime
                start_dt = pd.to_datetime(start_date)
                end_dt = pd.to_datetime(end_date) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)  # Include full end date
                
                # Apply date filter
                date_mask = (filtered_data['timestamp_dt'] >= start_dt) & (filtered_data['timestamp_dt'] <= end_dt)
                filtered_data = filtered_data[date_mask]
                
                print(f"Date filter applied: {len(filtered_data)} records remaining (from {start_date} to {end_date})")
                
            except Exception as e:
                print(f"Date filter error: {str(e)}")
        
        # Apply status code filter
        if status_filter and 'status_code' in filtered_data.columns:
            try:
                status_mask = filtered_data['status_code'].isin(status_filter)
                filtered_data = filtered_data[status_mask]
                print(f"Status filter applied: {len(filtered_data)} records remaining")
            except Exception as e:
                print(f"Status filter error: {str(e)}")
        
        # Apply protocol filter
        if protocol_filter and 'protocol' in filtered_data.columns:
            try:
                protocol_mask = filtered_data['protocol'].isin(protocol_filter)
                filtered_data = filtered_data[protocol_mask]
                print(f"Protocol filter applied: {len(filtered_data)} records remaining")
            except Exception as e:
                print(f"Protocol filter error: {str(e)}")
        
        # Apply stream filter
        if stream_filter and 'stream_name' in filtered_data.columns:
            try:
                stream_mask = filtered_data['stream_name'].isin(stream_filter)
                filtered_data = filtered_data[stream_mask]
                print(f"Stream filter applied: {len(filtered_data)} records remaining")
            except Exception as e:
                print(f"Stream filter error: {str(e)}")
        
        # Update global data with filtered results
        current_data = filtered_data
        
        # Prepare new analysis result
        total_entries = len(filtered_data)
        parsed_entries = len(filtered_data[filtered_data['parsed'] == True]) if 'parsed' in filtered_data.columns else total_entries
        
        # Create filtered analysis result
        filtered_analysis_result = {
            'total_entries': total_entries,
            'parsed_entries': parsed_entries,
            'analysis_timestamp': datetime.now().isoformat(),
            'format_detected': analysis_data.get('format_detected', 'Unknown') if analysis_data else 'Unknown',
            'filtered': True,
            'filter_info': f"Filtered data: {total_entries} records"
        }
        
        print(f"✅ Filters applied successfully: {total_entries} records remaining")
        return filtered_analysis_result
        
    except Exception as e:
        print(f"❌ Filter application error: {str(e)}")
        return analysis_data

# IPinfo Token Configuration Callback
@app.callback(
    Output('ipinfo-status', 'children'),
    Input('set-token-button', 'n_clicks'),
    State('ipinfo-token', 'value')
)
def set_ipinfo_token_callback(n_clicks, token):
    """Set IPinfo API token when button is clicked."""
    if n_clicks > 0:
        if token and token.strip():
            try:
                set_enhanced_ipinfo_token(token.strip())
                stats = enhanced_ipinfo_service.get_statistics()
                databases_status = "🗄️ Offline databases: " + (
                    "Country ✅" if stats['databases_loaded']['country'] else "Country ❌"
                ) + ", " + (
                    "City ✅" if stats['databases_loaded']['city'] else "City ❌"
                )
                return html.Div([
                    html.P("✅ IPinfo API token configured successfully!", 
                           style={'color': '#27ae60', 'fontWeight': 'bold'}),
                    html.P(databases_status, 
                           style={'color': '#2980b9', 'fontSize': '12px'})
                ])
            except Exception as e:
                return html.Div([
                    html.P(f"❌ Error setting token: {str(e)}", 
                           style={'color': '#e74c3c'})
                ])
        else:
            return html.Div([
                html.P("⚠️ Please enter a valid API token", 
                       style={'color': '#f39c12', 'fontWeight': 'bold'})
            ])
    return html.Div()

if __name__ == '__main__':
    try:
        print("� Starting Nimble Streamer Log Analyzer Web GUI...")
        print()
        print("💡 Debug mode enabled - check console for error messages")
        print("📝 Make sure you have a log file ready to upload")
        print()
        
        # Ensure directories exist
        os.makedirs('logs', exist_ok=True)
        os.makedirs('reports', exist_ok=True)
        print("✅ Created necessary directories: logs/, reports/")
        
        # Find available port
        port = find_available_port(8050)
        if port is None:
            print("❌ No available ports found in range 8050-8059")
            print("💡 Try closing other applications or restart your computer")
            import sys
            sys.exit(1)
        
        print(f"🌐 Server will be available at: http://127.0.0.1:{port}")
        if port != 8050:
            print(f"ℹ️  Using port {port} instead of 8050 (port was busy)")
        
        print()
        print("🔥 Starting server... (Press Ctrl+C to stop)")
        print("=" * 50)
        
        app.run(debug=False, host='127.0.0.1', port=port, dev_tools_ui=False, dev_tools_props_check=False, use_reloader=False, threaded=True)
        
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Failed to start web server: {str(e)}")
        
        # Additional troubleshooting info
        error_msg = str(e).lower()
        if "thread" in error_msg or "async" in error_msg or "tcl" in error_msg:
            print("💡 Threading issue detected. Try:")
            print("   1. Close VS Code and restart it")
            print("   2. Run the batch file directly instead: start_web_gui.bat")
            print("   3. Use a fresh terminal/command prompt")
        elif "port" in error_msg:
            print("💡 Port-related error. Try:")
            print("   1. Wait a few seconds and try again")
            print("   2. Close other applications using the port")
            print("   3. Restart your terminal")
        elif "permission" in str(e).lower():
            print("💡 Permission error. Try running as administrator")
        else:
            print("💡 General error. Check that all packages are installed correctly")
        
        import sys
        sys.exit(1)
