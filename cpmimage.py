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
#          the overall aesthetic of the application. COMPLETED
#        * Text Color and Background Color: Provide options to set the text color and background color 
#          of the listbox items. This allows users to personalize the appearance of the listbox to their 
#          preferences or match the theme of the application. COMPLETED
#        * Selection Colors: Allow users to specify the colors used to highlight selected items in the 
#          listbox. This can help improve visibility and distinguish selected items from others. COMPLETED
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
import tkinter.font as tkFont
from tkinter import filedialog, messagebox, simpledialog, colorchooser, ttk
from tkinter.simpledialog import askstring
import subprocess
import re
import sys
import os
import argparse

initial_text_color = 'black'
initial_bg_color = 'white'
initial_font = ('Mono', 12, 'normal')
initial_border_width = 2
initial_padding_x = 5
initial_padding_y = 5
initial_width=50
initial_height=30

parser = argparse.ArgumentParser(description='CPMImage application')
parser.add_argument('-f', '--format', help='Specify the disk format', default='ibm-3740')
parser.add_argument('filename', nargs='?', help='Filename of the image to open', default='')
args = parser.parse_args()

imgformat = args.format
current_filename = args.filename if args.filename else ''
debug_mode = True

last_used_directory = os.getcwd()                                               # Initialize last used directory to the current working directory

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

def choose_text_color():
    color_code = colorchooser.askcolor(title="Choose text color")[1]
    if color_code:
        listbox.config(fg=color_code)

def update_text_color():
    global initial_text_color
    color_code = colorchooser.askcolor(title="Choose text color")[1]
    if color_code:
        initial_text_color = color_code
        listbox.config(fg=initial_text_color)

def choose_bg_color():
    color_code = colorchooser.askcolor(title="Choose background color")[1]
    if color_code:
        listbox.config(bg=color_code)

def update_bg_color():
    global initial_bg_color
    color_code = colorchooser.askcolor(title="Choose background color")[1]
    if color_code:
        initial_bg_color = color_code
        listbox.config(bg=initial_bg_color)

def choose_select_bg_color():
    color_code = colorchooser.askcolor(title="Choose selection background color")[1]
    if color_code:
        listbox.config(selectbackground=color_code)

def choose_select_fg_color():
    color_code = colorchooser.askcolor(title="Choose selection text color")[1]
    if color_code:
        listbox.config(selectforeground=color_code)

def update_padding():
    global initial_padding_x, initial_padding_y
    new_padx = simpledialog.askinteger("Padding", "Enter horizontal padding (pixels):", minvalue=0)
    new_pady = simpledialog.askinteger("Padding", "Enter vertical padding (pixels):", minvalue=0)
    if new_padx is not None and new_pady is not None:
        initial_padding_x = new_padx
        initial_padding_y = new_pady
        listbox.pack_configure(padx=initial_padding_x, pady=initial_padding_y)

def customize_border():
    new_border_width = simpledialog.askinteger("Border Width", "Enter border width (pixels):", minvalue=0)
    new_highlight_thickness = simpledialog.askinteger("Highlight Thickness", "Enter highlight thickness (pixels):", minvalue=0)
    if new_border_width is not None:                                            # Check if the user made a selection
        listbox.config(borderwidth=new_border_width, highlightthickness=new_highlight_thickness)

def customize_padding():
    new_padx = simpledialog.askinteger("Padding", "Enter horizontal padding (pixels):", minvalue=0)
    new_pady = simpledialog.askinteger("Padding", "Enter vertical padding (pixels):", minvalue=0)
    if new_padx is not None and new_pady is not None:                           # Check if the user made a selection
        listbox.config(padx=new_padx, pady=new_pady)

def update_listbox_font():                                                      # Prompt the user for font, size, and weight
    font_spec = simpledialog.askstring("Font", "Enter font (e.g., 'Arial 12 bold'):")
    
    if font_spec:                                                               # Check if the user provided a value
        try:                                                                    # Create a font object with the user's specifications
            new_font = tkFont.Font(font=font_spec)
            listbox.config(font=new_font)
        except tk.TclError:
            tk.messagebox.showerror("Error", "Invalid font specification.")

