#!/bin/bash
# Update c21_property_listing module in Railway volume with latest from GitHub

echo "🔄 Updating c21_property_listing module from GitHub..."

# Download latest code
curl -L https://github.com/lojul/c21-odoo-addons/archive/refs/heads/main.tar.gz -o /tmp/c21.tar.gz

# Extract
cd /tmp
tar -xzf c21.tar.gz

# Copy to Odoo addons directory
echo "📁 Copying files to /var/lib/odoo/addons/19.0/c21_property_listing..."

# Remove old module
rm -rf /var/lib/odoo/addons/19.0/c21_property_listing

# Copy new module
cp -r /tmp/c21-odoo-addons-main/c21_property_listing /var/lib/odoo/addons/19.0/

# Also copy admin dashboard if it exists
if [ -d "/tmp/c21-odoo-addons-main/c21_admin_dashboard" ]; then
    rm -rf /var/lib/odoo/addons/19.0/c21_admin_dashboard
    cp -r /tmp/c21-odoo-addons-main/c21_admin_dashboard /var/lib/odoo/addons/19.0/
fi

# List what was installed
echo ""
echo "✅ Module updated! Files in views folder:"
ls -la /var/lib/odoo/addons/19.0/c21_property_listing/views/

echo ""
echo "🔍 Checking for property_image_views.xml:"
if [ -f "/var/lib/odoo/addons/19.0/c21_property_listing/views/property_image_views.xml" ]; then
    echo "✅ property_image_views.xml EXISTS!"
else
    echo "❌ property_image_views.xml NOT FOUND!"
fi

echo ""
echo "🎉 Update complete! Now:"
echo "1. Go to Odoo → Apps"
echo "2. Update Apps List"
echo "3. Search 'C21'"
echo "4. Click 'Upgrade'"

# Cleanup
rm -rf /tmp/c21.tar.gz /tmp/c21-odoo-addons-main
