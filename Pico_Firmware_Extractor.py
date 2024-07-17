import tkinter as tk
from tkinter import filedialog
import zipfile
import os
import sys
import subprocess
import shutil
import tkinter as tk
from tkinter import filedialog
import pytsk3

script_dir = os.path.dirname(os.path.realpath(sys.argv[0]))
bin_dir = os.path.join(script_dir, "bin")
temp_dir = os.path.join(script_dir, 'temp')
target_dir = os.path.join(script_dir, 'Image')
brotli_dir = os.path.join(bin_dir, "brotli.exe")
sdat2img_dir = os.path.join(bin_dir, "sdat2img.exe")
pne_dir = os.path.join(bin_dir, "Package_Names_Extractor.py")
systrans_dir = os.path.join(temp_dir, "system.transfer.list")
protrans_dir = os.path.join(temp_dir, "product.transfer.list")
ventrans_dir = os.path.join(temp_dir, "vendor.transfer.list")
system_br_file = os.path.join(temp_dir, 'system.new.dat.br')
output_system_file = os.path.join(temp_dir, 'system.new.dat')
product_br_file = os.path.join(temp_dir, 'product.new.dat.br')
output_product_file = os.path.join(temp_dir, 'product.new.dat')
vendor_br_file = os.path.join(temp_dir, 'vendor.new.dat.br')
output_vendor_file = os.path.join(temp_dir, 'vendor.new.dat')
system_ext = os.path.join(temp_dir, "system.ext4")
product_ext = os.path.join(temp_dir, "product.ext4")
vendor_ext = os.path.join(temp_dir, "vendor.ext4")

def extract_zip(zip_file_path, extract_path):
    try:
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            zip_ref.extractall(extract_path)
    except Exception as e:
        print(f'Fehler beim Extrahieren der Dateien: {str(e)}')

def select_zip():
    file_path = filedialog.askopenfilename(filetypes=[('ZIP-Dateien', '*.zip')])
    if file_path:
        os.makedirs(temp_dir, exist_ok=True)
        print("Extracting Firmware...")
        extract_zip(file_path, temp_dir)
    else: 
        sys.exit()

def extract_files(image_path, output_dir):
    # Öffne das Image
    img = pytsk3.Img_Info(image_path)
    fs = pytsk3.FS_Info(img)

    # Durchlaufe alle Dateien und Ordner
    directory = fs.open_dir("/")
    for entry in directory:
        if entry.info.name.name in [b'.', b'..']:
            continue
        extract_file(entry, output_dir)

def extract_file(entry, output_dir):
    file_name = entry.info.name.name.decode('utf-8')
    if entry.info.meta.type == pytsk3.TSK_FS_META_TYPE_REG:
        # Es ist eine Datei
        file_path = os.path.join(output_dir, file_name)
        try:
            with open(file_path, "wb") as output_file:
                file_size = entry.info.meta.size
                offset = 0
                while offset < file_size:
                    available_to_read = min(4096, file_size - offset)
                    try:
                        data = entry.read_random(offset, available_to_read)
                    except:
                        break
                    if not data:
                        break
                    output_file.write(data)
                    offset += len(data)
        except OSError as e:
            print(f"Fehler beim Öffnen der Datei {file_name}: {e}")
    elif entry.info.meta.type == pytsk3.TSK_FS_META_TYPE_DIR:
        # Es ist ein Verzeichnis
        new_dir = os.path.join(output_dir, file_name)
        if not os.path.exists(new_dir):
            os.makedirs(new_dir)
        sub_directory = entry.as_directory()
        for sub_entry in sub_directory:
            if sub_entry.info.name.name in [b'.', b'..']:
                continue
            extract_file(sub_entry, new_dir)

