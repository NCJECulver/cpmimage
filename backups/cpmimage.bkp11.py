import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import subprocess
import re
import sys
import os
import argparse

parser = argparse.ArgumentParser(description='CPMImage application')
parser.add_argument('-f', '--format', help='Specify the disk format', default='ibm-3740')
parser.add_argument('filename', nargs='?', help='Filename of the image to open', default='')
args = parser.parse_args()

imgformat = args.format
current_filename = args.filename if args.filename else ''
debug_mode = False

def toggle_debug_mode():
    global debug_mode
    debug_mode = not debug_mode
    if debug_mode:
        print("Debug mode enabled")
    else:
        print("Debug mode disabled")

def debug_print(*args):
    if debug_mode:
        print(*args)

def open_file_or_dialog():
    global current_filename
    if current_filename:
        populate_listbox(current_filename)
        update_window_title()
    else:
        filename = open_image()
        if filename:
            current_filename = filename
            update_window_title()

def open_image():
    global current_filename  # Ensure we're modifying the global variable

    filetypes = [('CP/M Image', '.img'),('CP/M Image','.IMG'),('CP/M Image','.ima'),('CP/M Image','.IMA'),('CP/M Image','.DSK'),('CP/M Image','.dsk'),('All Files','*')]
    filename = askopenfilename_case_insensitive(filetypes=filetypes)

    if filename:
        current_filename = filename  # Update the global variable
        populate_listbox(current_filename)
        update_window_title()  # Update the window title with the new filename
        return current_filename

    return None

def close_image():
    global current_filename
    current_filename = ""
    listbox.delete(0, tk.END)
    update_window_title()

def update_window_title():
    global imgformat
    debug_print(f"File '{current_filename}'Format {imgformat}")
    if current_filename:
        disk_format = imgformat.upper()
        root.title(f"CPMImage - {os.path.basename(current_filename)} ({disk_format})")
    else:
        root.title(f"CPMImage - NoFile ({imgformat})")

def populate_listbox(filename):
    listbox.delete(0, tk.END)
    try:
        output = subprocess.check_output(['cpmls', '-f', imgformat, filename], universal_newlines=True)
        lines = output.splitlines()
        i = 0
        while i < len(lines):
            line = lines[i]
            if re.match(r'^\d+:$', line.strip()):
                prefix = line.strip()
                i += 1
                while i < len(lines) and not re.match(r'^\d+:$', lines[i].strip()):
                    listbox.insert(tk.END, prefix + lines[i])
                    i += 1
            else:
                listbox.insert(tk.END, line)
                i += 1
    except subprocess.CalledProcessError as e:
        listbox.insert(tk.END, f"Error: {e}")

def extract_items():
    global current_filename
    if not current_filename:
        return

    selected_items = listbox.curselection()
    if not selected_items:
        messagebox.showinfo("No Items Selected", "Please select one or more items to extract.")
        return

    try:
        for idx in selected_items:
            item = listbox.get(idx)
            user_match = re.match(r'^(\d+):(.*)$', item)
            if user_match:
                usernum, itemname = user_match.group(1), user_match.group(2)
                subprocess.run(['cpmcp', '-f', imgformat, current_filename, f'{item}', itemname])
            else:
                subprocess.run(['cpmcp', '-f', imgformat, current_filename, item, item])
    except subprocess.CalledProcessError as e:
        print(f"Error extracting item '{item}': {e}")

    listbox.selection_clear(0, tk.END)

def delete_items():
    global current_filename
    if not current_filename:
        return

    selected_items = listbox.curselection()
    if not selected_items:
        messagebox.showinfo("No Items Selected", "Please select one or more items to delete.")
        return

    if not confirm_delete():
        return

    try:
        for idx in selected_items:
            item = listbox.get(idx)
            subprocess.run(['cpmrm', '-f', imgformat, current_filename, item], capture_output=True, text=True)
            refresh_listbox()  # Refresh listbox after deletion
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Failed to delete items: {e}")

def import_files():
    global current_filename
    if not current_filename:
        messagebox.showinfo("No Image Open", "Please open an image file before importing.")
        return

    filetypes = [('All files', '*')]
    filenames = filedialog.askopenfilenames(filetypes=filetypes)
    if not filenames:
        return

    target_user = tk.simpledialog.askinteger("Target User Number", "Enter the target user number (0-15):", initialvalue=0, minvalue=0, maxvalue=15)
    if target_user is None:  # Cancel button clicked
        return

    try:
        for filename in filenames:
            result = subprocess.run(['cpmcp', '-f', imgformat, current_filename, f'{filename}', f'{target_user}:{os.path.basename(filename)}'], capture_output=True, text=True)
            if "device full" in result.stdout.lower():
                messagebox.showinfo("Image Full", "The disk image is full. Import aborted.")
                break  # Abort import if image is full
        else:
            messagebox.showinfo("Import Successful", "Files imported successfully.")
            refresh_listbox()  # Refresh listbox after successful import
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Failed to import files: {e}")

