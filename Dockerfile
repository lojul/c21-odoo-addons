FROM odoo:19.0

# Copy custom addons to Odoo's extra addons directory
COPY ./c21_property_listing /mnt/extra-addons/c21_property_listing
COPY ./c21_admin_dashboard /mnt/extra-addons/c21_admin_dashboard
COPY --chown=odoo:odoo ./scripts/sync_addons_and_start.sh /usr/local/bin/sync_addons_and_start.sh
COPY --chown=root:root ./scripts/bulk_image_import.py /usr/local/bin/bulk_image_import.py

# Copy Odoo configuration for performance
COPY --chown=odoo:odoo ./config/odoo.conf /etc/odoo/odoo.conf

# Set permissions
USER root
RUN chown -R odoo:odoo /mnt/extra-addons \
    && chmod +x /usr/local/bin/sync_addons_and_start.sh \
    && chmod +x /usr/local/bin/bulk_image_import.py
USER odoo

ENTRYPOINT ["/usr/local/bin/sync_addons_and_start.sh"]

# The ODOO_ADDONS_PATH should be set via Railway environment variable:
# ODOO_ADDONS_PATH=/mnt/extra-addons,/usr/lib/python3/dist-packages/odoo/addons
