#!/bin/bash
# This script updates c21 modules in the Railway volume
# Run with: railway shell

set -e

echo "🔄 Updating C21 modules from GitHub..."
echo ""

# Download latest from GitHub
echo "📥 Downloading latest code..."
cd /tmp
curl -sL https://github.com/lojul/c21-odoo-addons/archive/refs/heads/main.tar.gz -o c21.tar.gz

# Extract
echo "📦 Extracting..."
tar -xzf c21.tar.gz

# Backup current module
echo "💾 Creating backup..."
if [ -d "/var/lib/odoo/addons/19.0/c21_property_listing" ]; then
    cp -r /var/lib/odoo/addons/19.0/c21_property_listing /tmp/c21_backup_$(date +%Y%m%d_%H%M%S)
fi

# Update c21_property_listing
echo "📁 Updating c21_property_listing..."
rm -rf /var/lib/odoo/addons/19.0/c21_property_listing
cp -r /tmp/c21-odoo-addons-main/c21_property_listing /var/lib/odoo/addons/19.0/

# Update c21_admin_dashboard if exists
if [ -d "/tmp/c21-odoo-addons-main/c21_admin_dashboard" ]; then
    echo "📁 Updating c21_admin_dashboard..."
    rm -rf /var/lib/odoo/addons/19.0/c21_admin_dashboard
    cp -r /tmp/c21-odoo-addons-main/c21_admin_dashboard /var/lib/odoo/addons/19.0/
fi

# Verify
echo ""
echo "✅ Update complete!"
echo ""
echo "📋 Files in c21_property_listing/views/:"
ls -1 /var/lib/odoo/addons/19.0/c21_property_listing/views/

echo ""
echo "🔍 Checking for property_image_views.xml..."
if [ -f "/var/lib/odoo/addons/19.0/c21_property_listing/views/property_image_views.xml" ]; then
    echo "✅ property_image_views.xml EXISTS!"
    echo "   Size: $(wc -c < /var/lib/odoo/addons/19.0/c21_property_listing/views/property_image_views.xml) bytes"
else
    echo "❌ property_image_views.xml NOT FOUND!"
fi

echo ""
echo "📝 Next steps:"
echo "1. Exit this shell (type 'exit')"
echo "2. Restart Odoo service in Railway dashboard"
echo "3. In Odoo: Apps → Update Apps List → Search 'C21' → Upgrade"

# Cleanup
rm -rf /tmp/c21.tar.gz /tmp/c21-odoo-addons-main
