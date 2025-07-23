# 🌍 IPinfo Integration Guide

## Quick Start Options

### Option 1: Use Included Offline Database (Recommended)
- ✅ **No setup needed** - Works immediately
- ✅ **Offline capable** - No internet required
- ✅ **Fast performance** - Instant lookups
- ✅ **No API costs** - Completely free

The included `ipinfo_lite.mmdb` database provides basic country/continent data for most IPs.

### Option 2: Add Your Own IPinfo Token (Enhanced)
Get enhanced geolocation data with city, ISP, and organization information.

1. **Get Free Token:**
   - Visit [ipinfo.io](https://ipinfo.io)
   - Sign up for free account (50,000 requests/month)
   - Copy your API token

2. **Configure Token:**
   - In web interface: Go to settings and paste your token
   - Or set environment variable: `export IPINFO_TOKEN="your_token_here"`

3. **Benefits:**
   - ✅ **City-level accuracy** - Not just country
   - ✅ **ISP/Organization data** - See who owns the IP
   - ✅ **Latest database** - Always up-to-date
   - ✅ **Commercial use** - No licensing concerns

## Database Strategy

### 4-Layer Lookup System:
1. **Local SQLite DB** (0.1ms) - Your analyzed IPs
2. **Memory Cache** (0.2ms) - Recent lookups  
3. **Offline MMDB** (2ms) - Included database
4. **IPinfo API** (200ms) - Online when token provided

### Smart Fallback:
- Without token: Uses offline database (good coverage)
- With token: Enhanced online data + offline backup
- Best of both worlds: Speed + accuracy

## License & Redistribution

### IPinfo Lite Database:
- Free for non-commercial use
- Redistribution allowed for open source projects
- Check [IPinfo's terms](https://ipinfo.io/terms) for commercial use

### Recommendation:
- Include the lite database for easy setup
- Encourage users to get tokens for enhanced features
- Document both options clearly

## Usage Examples

```python
# Works without token (offline database)
analyzer = LogAnalyzer()
result = analyzer.analyze_log("mylog.txt")

# Enhanced with token
set_ipinfo_token("your_token_here") 
result = analyzer.analyze_log("mylog.txt")  # Now with city/ISP data
```
