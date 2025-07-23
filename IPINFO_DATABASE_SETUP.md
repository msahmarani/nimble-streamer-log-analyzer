# 🌍 IPinfo Database Setup Guide

## Automatic Setup (Recommended)

The `setup_oracle_linux.sh` script automatically downloads the free IPinfo Lite database during installation.

## Manual Database Setup

If automatic download fails, you can manually set up the offline databases:

### Option 1: IPinfo Lite (Free)
```bash
# Create directory
mkdir -p ipinfo_data
cd ipinfo_data

# Download free country database
curl -o country.mmdb.gz "https://ipinfo.io/data/free/country.mmdb.gz?token=free"
gunzip country.mmdb.gz
mv country.mmdb ipinfo_lite.mmdb

cd ..
```

### Option 2: Full IPinfo Databases (Requires Token)
If you have an IPinfo account with token:

1. **Visit:** https://ipinfo.io/account/data-downloads
2. **Download:** Country, City, or ASN databases
3. **Extract to:** `ipinfo_data/` directory
4. **Rename as needed:**
   - `country.mmdb` → Keep as is
   - `city.mmdb` → Keep as is  
   - `asn.mmdb` → Keep as is

## Database Files Structure
```
ipinfo_data/
├── ipinfo_lite.mmdb    # Free country data (auto-downloaded)
├── country.mmdb        # Enhanced country data (optional)
├── city.mmdb          # City-level data (optional)
└── asn.mmdb           # ISP/Organization data (optional)
```

## License Compliance

### IPinfo Lite Database:
- ✅ **Free for any use**
- ✅ **Downloaded directly from IPinfo.io**
- ✅ **User accepts IPinfo's terms directly**
- ✅ **No redistribution concerns**

### Commercial Databases:
- Requires paid IPinfo account
- Downloaded by user with their credentials
- Full compliance with IPinfo terms

## Verification

Check if databases are loaded:
```bash
# Start the application
./start_web_gui_linux.sh

# Look for these messages:
# ✅ MMDB database loaded: ipinfo_data/ipinfo_lite.mmdb
# ✅ Loaded IPinfo Lite database: ipinfo_data/ipinfo_lite.mmdb
```

## Fallback Strategy

The system works in this order:
1. **Local SQLite Database** (your analyzed IPs)
2. **Memory Cache** (recent lookups)
3. **Offline MMDB Files** (downloaded databases)
4. **IPinfo API** (if token provided)
5. **Basic Classification** (private/public IP detection)

Even without offline databases, the system provides basic IP analysis and can use the IPinfo API when a token is configured.

## Troubleshooting

### Database Download Failed
```bash
# Check internet connection
curl -I https://ipinfo.io/

# Manual download
wget https://ipinfo.io/data/free/country.mmdb.gz?token=free -O country.mmdb.gz
```

### Database Not Loading
```bash
# Check file permissions
ls -la ipinfo_data/

# Verify file integrity
file ipinfo_data/*.mmdb
```

## API Token Enhancement (Optional)

For enhanced city/ISP data:
1. Get free token: https://ipinfo.io/signup
2. Configure in web interface or set: `export IPINFO_TOKEN="your_token"`
3. Enjoy city-level accuracy and ISP information!
