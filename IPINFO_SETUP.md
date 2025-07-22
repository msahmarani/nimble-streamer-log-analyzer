# IPinfo Integration Configuration

## Overview
The Nimble Streamer Log Analyzer now includes IPinfo integration to provide enhanced geographic and ISP analysis of IP addresses found in your log files.

## Features Added
- **Country Analysis**: Pie chart showing request distribution by country
- **ISP/Organization Analysis**: Bar chart of top ISPs and organizations
- **Enhanced IP Table**: IP addresses now include country, city, and ISP information
- **Smart Caching**: IP lookups are cached locally to reduce API calls
- **Private IP Detection**: Private/internal IPs are automatically detected and labeled

## Setup Instructions

### 1. Get IPinfo API Token
1. Visit [https://ipinfo.io](https://ipinfo.io)
2. Sign up for a free account
3. Get your API token from the dashboard
4. Free tier includes: 50,000 requests/month, country and ASN data

### 2. Configure Token in Web GUI
1. Start the web application: `python web_gui.py`
2. Open http://127.0.0.1:8051 in your browser
3. Find the "🌍 IP Geolocation Configuration" section
4. Enter your API token in the password field
5. Click "Set Token"
6. Enable "IP Geolocation Analysis" checkbox

### 3. Example API Token Usage
```bash
# Example curl command (replace YOUR_TOKEN)
curl https://api.ipinfo.io/lite/8.8.8.8?token=YOUR_TOKEN
```

## API Response Format
```json
{
  "ip": "8.8.8.8",
  "country": "US",
  "org": "AS15169 Google LLC"
}
```

## Enhanced Features

### Country Analysis
- Visual pie chart of request distribution by country
- Automatically filters out unknown/private IPs
- Shows percentage breakdown of traffic sources

### ISP/Organization Analysis  
- Horizontal bar chart of top ISPs and organizations
- Helps identify traffic patterns and potential issues
- Useful for understanding user demographics

### Enhanced IP Table
Now includes additional columns:
- **Country**: Country code or full name
- **City**: City name (when available)
- **ISP/Org**: Internet Service Provider or organization name

### Performance Optimizations
- **Local Caching**: IP lookups are cached for 7 days to reduce API usage
- **Batch Processing**: Multiple IPs are processed efficiently
- **Rate Limiting**: Built-in delays prevent API rate limit issues
- **Sample Limiting**: Only top 50 unique IPs are analyzed to conserve API calls

## Usage Without Token
The analyzer works without an IPinfo token but with limited functionality:
- Basic IP address counting and ranking
- No geographic or ISP information
- Still shows top IP addresses and request counts

## Privacy and Security
- API tokens are stored temporarily in memory only
- Local cache file (`ip_cache.json`) contains only public IP information
- Private/internal IP addresses are never sent to external APIs
- Tokens are entered as password fields for security

## Troubleshooting

### Common Issues
1. **"IPinfo enrichment failed"**: Check your API token and internet connection
2. **Rate limit errors**: Free tier has monthly limits, consider upgrading
3. **No geographic data**: Ensure token is set and "Enable IP Geolocation Analysis" is checked

### API Limits
- Free tier: 50,000 requests/month
- Rate limit: ~1000 requests per day for free accounts
- Consider paid plans for higher usage

### Cache Management
- Cache file: `ip_cache.json`
- Cache duration: 7 days
- Manual cache clearing: Delete `ip_cache.json` file

## Example Log Analysis Output

### Before IPinfo Integration
```
Top IP Addresses:
192.168.1.100 - 1,250 requests (25%)
203.0.113.45 - 890 requests (18%)
198.51.100.23 - 654 requests (13%)
```

### After IPinfo Integration
```
Top IP Addresses:
192.168.1.100 - Private Network - 1,250 requests (25%)
203.0.113.45 - Australia (Sydney) - Telstra Corp - 890 requests (18%) 
198.51.100.23 - United States (New York) - Verizon - 654 requests (13%)

Country Distribution:
🇺🇸 United States: 45%
🇦🇺 Australia: 25% 
🇬🇧 United Kingdom: 15%
🏠 Private/Internal: 15%
```
