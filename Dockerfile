FROM odoo:19.0

# Copy custom addons to Odoo's extra addons directory
COPY ./c21_property_listing /mnt/extra-addons/c21_property_listing
COPY ./c21_admin_dashboard /mnt/extra-addons/c21_admin_dashboard
COPY --chown=root:root ./scripts/sync_addons_and_start.sh /usr/local/bin/sync_addons_and_start.sh
COPY --chown=root:root ./scripts/bulk_image_import.py /usr/local/bin/bulk_image_import.py

# Copy Odoo configuration for performance
COPY --chown=odoo:odoo ./config/odoo.conf /etc/odoo/odoo.conf

# Set permissions
USER root
RUN chown -R odoo:odoo /mnt/extra-addons \
    && chmod +x /usr/local/bin/sync_addons_and_start.sh \
    && chmod +x /usr/local/bin/bulk_image_import.py \
    && mkdir -p /var/lib/odoo/addons/19.0 \
    && chown -R odoo:odoo /var/lib/odoo

# Run as root to handle volume permissions, script will call Odoo
ENTRYPOINT ["/usr/local/bin/sync_addons_and_start.sh"]
CMD []
