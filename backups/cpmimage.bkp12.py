# TO DO

# 1. Duplicate Code in open_image and open_file_or_dialog Functions: Both functions perform 
#    similar actions to open an image file. You can refactor the code to avoid duplication 
#    and make it more maintainable. 
#  STATUS: complete

# 2. Handling of Initial Directory in open_image: Currently, the initial directory for opening 
#    an image file is set to the current working directory. You might want to set it to a more 
#    user-friendly location or the last used directory.
#  STATUS: complete

# 3. Error Handling in refresh_listbox Function: If an error occurs while refreshing the listbox, 
#    it should be handled appropriately, such as displaying an error message to the user.
#  STATUS: pending

# 4. Consistency in Error Handling: Ensure consistent error handling throughout the application, 
#    providing informative messages to the user in case of errors.
#  STATUS: pending

# 5. Code Documentation: Consider adding comments to explain complex logic, especially in functions 
#    like populate_listbox, parse_footer, and parse_cpmls_output, to improve code readability and 
#    maintainability.
#  STATUS: pending

# 6. Keyboard Shortcuts: Include keyboard shortcuts for menu items to enhance usability, especially 
#    for actions like opening, closing, and saving images.
#  STATUS: completed ?

# 7. UI Improvements: Depending on your requirements, you may want to consider adding features such as
#      - drag-and-drop support, 
#      - tooltips for menu items, 
#      - additional customization options for the listbox appearance.
#        * Font and Text Size: Allow users to customize the font family, font size, and font weight of 
#          the text displayed in the listbox. This can be useful for improving readability and matching 
#          the overall aesthetic of the application.
#        * Text Color and Background Color: Provide options to set the text color and background color 
#          of the listbox items. This allows users to personalize the appearance of the listbox to their 
#          preferences or match the theme of the application.
#        * Selection Color: Allow users to specify the color used to highlight selected items in the 
#          listbox. This can help improve visibility and distinguish selected items from others.
#        * Scrollbar Style: Customize the style of the scrollbar used with the listbox. Users may prefer 
#          different scrollbar designs such as flat, sunken, raised, or themed scrollbars that match the 
#          operating system's native appearance.
#        * Border and Padding: Provide options to add borders and padding around the listbox to enhance 
#          its visual presentation and separation from other elements in the user interface.
#        * Item Spacing: Allow users to adjust the spacing between items in the listbox. This can help 
#          improve readability and make it easier to differentiate between individual items, especially 
#          when the list contains dense information.
#        * Grid Lines: Offer the option to display grid lines between rows and columns in the listbox. 
#          Grid lines can improve readability by visually separating rows and columns, especially when 
#          dealing with tabular data.
#        * Hover Effects: Implement hover effects for listbox items to provide visual feedback when users 
#          hover their mouse pointer over items. This can include changes in text color, background color, 
#          or adding subtle animations.
#        * Alternate Row Color: Enable users to specify alternate background colors for rows in the listbox. 
#          This can improve readability and make it easier to track across long lists of items.
#        * Item Alignment: Allow users to customize the alignment of text within listbox items, including 
#          options such as left-align, center-align, and right-align. This ensures flexibility in presenting 
#          different types of data in the listbox.

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

last_used_directory = os.getcwd()  # Initialize last used directory to the current working directory

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

def open_image():
    global current_filename, last_used_directory  # Ensure we're modifying the global variables
    filetypes = [('CP/M Image', '*.img'), ('CP/M Image', '.IMG'), ('CP/M Image', '.ima'), ('CP/M Image', '.IMA'),
                 ('CP/M Image', '.DSK'), ('CP/M Image', '.dsk'), ('All Files', '*')]
    filename = askopenfilename_case_insensitive(filetypes=filetypes, initialdir=last_used_directory)

    if filename:
        current_filename = filename  # Update the global variable
        last_used_directory = os.path.dirname(filename)  # Update the last used directory
        populate_listbox(current_filename)
        update_window_title()  # Update the window title with the new filename
        return current_filename
    return None

def open_file_or_dialog():
    global current_filename
    if current_filename:
        populate_listbox(current_filename)
        update_window_title()
    else:
        open_image()

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

def parse_cpmls_output(output):
    lines = output.splitlines()
    parsed_lines = []
    for line in lines:
        if line.startswith("Name") or line.startswith("-") or line.startswith(" ") or line.startswith("  "):
            parsed_lines.append(line.strip())  # Keep header, footer, and empty lines as is
        else:
            parsed_lines.append(line[:20])  # Display first 20 characters of the line as-is
    return parsed_lines

