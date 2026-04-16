#!/bin/bash

echo "🔍 Checking Railway deployment status..."
echo ""

# Get latest logs
echo "📋 Latest Railway logs (last 5 lines):"
railway logs --tail 5

echo ""
echo "---"
echo ""
echo "✅ If you see 'Module c21_property_listing loaded' with property_image_views.xml, NEW code is deployed!"
echo "❌ If you DON'T see property_image_views.xml, still waiting for new deployment..."
echo ""
echo "🔗 Check build status: https://railway.com/project/357d3bd3-d006-46ad-aa91-7ac88b3fb7c1"
