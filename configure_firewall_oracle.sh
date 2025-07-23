#!/bin/bash
# Firewall configuration for Oracle Linux 10
# Opens necessary ports for Nimble Streamer Log Analyzer

echo "🔥 Configuring firewall for Nimble Streamer Log Analyzer"
echo "========================================================="

# Check if firewalld is running
if systemctl is-active --quiet firewalld; then
    echo "✅ Firewalld is running"
    
    # Open port 8050 for HTTP traffic
    echo "🔓 Opening port 8050..."
    sudo firewall-cmd --permanent --add-port=8050/tcp
    
    # Open ports 8051-8060 as backup
    echo "🔓 Opening backup ports 8051-8060..."
    sudo firewall-cmd --permanent --add-port=8051-8060/tcp
    
    # Reload firewall
    echo "🔄 Reloading firewall..."
    sudo firewall-cmd --reload
    
    # Show current rules
    echo "📋 Current firewall rules:"
    sudo firewall-cmd --list-ports
    
    echo "✅ Firewall configured successfully!"
    
elif systemctl is-active --quiet iptables; then
    echo "✅ iptables is running"
    
    # Add iptables rules
    echo "🔓 Adding iptables rules..."
    sudo iptables -A INPUT -p tcp --dport 8050 -j ACCEPT
    sudo iptables -A INPUT -p tcp --dport 8051:8060 -j ACCEPT
    
    # Save iptables rules (Oracle Linux specific)
    if command -v iptables-save >/dev/null 2>&1; then
        sudo iptables-save > /etc/sysconfig/iptables
        echo "✅ iptables rules saved!"
    fi
    
else
    echo "⚠️ No active firewall detected"
    echo "Manual configuration may be required"
fi

echo ""
echo "🎯 Network Access Information:"
echo "================================"
echo "Local Access:    http://localhost:8050"
echo "Network Access:  http://$(hostname -I | awk '{print $1}'):8050"
echo ""
echo "🔒 Security Note:"
echo "The application is now accessible from external networks."
echo "Consider using a reverse proxy (nginx) for production use."