def brotli():
    print("Decompressing system.new.dat.br...")
    subprocess.run([brotli_dir, '--decompress', '--in', system_br_file, '--out', output_system_file], stderr=subprocess.STDOUT, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
    print("Decompressing product.new.dat.br...")
    subprocess.run([brotli_dir, '--decompress', '--in', product_br_file, '--out', output_product_file], stderr=subprocess.STDOUT, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
    print("Decompressing vendor.new.dat.br...")
    subprocess.run([brotli_dir, '--decompress', '--in', vendor_br_file, '--out', output_vendor_file], stderr=subprocess.STDOUT, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
    print("Making system.ext4 image...")
    subprocess.run([sdat2img_dir, systrans_dir, output_system_file, system_ext], stderr=subprocess.STDOUT, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
    print("Making product.ext4 image...")
    subprocess.run([sdat2img_dir, protrans_dir, output_product_file, product_ext], stderr=subprocess.STDOUT, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
    print("Making vendor.ext4 image...")
    subprocess.run([sdat2img_dir, ventrans_dir, output_vendor_file, vendor_ext], stderr=subprocess.STDOUT, text=True, creationflags=subprocess.CREATE_NO_WINDOW)

    target_dir = os.path.join(script_dir, 'Image')

    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    shutil.move(system_ext, os.path.join(script_dir, 'Image', 'system.ext4'))
    shutil.move(product_ext, os.path.join(script_dir, 'Image', 'product.ext4'))
    shutil.move(vendor_ext, os.path.join(script_dir, 'Image', 'vendor.ext4'))

    shutil.rmtree(temp_dir)

def image():
    image_path = os.path.join(script_dir, "image", "system.ext4")
    output_dir = os.path.join(script_dir, "Image")
    print("Extracting system.ext4 image...")
    extract_files(image_path, output_dir)
    image_path = os.path.join(script_dir, "image", "product.ext4")
    output_dir = os.path.join(script_dir, "Image")
    print("Extracting product.ext4 image...")
    extract_files(image_path, output_dir)
    image_path = os.path.join(script_dir, "image", "vendor.ext4")
    output_dir = os.path.join(script_dir, "Image")
    print("Extracting vendor.ext4 image...")
    extract_files(image_path, output_dir)
    sortapks = input("\n\nDo you want to sort the Firmware apks into folders with their package name and delete all other files? [y]es / [n]o\n\nYour choice: ")

    while sortapks.lower() not in ["y", "yes", "n", "no"]:
        print("Invalid input. Please enter '[y]es' or '[n]o'.")
        sortapks = input("Do you want to sort the Firmware apks into folders with their package name and delete all other files? [y]es / [n]o\n\nYour choice: ")

    if sortapks.lower() in ["y", "yes"]:
        apks()
    if sortapks.lower() in ["n", "no"]:
        image_path = os.path.join(script_dir, "image", "system.ext4")
        image_path1 = os.path.join(script_dir, "image", "product.ext4")
        image_path2 = os.path.join(script_dir, "image", "vendor.ext4")
        os.remove(image_path)
        os.remove(image_path1)
        os.remove(image_path2)
        return True

#def image():
#        print("")
#        print("Now extract the .ext4 files into the Image folder")
#        print("")
#        user_input = input("When you are done, press Enter to continue or 'n' to cancel: ")
#        if user_input.strip().lower() == 'n':
#            print("Operation canceled.")
#            shutil.rmtree(target_dir)
#            sys.exit()
#        elif user_input == "":
#            confirmation = input("Are you sure? (Type 'y' to confirm): ")
#            if confirmation.strip().lower() == 'y':
#                print("Operation confirmed. Proceeding...")
#                apks()
#            else:
#                print("Operation canceled.")
#                image()

def apks():
    print("")
    print("Copying all APKs to Firmware folder")
    for root, _, files in os.walk(target_dir):
        for file in files:
            if file.endswith('.apk'):
                firmware_dir = os.path.join(script_dir, 'Firmware')

                if not os.path.exists(firmware_dir):
                    os.makedirs(firmware_dir)

                shutil.move(os.path.join(root, file), os.path.join(firmware_dir, file))

    shutil.rmtree(target_dir)

def sorting():
    print("Sorting APKs to their folders...")
    subprocess.run(['python', pne_dir], stderr=subprocess.STDOUT, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
    print("")
    print("")
    print("")
    print("Firmware APKs are now sorted. Process ended. Press Enter to exit")
    input()

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()

    select_zip()
    brotli()
    process = image()
    if process == True:
        input("Firmware Extracted\nDone")
        exit()
    sorting()
    sys.exit()

    root.mainloop()