def open_image():
    global current_filename, last_used_directory                                # Ensure we're modifying the global variables
    filetypes = [('CP/M Image', '*.img'), ('CP/M Image', '.IMG'), ('CP/M Image', '.ima'), ('CP/M Image', '.IMA'),
                 ('CP/M Image', '.DSK'), ('CP/M Image', '.dsk'), ('All Files', '*')]
    filename = askopenfilename_case_insensitive(filetypes=filetypes, initialdir=last_used_directory)

    if filename:
        current_filename = filename                                             # Update the global variable
        last_used_directory = os.path.dirname(filename)                         # Update the last used directory
        populate_listbox(current_filename)
        update_window_title()                                                   # Update the window title with the new filename
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
            parsed_lines.append(line.strip())                                   # Keep header, footer, and empty lines as is
        else:
            parsed_lines.append(line[:20])                                      # Display first 20 characters of the line as-is
    return parsed_lines

def parse_footer(footer_line):                                                  # Split the footer line by spaces
    parts = footer_line.strip().split()
    
    if len(parts) >= 5:                                                         # Ensure the minimum required parts are available for parsing
        total_occupied = parse_size(parts[3])
        total_free = 0                                                          # Default value for total free space
        total_space = 0                                                         # Default value for total space

        if "Free." in parts:                                                    # Check if "Free." is present in the footer line
            free_index = parts.index("Free.")                                   # If "Free." is present, find its index
            if free_index >= 1:                                                 # Ensure "Free." is not the first element
                total_free = parse_size(parts[free_index - 1])                  # Extract the total free space (located before "Free.")
                if free_index >= 2:                                             # Extract the total space (located before total free space)
                    total_space = parse_size(parts[free_index - 2])
        
        return f"{parts[0]} Files {total_occupied} / {total_space + total_free}K" # Return the formatted string
    else:
        return "Footer line format error"

def parse_size(size_str):                                                       # Removing non-numeric characters and converting to integer
    numeric_part = ''.join(filter(str.isdigit, size_str))
    return int(numeric_part) if numeric_part.isdigit() else 0

def format_size(size):                                                          # Formatting size in KiloBytes
    return f"{size}"

def on_listbox_select(event):                                                   # Triggered when an item in the listbox is clicked
    unselectable_indices = [0, 1, listbox.size() - 2, listbox.size() - 1]       # Indices of items that should not be selectable
    for index in unselectable_indices:                                          
        listbox.selection_clear(index)                                          # Clear selection

def treeview_sort_column(tv, col, reverse):
    l = [(tv.set(k, col), k) for k in tv.get_children('')]
    l.sort(reverse=reverse)

    for index, (val, k) in enumerate(l):                                        # Rearrange items in sorted positions
        tv.move(k, '', index)

    tv.heading(col, command=lambda: treeview_sort_column(tv, col, not reverse)) # Reverse sort next time

def populate_listbox(filename):                                                 # New function to use treeview
    tree.delete(*tree.get_children())                                           # clear any existing data

    usernum = 0                                                                 # Initialize user number
    total_files = 0                                                             # Initialize total_files
    total_size = 0                                                              # Initialize total_size
    free_space = 0                                                              # Initialize free_space

    try:                                                                        # Execute cpmls command and split output into lines
        cmd=['cpmls', '-D', '-f', imgformat, filename]
        debug_print("Executing command:", ' '.join(cmd))
        output = subprocess.check_output(cmd, universal_newlines=True)
        for line in output.splitlines():
            if line.strip() == "" or "Name    Bytes" in line or "------" in line or "No files found" in line:
                continue                                                        # Skip blank and specific header lines
            elif line.startswith("User"):
                usernum = int(line.split()[1][:-1])                             # Extract and update usernum
            elif "Files occupying" in line:
                parts = line.split()
                if len(parts) >= 6:                                             # Ensure there are enough parts in the line
                    total_files = parts[0]
                    total_size = parts[3].rstrip("K")
                    free_space = parts[4].rstrip("K")
                    debug_print(total_files, " Files occupying ", total_size, "K, ", free_space, "K Free.")
            else:                                                               # Extract filename and size from the line (adjust slicing/indexing as needed based on your output format)
                filename = line[:12].replace(' ', '')                           # Example: Adjust based on actual data layout in 'line' 
                size = line[13:20].rstrip('K').strip()                          # Example: Adjust based on actual data layout in 'line'
                tree.insert('', 'end', values=(usernum, filename, size))        # Insert a new row into the Treeview
        footer_label.config(text=f"Files: {total_files}, Total Size: {total_size}K, Free Space: {free_space}K") # Update the footer label
        
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Failed to load file list: {e}")

