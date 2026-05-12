# Custom Odoo image with Pillow and Chinese fonts
FROM odoo:19.0

USER root

# Install Pillow dependencies and Chinese fonts
RUN apt-get update && apt-get install -y --no-install-recommends \
    fonts-noto-cjk \
    fonts-noto-cjk-extra \
    libjpeg-dev \
    libpng-dev \
    libfreetype6-dev \
    && pip3 install --no-cache-dir --break-system-packages Pillow==10.4.0 feedparser==6.0.11 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy custom addons (optional - can also use volume mount)
# COPY ./addons /mnt/extra-addons

USER odoo
