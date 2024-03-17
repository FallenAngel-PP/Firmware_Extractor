import tkinter as tk
from tkinter import filedialog
import zipfile
import os
import subprocess
import tempfile
import shutil
import tkinter as tk
from tkinter import filedialog

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

def brotli():
    print("Decompressing system.new.dat.br...")
    subprocess.run([brotli_dir, '--decompress', '--in', system_br_file, '--out', output_system_file], stderr=subprocess.STDOUT, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
    print("Decompressing product.new.dat.br...")
    subprocess.run([brotli_dir, '--decompress', '--in', product_br_file, '--out', output_product_file], stderr=subprocess.STDOUT, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
    print("Decompressing vendor.new.dat.br...")
    subprocess.run([brotli_dir, '--decompress', '--in', vendor_br_file, '--out', output_vendor_file], stderr=subprocess.STDOUT, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
    print("Making system.ext4 image...")
    subprocess.run([sdat2img_dir, systrans_dir, output_system_file, 'temp\system.ext4'], stderr=subprocess.STDOUT, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
    print("Making product.ext4 image...")
    subprocess.run([sdat2img_dir, protrans_dir, output_product_file, 'temp\product.ext4'], stderr=subprocess.STDOUT, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
    print("Making vendor.ext4 image...")
    subprocess.run([sdat2img_dir, ventrans_dir, output_vendor_file, 'temp/vendor.ext4'], stderr=subprocess.STDOUT, text=True, creationflags=subprocess.CREATE_NO_WINDOW)

    target_dir = os.path.join(script_dir, 'Image')

    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    shutil.move('temp/system.ext4', os.path.join(script_dir, 'Image', 'system.ext4'))
    shutil.move('temp/product.ext4', os.path.join(script_dir, 'Image', 'product.ext4'))
    shutil.move('temp/vendor.ext4', os.path.join(script_dir, 'Image', 'vendor.ext4'))

    # Löschen des temp_dir-Verzeichnisses
    shutil.rmtree(temp_dir)

def image():
        print("")
        print("Now extract the .ext4 files into the Image folder")
        print("")
        user_input = input("When you are done, press Enter to continue or 'n' to cancel: ")

        if user_input.strip().lower() == 'n':
            print("Operation canceled.")
            shutil.rmtree(target_dir)
            sys.exit()
        elif user_input == "":
            confirmation = input("Are you sure? (Type 'y' to confirm): ")
            if confirmation.strip().lower() == 'y':
                print("Operation confirmed. Proceeding...")
                apks()
            else:
                print("Operation canceled.")
                image()

def apks():
    print("")
    print("Copying all APKs to Firmware folder")
    for root, _, files in os.walk(target_dir):
        for file in files:
            if file.endswith('.apk'):
                # Zielverzeichnis für die .apk-Datei
                firmware_dir = os.path.join(script_dir, 'Firmware')

                # Erstellen Sie das Firmware-Verzeichnis, wenn es nicht existiert
                if not os.path.exists(firmware_dir):
                    os.makedirs(firmware_dir)

                # Kopieren der .apk-Datei in das Firmware-Verzeichnis
                shutil.move(os.path.join(root, file), os.path.join(firmware_dir, file))

    # Löschen des Image-Ordners
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
    root.withdraw()  # Verstecke das Hauptfenster

    select_zip()
    brotli()
    image()
    sorting()
    sys.exit()

    root.mainloop()