def on_select(event):
    widget = event.widget
    selected_indices = widget.curselection()

    unselectable_indices = [0, 1]                                               # Define unselectable indices for header lines

    last_index = widget.size() - 1                                              # Calculate and add indices for footer lines
    unselectable_indices.extend([last_index - 1, last_index])

    for index in selected_indices:                                              # Deselect if any unselectable indices are selected
        if index in unselectable_indices:
            widget.selection_clear(index)

#def extract_items():
#    global current_filename
#    if not current_filename:
#        messagebox.showinfo("No Image Open", "Please open an image file before attempting to extract files.")
#        return

#    selected_items = listbox.curselection()
#    if not selected_items:
#        messagebox.showinfo("No Items Selected", "Please select one or more items to extract.")
#        return

#    destination_directory = "./extracted_files/"
#    if not os.path.exists(destination_directory):
#        os.makedirs(destination_directory)

#    for idx in selected_items:
#        item = listbox.get(idx)
#        usernum = item[:2].strip()
#        original_filename = item[3:15].replace(" ", "")
#        filename = original_filename                                            # Start with the original filename

#        dest = os.path.join(destination_directory, filename)
#        while os.path.exists(dest):
                                                                                # Prompt for a new filename due to duplicate
#            new_filename = askstring("File Exists", f"The file {filename} already exists. Enter a new filename:")
#            if new_filename is None or new_filename.strip() == "":
#                messagebox.showinfo("Extraction Cancelled", "Extraction cancelled for the current item.")
#                break                                                           # Exit the loop and skip to the next selected item

                                                                                # Update filename and dest with the new name provided by the user
#            filename = new_filename.strip()                                     # Ensure we strip any leading/trailing spaces
#            dest = os.path.join(destination_directory, filename)

#        if not os.path.exists(dest):
#            try:                                                                # Proceed with extraction only if the destination does not exist (i.e., user provided a new name)
#                src = f"{usernum}:{original_filename}"                          # src still uses the original filename from the listbox
#                subprocess.run(['cpmcp', '-f', imgformat, current_filename, src, dest], check=True)
#            except subprocess.CalledProcessError as e:
#                messagebox.showerror("Extraction Error", f"Failed to extract '{original_filename}': {e}")
#                continue

#    listbox.selection_clear(0, tk.END)
#    messagebox.showinfo("Extraction Complete", "Selected files have been extracted to " + destination_directory)

def extract_items():
    global current_filename
    if not current_filename:
        messagebox.showinfo("No Image Open", "Please open an image file before attempting to extract files.")
        return

    selected_items = tree.selection()  # Use .selection() for Treeview
    if not selected_items:
        messagebox.showinfo("No Items Selected", "Please select one or more items to extract.")
        return

    # Prompt the user for the extraction directory, defaulting to the current working directory
    destination_directory = filedialog.askdirectory(initialdir=os.getcwd(), title="Select Extraction Directory")
    if not destination_directory:  # If the user cancels the dialog
        messagebox.showinfo("Extraction Cancelled", "Extraction cancelled by user.")
        return

    for item_id in selected_items:
        item_values = tree.item(item_id, 'values')
        usernum, filename, _ = item_values                                      # Assuming the 'values' are in the order (usernum, filename, size)
        filename = filename.replace(" ", "")                                    # Remove internal spaces from filename

        src_path = f"{usernum}:{filename}"  # Construct the source path
        dest_path = os.path.join(destination_directory, filename)

        # Execute the cpmcp command
        try:
            cmd = ['cpmcp', '-f', imgformat, current_filename, src_path, dest_path]
            debug_print("Executing command:", ' '.join(cmd))                    # Print the command for troubleshooting
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Extraction Error", f"Failed to extract '{filename}': {e}")

    messagebox.showinfo("Extraction Complete", "Selected files have been extracted.")

#def delete_items():
#    global current_filename
#    if not current_filename:
#        return

#    selected_items = listbox.curselection()
#    if not selected_items:
#        messagebox.showinfo("No Items Selected", "Please select one or more items to delete.")
#        return