def confirm_delete():
    return messagebox.askokcancel("Confirm Delete", "Are you sure you want to delete the selected item(s)?")

def quit_application():
    if confirm_quit():
        root.quit()

def confirm_quit():
    return messagebox.askokcancel("Quit", "Are you sure you want to quit?")

def on_close(event=None):
    if confirm_quit():
        root.quit()

def askopenfilename_case_insensitive(**options):
    if 'filetypes' in options:
        filetypes = options['filetypes']
        new_filetypes = [(ftype[0], ftype[1].lower() + ftype[1][1:]) if ftype[1].startswith('*') else ftype for ftype in filetypes]
        options['filetypes'] = new_filetypes
    return filedialog.askopenfilename(**options)

def format_changed(new_format):
    global imgformat
    imgformat = new_format
    update_window_title()
    print("Format changed to", imgformat)
    refresh_listbox()

def refresh_listbox():
    if current_filename:
        populate_listbox(current_filename)

def populate_format_menu():
    try:
        # Look for the diskdefs file in multiple locations
        locations = ['/usr/local/share/diskdefs', '/usr/share/cpmtools/diskdefs', '/etc/cpmtools/diskdefs']
        diskdefs_file = None
        for location in locations:
            if os.path.isfile(location):
                diskdefs_file = location
                break

        if diskdefs_file:
            diskdef_lines = []
            with open(diskdefs_file, 'r') as file:
                for line in file:
                    line = line.strip()
                    if line.startswith('diskdef'):
                        diskdef = line.split()[1]
                        diskdef_lines.append(diskdef)
        else:
            # If diskdefs file not found, use this predefined list (from the default diskdefs)
            diskdef_lines = [
                '1715',            '17153',                 '4mb-hd',              '8megAltairSIMH',        'all1',
                'alpha',           'altdsdd',               'amp1',                'amp2',                  'amp3',
                'amp4',            'amp5',                  'amp6',                'ampdsdd80',             'ampro400d',
                'ampro800',        'apple-do',              'apple-po',            'attwp',                 'bw12',
                'bw14',            'cf2dd',                 'com8',                'cpcdata',               'cpcsys',
                'cpm86-144feat',   'cpm86-720',             'dec_pro',             'dreamdisk40',           'dreamdisk80',
                'electroglas',     'epsqx10',               'fdd3000',             'fdd3000_2',             'gide-cfa',
                'gide-cfb',        'heassdd8',              'ibm-3740',            'ibm-8ds',               'ibm-8ss',
                '-514ds',          'ibmpc-514ss',           'icl-comet-525ss',     'interak',               'kpii',
                'kpiv',            'lobo2',                 'lobo3',               'mdsad175',              'mdsad350',
                'memotech-type03', 'memotech-type07',       'memotech-type18',     'memotech-type19',       'memotech-type1A',
                'memotech-type1B', 'memotech-type1C',       'memotech-type1D',     'memotech-type1E',       'memotech-type1F',
                'memotech-type43', 'memotech-type47',       'memotech-type4B',     'memotech-type4F',       'memotech-type50',
                'memotech-type51', 'memotech-type51-italy', 'memotech-type51-s2r', 'memotech-type51-s2r64', 'memotech-type52',
                'microbee40',      'mordsdd',               'morsddd',             'myz80',                 'nigdos',
                'nsfd',            'nshd4',                 'nshd8',               'osb1sssd',              'osborne1',
                'osborne4',        'p112',                  'p112-old',            'pc1.2m',                'pcw',
                'pmc101',          'rc75x',                 'rm-dd',               'rm-qd',                 'rm-sd',
                'scp624',          'scp640',                'scp780',              'scp800',                'sdcard',
                'simh',            'svi707',                'td143ssdd8',          'tdos-ds',               'trs5',
                'trse',            'trsf',                  'trsg',                'trsh',                  'trsi',
                'trsj',            'trsk',                  'trsl',                'trsm',                  'trsn',
                'trso',            'trsomsssd',             'trsp',                'trsq',                  'trsr',
                'trss',            'trst',                  'trsu',                'trsv',                  'trsw',
                'v1050',           'z80pack-hd',            'z80pack-hdb',         'z9001',                 'zen7',
                'zen8',            'zen9',                  'zena'
                ]
