"""
One-shot deploy script: downloads c21-odoo-addons from GitHub and installs
the c21_property_listing module into /var/lib/odoo/addons/
Run inside the Railway container: python3 /tmp/deploy.py
"""
import urllib.request
import tarfile
import os
import shutil

REPO_URL = "https://github.com/lojul/c21-odoo-addons/archive/refs/heads/main.tar.gz"
TMP_ARCHIVE = "/tmp/c21_addons.tgz"
TMP_EXTRACT = "/tmp/c21_addons_extract"
MODULE_NAME = "c21_property_listing"
DEST_DIR = "/var/lib/odoo/addons/" + MODULE_NAME

print("Downloading repo archive...")
urllib.request.urlretrieve(REPO_URL, TMP_ARCHIVE)
print("Download complete:", os.path.getsize(TMP_ARCHIVE), "bytes")

print("Extracting...")
if os.path.exists(TMP_EXTRACT):
    shutil.rmtree(TMP_EXTRACT)
with tarfile.open(TMP_ARCHIVE) as t:
    t.extractall(TMP_EXTRACT)

# The archive extracts to a folder like c21-odoo-addons-main/
extracted_top = os.path.join(TMP_EXTRACT, "c21-odoo-addons-main")
src = os.path.join(extracted_top, MODULE_NAME)

if not os.path.isdir(src):
    raise FileNotFoundError("Module not found at: " + src)

print("Installing to", DEST_DIR)
if os.path.exists(DEST_DIR):
    shutil.rmtree(DEST_DIR)
shutil.copytree(src, DEST_DIR)

print("Done! Files installed:")
for f in sorted(os.listdir(DEST_DIR)):
    print(" ", f)