#    if not confirm_delete():
#        return

#    try:
#        for idx in selected_items:
#            item = listbox.get(idx)
#            subprocess.run(['cpmrm', '-f', imgformat, current_filename, item], capture_output=True, text=True)
#            refresh_listbox()                                                   # Refresh listbox after deletion
#    except subprocess.CalledProcessError as e:
#        messagebox.showerror("Error", f"Failed to delete items: {e}")

def delete_items():
    global current_filename
    if not current_filename:
        messagebox.showinfo("No Image Open", "Please open an image file before attempting to delete files.")
        return

    selected_items = tree.selection()  # Get selected items' IDs
    if not selected_items:
        messagebox.showinfo("No Items Selected", "Please select one or more items to delete.")
        return

    if not confirm_delete():  # Confirm deletion from the user
        return

    try:
        for item_id in selected_items:
            item_values = tree.item(item_id, 'values')
            usernum, filename, _ = item_values  # Assuming the 'values' are in the order (usernum, filename, size)
            filename = filename.replace(" ", "")  # Adjust as necessary based on how filenames are stored

            # Construct the source path for deletion
            src_path = f"{usernum}:{filename}"
            cmd = ['cpmrm', '-f', imgformat, current_filename, src_path]
            debug_print("Executing command:", ' '.join(cmd))  # Optional: Print the command for troubleshooting
            subprocess.run(cmd, check=True)
            
            # Remove the item from the treeview
            tree.delete(item_id)

    except subprocess.CalledProcessError as e:
        messagebox.showerror("Deletion Error", f"Failed to delete the selected items: {e}")

    # Optionally, refresh the treeview to reflect the current state
    refresh_listbox()

def prompt_user_number():
    while True:
        usernum = simpledialog.askstring("User Number", "Enter the user number (0-15):")
        if usernum is None:  # User cancelled the dialog
            return None
        try:
            usernum = int(usernum)
            if 0 <= usernum <= 15:
                return usernum
            else:
                messagebox.showerror("Error", "User number must be between 0 and 15.")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid integer.")

def validate_and_correct_filename(initial_filename):
    
    restricted_chars = '<>,;:=?*[]%|()\\'                                        # Define CP/M restricted characters and 8.3 filename pattern
    pattern = re.compile("^[^.]{1,8}(.[^.]*)?$")  # Basic 8.3 pattern check
    
    filename = initial_filename
    while True:
        if any(char in restricted_chars for char in filename) or not pattern.match(filename):
            messagebox.showerror("Invalid Filename", "Filename must comply with 8.3 format and not contain restricted characters.")
            filename = simpledialog.askstring("Correct Filename", "Enter a new filename:", initialvalue=filename)
            if filename is None:  # User cancelled
                return None
        else:
            return filename