#            diskdef_lines = [
#                '4mb-hd', 'cpcsys', 'cpcdata', 'cpm86-144feat', 'cpm86-720', 'ibm-3740',
#                'ibm-8ss', 'ibm-8ds', 'icl-comet-525ss', 'kpii', 'kpiv', 'myz80', 'pcw',
#                'osborne1', 'osborne4', 'osb1sssd', 'z80pack-hd', 'z80pack-hdb'
#            ]

        # Dictionary to store submenus
        submenu_dict = {
            "1234567890": tk.Menu(format_menu, tearoff=0),
            "a": tk.Menu(format_menu, tearoff=0),
            "bcd": tk.Menu(format_menu, tearoff=0),
            "efghi": tk.Menu(format_menu, tearoff=0),
            "jkl": tk.Menu(format_menu, tearoff=0),
            "m": tk.Menu(format_menu, tearoff=0),
            "no": tk.Menu(format_menu, tearoff=0),
            "pqr": tk.Menu(format_menu, tearoff=0),
            "s": tk.Menu(format_menu, tearoff=0),
            "t": tk.Menu(format_menu, tearoff=0),
            "uvwxy": tk.Menu(format_menu, tearoff=0),
            "z": tk.Menu(format_menu, tearoff=0)
        }

        for diskdef in diskdef_lines:
            first_letter = diskdef[0].lower()

            # Find the appropriate submenu for the diskdef
            for submenu_label, submenu in submenu_dict.items():
                if first_letter in submenu_label:
                    submenu.add_radiobutton(label=diskdef, command=lambda df=diskdef: format_changed(df), variable=imgformat)
                    break

        # Add submenus to the Format menu
        for submenu_label, submenu in submenu_dict.items():
            format_menu.add_cascade(label=submenu_label, menu=submenu)

    except Exception as e:
        messagebox.showerror("Error", f"Failed to retrieve diskdefs: {e}")

def select_all(event=None):
    listbox.select_set(0, tk.END)

def create_new_image():
    default_filename = "NEW.IMG"
    filetypes = [('CP/M Image', '*.IMG'), ('All files', '*')]
    filename = filedialog.asksaveasfilename(initialfile=default_filename, filetypes=filetypes, defaultextension='.IMG')

    if filename:
        try:
            subprocess.run(['mkfs.cpm', '-f', imgformat, filename])
            messagebox.showinfo("New Image Created", f"New image '{filename}' created successfully.")
            open_image(filename)  # Open the newly created image
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create new image: {e}")

root = tk.Tk()
root.title("CPMImage")
root.resizable(True, True)

menubar = tk.Menu(root)

file_menu = tk.Menu(menubar, tearoff=0)
file_menu.add_command(label="New Image...", command=create_new_image, accelerator="Ctrl+N", underline=0)
file_menu.add_command(label="Open Image...", command=open_image, accelerator="Ctrl+O", underline=0)
file_menu.add_command(label="Close Image", command=close_image, accelerator="Ctrl+W", underline=0)
file_menu.add_separator()
file_menu.add_command(label="Save Image", command=lambda: print("Save Image"), accelerator="Ctrl+S", underline=0)
file_menu.add_command(label="Save Image As...", command=lambda: print("Save Image As"), accelerator="Ctrl+Shift+S", underline=5)
file_menu.add_separator()
file_menu.add_command(label="Quit", command=quit_application, accelerator="Ctrl+Q", underline=0)
menubar.add_cascade(label="File", menu=file_menu, underline=0)

image_menu = tk.Menu(menubar, tearoff=0)
image_menu.add_command(label="Extract", command=extract_items, accelerator="Ctrl+E", underline=0)
image_menu.add_command(label="Delete item(s)", command=delete_items, accelerator="Delete", underline=0)
image_menu.add_command(label="Import...", command=import_files, accelerator="Ctrl+I", underline=0)
image_menu.add_command(label="Refresh", command=lambda: populate_listbox(current_filename), accelerator="F5", underline=0)
menubar.add_cascade(label="Image", menu=image_menu, underline=0)

format_menu = tk.Menu(menubar, tearoff=0)
populate_format_menu()
menubar.add_cascade(label="Format", menu=format_menu, underline=1)

debug_menu = tk.Menu(menubar, tearoff=0)
debug_menu.add_checkbutton(label="Debug Mode", command=toggle_debug_mode)
menubar.add_cascade(label="Debug", menu=debug_menu)

root.bind_all("<Control-q>", lambda event: on_close())
root.bind_all("<Control-o>", lambda event: open_image())
root.bind_all("<Control-w>", lambda event: close_image())
root.bind_all("<Control-e>", lambda event: extract_items())
root.bind_all("<F5>",        lambda event: populate_listbox(current_filename))
root.bind_all("<Control-a>", select_all)

root.protocol("WM_DELETE_WINDOW", on_close)

root.config(menu=menubar)

listbox = tk.Listbox(root, selectmode=tk.MULTIPLE, width=50, height=30)
listbox.pack(fill=tk.BOTH, expand=True)

open_file_or_dialog()

root.mainloop()
