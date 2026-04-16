FROM odoo:19.0

# Copy custom addons to Odoo's extra addons directory
COPY ./c21_property_listing /mnt/extra-addons/c21_property_listing
COPY ./c21_admin_dashboard /mnt/extra-addons/c21_admin_dashboard

# Set permissions
USER root
RUN chown -R odoo:odoo /mnt/extra-addons
USER odoo

# The ODOO_ADDONS_PATH should be set via Railway environment variable:
# ODOO_ADDONS_PATH=/mnt/extra-addons,/usr/lib/python3/dist-packages/odoo/addons
