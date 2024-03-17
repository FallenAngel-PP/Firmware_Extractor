import os
import sys
import subprocess
import json
import shutil
import tkinter as tk
from tkinter import filedialog

from androguard.core.bytecodes.apk import APK

script_dir = os.path.dirname(os.path.realpath(sys.argv[0]))
parent_dir = os.path.dirname(script_dir)
grandparent_dir = os.path.dirname(parent_dir)
folder_path = os.path.join(parent_dir, 'Firmware')
print(parent_dir)
print(grandparent_dir)

def create_package_folders(folder_path, package_names):
    for package_name in package_names:
        package_folder = os.path.join(folder_path, package_name)
        os.makedirs(package_folder, exist_ok=True)

def copy_apk_to_package_folder(apk_path, package_name, folder_path):
    package_folder = os.path.join(folder_path, package_name)
    apk_filename = os.path.basename(apk_path)
    destination_path = os.path.join(package_folder, apk_filename)
    shutil.move(apk_path, destination_path)

def get_apk_package_names(folder_path):
    package_names = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".apk"):
            apk_path = os.path.join(folder_path, filename)
            package_name = get_package_name(apk_path)
            if package_name:
                package_names.append((filename, package_name))
    return package_names

def get_package_name(apk_path):
    try:
        apk = APK(apk_path)
        package_name = apk.get_package()
        return package_name
    except Exception as e:
        print(f"Error extracting package name for {apk_path}: {str(e)}")
        return None

# Ordner auswählen

# APK-Paketnamen extrahieren
package_names = get_apk_package_names(folder_path)

# Ordner für Package-Namen erstellen und APKs kopieren
create_package_folders(folder_path, set(package_name for _, package_name in package_names))

for apk_name, package_name in package_names:
    apk_path = os.path.join(folder_path, apk_name)
    copy_apk_to_package_folder(apk_path, package_name, folder_path)