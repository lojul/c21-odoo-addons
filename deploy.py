"""
One-shot deploy script: downloads c21-odoo-addons from GitHub and installs
all C21 modules into Odoo 19's runtime addons directory.
Run inside the Railway container: python3 /tmp/deploy.py
"""
import urllib.request
import tarfile
import os
import shutil

REPO_URL = "https://github.com/lojul/c21-odoo-addons/archive/refs/heads/main.tar.gz"
TMP_ARCHIVE = "/tmp/c21_addons.tgz"
TMP_EXTRACT = "/tmp/c21_addons_extract"
MODULES = ["c21_property_listing", "c21_admin_dashboard"]
BASE_DEST = "/var/lib/odoo/addons/19.0/"

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

# Install each module
for module_name in MODULES:
    src = os.path.join(extracted_top, module_name)
    dest_dir = os.path.join(BASE_DEST, module_name)

    if not os.path.isdir(src):
        print(f"Warning: Module {module_name} not found at: {src}")
        continue

    print(f"\nInstalling {module_name} to {dest_dir}")
    if os.path.exists(dest_dir):
        shutil.rmtree(dest_dir)
    shutil.copytree(src, dest_dir)

    print(f"✓ {module_name} installed. Files:")
    for f in sorted(os.listdir(dest_dir))[:10]:  # Show first 10 files
        print(f"   - {f}")
    file_count = len(os.listdir(dest_dir))
    if file_count > 10:
        print(f"   ... and {file_count - 10} more files")

print("\n✅ All modules deployed successfully!")