def parse_footer(footer_line):
    # Split the footer line by spaces
    parts = footer_line.strip().split()
    
    # Ensure the minimum required parts are available for parsing
    if len(parts) >= 5:
        total_occupied = parse_size(parts[3])
        total_free = 0  # Default value for total free space
        total_space = 0  # Default value for total space

        # Check if "Free." is present in the footer line
        if "Free." in parts:
            # If "Free." is present, find its index
            free_index = parts.index("Free.")
            if free_index >= 1:  # Ensure "Free." is not the first element
                # Extract the total free space (located before "Free.")
                total_free = parse_size(parts[free_index - 1])
                # Extract the total space (located before total free space)
                if free_index >= 2:
                    total_space = parse_size(parts[free_index - 2])

        # Return the formatted string
        return f"{parts[0]} Files {total_occupied} / {total_space + total_free}K"
    else:
        return "Footer line format error"

def parse_size(size_str):
    # Removing non-numeric characters and converting to integer
    numeric_part = ''.join(filter(str.isdigit, size_str))
    return int(numeric_part) if numeric_part.isdigit() else 0

def format_size(size):
    # Formatting size in KiloBytes
    return f"{size}K"

def populate_listbox(filename):
    listbox.delete(0, tk.END)

    # Manually define the header lines
    header_line_1 = "    Name       Size"
    header_line_2 = "------------ ------"
    listbox.insert(tk.END, header_line_1)
    listbox.insert(tk.END, header_line_2)

    try:
        output = subprocess.check_output(['cpmls', '-D', '-f', imgformat, filename], universal_newlines=True)
        parsed_output = parse_cpmls_output(output)
        for i, line in enumerate(parsed_output[2:]):  # Skip the first two lines
            if i == len(parsed_output) - 4:  # Insert a duplicate of the second header line just above the footer
                listbox.insert(tk.END, header_line_2)
            elif i == len(parsed_output) - 2:  # Display the last line (footer) and mark it as not selectable
                footer_text = parse_footer(line)
                listbox.insert(tk.END, footer_text)
            elif i == len(parsed_output) - 3:  # Display the dashes line above the footer and mark it as not selectable
                dashes_line = header_line_2
                listbox.insert(tk.END, dashes_line)
            else:
                truncated_line = line[:20]  # Truncate to the first 20 characters
                listbox.insert(tk.END, truncated_line)

        # Disable selection for the header and footer lines
        for idx in [0, 1, len(parsed_output) - 1, len(parsed_output) - 2]:
            listbox.selection_set(idx)
            listbox.selection_clear(idx)

    except subprocess.CalledProcessError as e:
        listbox.insert(tk.END, f"Error: {e}")

def on_select(event):
    selected_idx = event.widget.curselection()
    if selected_idx:
        # Get the index of the selected item
        idx = int(selected_idx[0])
        # Get the total number of items in the listbox
        total_items = event.widget.size()
        # Check if the selected item is the header or footer
        if idx < 2 or idx == total_items - 1:
            # If it's the header or footer, deselect the item
            event.widget.selection_clear(idx)
            # Perform any additional actions you want for header or footer
            # For example, display a message indicating that it's not selectable
            print("Header or footer item. Not selectable.")

#   def populate_listbox(filename):
 #   listbox.delete(0, tk.END)
 #   try:
 #       output = subprocess.check_output(['cpmls', '-f', imgformat, filename], universal_newlines=True)
 #       lines = output.splitlines()
 #       i = 0
 #       while i < len(lines):
 #           line = lines[i]
 #           if re.match(r'^\d+:$', line.strip()):
 #               prefix = line.strip()
 #               i += 1
 #               while i < len(lines) and not re.match(r'^\d+:$', lines[i].strip()):
 #                   listbox.insert(tk.END, prefix + lines[i])
 #                   i += 1
 #           else:
 #               listbox.insert(tk.END, line)
 #               i += 1
 #   except subprocess.CalledProcessError as e:
 #       listbox.insert(tk.END, f"Error: {e}")

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

#listbox = tk.Listbox(root, selectmode=tk.MULTIPLE, width=50, height=30)
listbox = tk.Listbox(root, selectmode=tk.MULTIPLE, width=50, height=30, font=("Courier", 12))
listbox.pack(fill=tk.BOTH, expand=True)
listbox.bind('<<ListboxSelect>>', on_select)

open_file_or_dialog()

root.mainloop()