def import_files():
    global current_filename
    if not current_filename:
        messagebox.showinfo("No Image Open", "Please open an image file before importing.")
        return
    
    # Prompt for the file to import
    filename_to_import = filedialog.askopenfilename(title="Select file to import")
    if not filename_to_import:
        return  # User cancelled the dialog

    basename = os.path.basename(filename_to_import)
    corrected_filename = validate_and_correct_filename(basename.replace(" ", "_"))  # Initial correction for spaces
    if corrected_filename is None:
        return  # User cancelled or failed to provide a valid filename
    
    usernum = prompt_user_number()
    if usernum is None:
        return  # User cancelled the usernum dialog

    # Execute the cpmcp command
    try:
        cmd = ['cpmcp', '-f', imgformat, current_filename, filename_to_import, f'{usernum}:{corrected_filename}']
        debug_print("Executing command:", ' '.join(cmd))                        # Print the command for troubleshooting
        result = subprocess.run(cmd, check=True, text=True, capture_output=True)
        if "device full" in result.stderr.lower():
            messagebox.showerror("Insufficient room", "The CP/M device is full.")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Import Error", f"Failed to import '{corrected_filename}': {e}")
    refresh_listbox()
    
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
    try:                                                                        # Look for the diskdefs file in multiple locations
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
        else:                                                                   # If diskdefs file not found, use this predefined list (from the default diskdefs)
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

        submenu_dict = {                                                        # Dictionary to store submenus
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

            for submenu_label, submenu in submenu_dict.items():                 # Find the appropriate submenu for the diskdef
                if first_letter in submenu_label:
                    submenu.add_radiobutton(label=diskdef, command=lambda df=diskdef: format_changed(df), variable=imgformat)
                    break
        
        for submenu_label, submenu in submenu_dict.items():                     # Add submenus to the Format menu
            format_menu.add_cascade(label=submenu_label, menu=submenu)

    except Exception as e:
        messagebox.showerror("Error", f"Failed to retrieve diskdefs: {e}")

def update_footer(file_count, total_size, free_space):
    footer_text = f"Files: {file_count}, Total Size: {total_size}K, Free Space: {free_space}K"
    footer_label.config(text=footer_text)

def select_all(event=None):
    items = tree.get_children()                                                 # Get a list of all item IDs in the Treeview
    tree.selection_set(items)                                                   # Select all items

def create_new_image():
    default_filename = "NEW.IMG"
    filetypes = [('CP/M Image', '*.IMG'), ('All files', '*')]
    filename = filedialog.asksaveasfilename(initialfile=default_filename, filetypes=filetypes, defaultextension='.IMG')

    if filename:
        try:
            subprocess.run(['mkfs.cpm', '-f', imgformat, filename])
            messagebox.showinfo("New Image Created", f"New image '{filename}' created successfully.")
            open_image(filename)                                                # Open the newly created image
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create new image: {e}")

# Define the Main Window

root = tk.Tk()
root.title("CPMImage")
root.resizable(True, True)
root.geometry("400x400")
root.bind_all("<q>",         lambda event: on_close())
root.bind_all("<Control-q>", lambda event: on_close())
root.bind_all("<o>",         lambda event: open_image())
root.bind_all("<Control-o>", lambda event: open_image())
root.bind_all("<w>",         lambda event: close_image())
root.bind_all("<Control-w>", lambda event: close_image())
root.bind_all("<e>",         lambda event: extract_items())
root.bind_all("<Control-e>", lambda event: extract_items())
root.bind_all("<i>",         lambda event: import_files())
root.bind_all("<Control-i>", lambda event: import_files())
root.bind_all("<F5>",        lambda event: populate_listbox(current_filename))
root.bind_all("<r>",         lambda event: populate_listbox(current_filename))
root.protocol("WM_DELETE_WINDOW", on_close)

menubar = tk.Menu(root)
root.config(menu=menubar)

# Define the main menu line

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

settings_menu = tk.Menu(menubar, tearoff=0)
settings_menu.add_command(label="Text Color...", command=choose_text_color)
settings_menu.add_command(label="Background Color...", command=choose_bg_color)
settings_menu.add_command(label="Font...", command=update_listbox_font)
settings_menu.add_command(label="Selection Background Color...", command=choose_select_bg_color)
settings_menu.add_command(label="Selection Text Color...", command=choose_select_fg_color)
settings_menu.add_command(label="Customize Border...", command=customize_border)
settings_menu.add_command(label="Customize Padding...", command=customize_padding)
settings_menu.add_separator()
settings_menu.add_checkbutton(label="Debug Mode", command=toggle_debug_mode)    # Keep the toggle for debug mode if needed
menubar.add_cascade(label="Settings", menu=settings_menu)

frame = ttk.Frame(root)
frame.pack(fill='both', expand=True)  # This frame will contain the Treeview

columns = ('un', 'name', 'size')
tree = ttk.Treeview(frame, columns=columns, show='headings', height=15)
tree.pack(fill='both', expand=True)  # Pack the Treeview widget once
tree.heading('un', text='U#')
tree.heading('name', text='Name')
tree.heading('size', text='Size (K)')
tree.column('un', width=30, anchor='center')
tree.column('name', width=150, anchor='w')
tree.column('size', width=100, anchor='center')
tree.bind('<Control-a>', select_all)
for col in columns:
    tree.heading(col, text=col.capitalize(), command=lambda _col=col: treeview_sort_column(tree, _col, False))

footer_frame = ttk.Frame(root)
footer_frame.pack(fill=tk.X, side='bottom', expand=False)  # Ensure footer is at the bottom
footer_label = ttk.Label(footer_frame, text="Initializing...", anchor="w")
footer_label.pack(fill=tk.X, padx=5, pady=5)  # Ensure label fills the footer frame


open_file_or_dialog()

root.mainloop()
