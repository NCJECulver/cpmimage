# Work in progress
# 2024-03-11
#    -- Added filename translation

# TO DO

# 2. Handling of Initial Directory in open_image: Currently, the initial directory for opening
#    an image file is set to the current working directory. You might want to set it to a more 
#    user-friendly location or the last used directory. COMPLETED

# 3. Error Handling in refresh_listbox Function: If an error occurs while refreshing the listbox, 
#    it should be handled appropriately, such as displaying an error message to the user. PENDING

# 4. Consistency in Error Handling: Ensure consistent error handling throughout the application, 
#    providing informative messages to the user in case of errors. PENDING

# 5. Code Documentation: Consider adding comments to explain complex logic, especially in functions 
#    like populate_listbox, parse_footer, and parse_cpmls_output, to improve code readability and 
#    maintainability. PENDING

# 6. Keyboard Shortcuts:
#      - Include keyboard shortcuts for menu items to enhance usability, especially for actions like
#        opening, closing, and saving images. MOVING TARGET; CURRENTLY BUGGY
#      - Customization - Provide an interface for users to customize keyboard shortcuts. This allows
#        users to tailor the application's controls to their workflow and preferences, enhancing usability.

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
#      - recent files list COMPLETED.
#        * Enhancements: allow user to pin files to the top of the list. PENDING.
#      - customizable themes - customize the application's appearance through themes or skins, which could
#        include options for light/dark modes, color schemes, and font choices.
# 8. File Viewer - text and binary file viewer capability.
#        * Attempt to auto-detect char encoding. COMPLETED.
#        * ASCII and binary modes. COMPLETED.
#        * Allow switching between view modes from within the viewer. COMPLETED.
#        * Search within file. COMPLETED
#        * Go to offset functionality in binary viewer. COMPLETED.
#        * Handling of special file types:
#                - squeezed COMPLETED but buggy; can't handle files with / in name
#                - crunched COMPLETED but untested; uses same code as squeeze so should be ok
#                - LBR, ARK, PENDING
# 9. Image browser - allow user to browse a hex dump of the entire disk image. COMPLETED.
# 10 Drag-and-drop PENDING
# 11 Persistent appplication state - saving the application state between sessions, such as window size and
#    position, last opened directory, and other user preferences. PENDING
# 12 Extraction and importing of system tracks. PENDING
# 13 Rename files - there's no cpmtool for in-place renaming. So what? export/delete/import?
# 14 Change file's user number - see rename above - no direct way to do it with cpmtools, so extract/delete/
#       import to new user?
# 15 Filename translation COMPLETED.

#----------------------------------------------------------------------------------------------------------------------------------
# Python imports                                                                                                                  #
#---------------                                                                                                                  #
import tkinter as tk                                                                                                              #
import tkinter.font as tkFont                                                                                                     #
from tkinter import filedialog, messagebox, simpledialog, colorchooser, ttk                                                       #
from tkinter.simpledialog import askstring                                                                                        #
import configparser                                                             # for maintaining a configuration file            #
import subprocess                                                                                                                 #
import re                                                                                                                         #
import sys                                                                                                                        #
import os                                                                                                                         #
import argparse                                                                                                                   #
import tempfile                                                                                                                   #
import chardet                                                                  # Detect char encoding; "pip install chardet"     #
import shutil                                                                   # Python until to move files                      #
import atexit                                                                   # If app is closed or exits unexpectedly.         #
#----------------------------------------------------------------------------------------------------------------------------------
#                                         =================================
#----------------------------------------------------------------------------------------------------------------------------------
# Global Variables                                                                                                                #
#-----------------                                                                                                                #
initial_text_color = 'black'                                                                                                      #
initial_bg_color = 'white'                                                                                                        #
initial_font = ('Mono', 12, 'normal')                                                                                             #
initial_border_width = 2                                                                                                          #
initial_padding_x = 5                                                                                                             #
initial_padding_y = 5                                                                                                             #
initial_width=50                                                                                                                  #
initial_height=30                                                                                                                 #
temp_dir = None                                                                                                                   #
recent_files = []                                                               # Recently opened files; tuplets w fname/imgformat#
parser = argparse.ArgumentParser(description='CPMImage application')                                                              #
parser.add_argument('-f', '--format', help='Specify the disk format', default='ibm-3740')                                         #
parser.add_argument('filename', nargs='?', help='Filename of the image to open', default='')                                      #
args = parser.parse_args()                                                                                                        #
                                                                                                                                  #
imgformat = args.format                                                                                                           #
current_filename = args.filename if args.filename else ''                                                                         #
debug_mode = True                                                                                                                 #
                                                                                                                                  #
last_used_directory = os.getcwd()                                               # Init last used dir to current working dir       #
config_file_path = 'cpmimage.cfg'                                                                                                 #
character_mappings = [                                                          # For translating filenames. E.g., the CP/M file  #
    ('/', '_'),                                                                 # CP/M&NET.$$$ would be exported to CP_M%NET.===  #
    ('&', '%'),                                                                 # on the host. Importing files would be reversed. #
    ('$', '=')                                                                                                                    #
]                                                                                                                                 #
#----------------------------------------------------------------------------------------------------------------------------------
#                                         =================================
#----------------------------------------------------------------------------------------------------------------------------------
# Debug functions                                                                                                                 #
#----------------                                                                                                                 #
def toggle_debug_mode():                                                                                                          #
    global debug_mode                                                                                                             #
    debug_mode = not debug_mode                                                                                                   #
    if debug_mode:                                                                                                                #
        print("Debug mode enabled")                                                                                               #
    else:                                                                                                                         #
        print("Debug mode disabled")                                                                                              #
                                                                                                                                  #
def debug_print(*args):                                                                                                           #
    if debug_mode:                                                                                                                #
        print(*args)                                                                                                              #
#----------------------------------------------------------------------------------------------------------------------------------
#                                         =================================
#----------------------------------------------------------------------------------------------------------------------------------
# UI Customization functions                                                                                                      #
#---------------------------                                                                                                      #
                                                                                                                                  #
def choose_text_color():                                                                                                          #
    color_code = colorchooser.askcolor(title="Choose text color")[1]                                                              #
    if color_code:                                                                                                                #
        listbox.config(fg=color_code)                                                                                             #
                                                                                                                                  #
def update_text_color():                                                                                                          #
    global initial_text_color                                                                                                     #
    color_code = colorchooser.askcolor(title="Choose text color")[1]                                                              #
    if color_code:                                                                                                                #
        initial_text_color = color_code                                                                                           #
        listbox.config(fg=initial_text_color)                                                                                     #
                                                                                                                                  #
def choose_bg_color():                                                                                                            #
    color_code = colorchooser.askcolor(title="Choose background color")[1]                                                        #
    if color_code:                                                                                                                #
        listbox.config(bg=color_code)                                                                                             #
                                                                                                                                  #
def update_bg_color():                                                                                                            #
    global initial_bg_color                                                                                                       #
    color_code = colorchooser.askcolor(title="Choose background color")[1]                                                        #
    if color_code:                                                                                                                #
        initial_bg_color = color_code                                                                                             #
        listbox.config(bg=initial_bg_color)                                                                                       #
                                                                                                                                  #
def choose_select_bg_color():                                                                                                     #
    color_code = colorchooser.askcolor(title="Choose selection background color")[1]                                              #
    if color_code:                                                                                                                #
        listbox.config(selectbackground=color_code)                                                                               #
                                                                                                                                  #
def choose_select_fg_color():                                                                                                     #
    color_code = colorchooser.askcolor(title="Choose selection text color")[1]                                                    #
    if color_code:                                                                                                                #
        listbox.config(selectforeground=color_code)                                                                               #
                                                                                                                                  #
def update_padding():                                                                                                             #
    global initial_padding_x, initial_padding_y                                                                                   #
    new_padx = simpledialog.askinteger("Padding", "Enter horizontal padding (pixels):", minvalue=0)                               #
    new_pady = simpledialog.askinteger("Padding", "Enter vertical padding (pixels):", minvalue=0)                                 #
    if new_padx is not None and new_pady is not None:                                                                             #
        initial_padding_x = new_padx                                                                                              #
        initial_padding_y = new_pady                                                                                              #
        listbox.pack_configure(padx=initial_padding_x, pady=initial_padding_y)                                                    #
                                                                                                                                  #
def customize_border():                                                                                                           #
    new_border_width = simpledialog.askinteger("Border Width", "Enter border width (pixels):", minvalue=0)                        #
    new_highlight_thickness = simpledialog.askinteger("Highlight Thickness", "Enter highlight thickness (pixels):", minvalue=0)   #
    if new_border_width is not None:                                            # Check if the user made a selection              #
        listbox.config(borderwidth=new_border_width, highlightthickness=new_highlight_thickness)                                  #
                                                                                                                                  #
def customize_padding():                                                                                                          #
    new_padx = simpledialog.askinteger("Padding", "Enter horizontal padding (pixels):", minvalue=0)                               #
    new_pady = simpledialog.askinteger("Padding", "Enter vertical padding (pixels):", minvalue=0)                                 #
    if new_padx is not None and new_pady is not None:                           # Check if the user made a selection              #
        listbox.config(padx=new_padx, pady=new_pady)                                                                              #
#----------------------------------------------------------------------------------------------------------------------------------
#                                         =================================
#----------------------------------------------------------------------------------------------------------------------------------
# File Viewer functions                                                                                                           #
#----------------------                                                                                                           #
def display_viewer(filename, raw_data, initial_mode='text'):                                                                      #
    """                                                                         # Display the file viewer window with support for #
    :param filename: Name of the file being viewed.                             # switching between text and binary (hex) modes.  #
    :param raw_data: The raw binary content of the file.                                                                          #
    :param initial_mode: Initial viewing mode ('text' or 'binary').                                                               #
    """                                                                                                                           #
    def on_focus_in(event):                                                     # When focus enter the text entry field           #
        # place here any code you want to run when the search field is entered                                                    #
        pass                                                                                                                      #
                                                                                                                                  #
    def on_focus_out(event):                                                    # When focus leaves the text entry field          #
        # place here any code you want to run when the search field is exited                                                     #
        pass                                                                                                                      #
                                                                                                                                  #
    def on_search(event=None):                                                  # Doing a search                                  #
        search_target = action_entry.get().strip().lower()                      # Case-insensitive                                #
        if search_target:                                                                                                         #
            start_index = '1.0'                                                                                                   #
            text_area.tag_remove('found', '1.0', tk.END)                        # Clear previous highlights                       #
            while True:                                                                                                           #
                pos = text_area.search(search_target, start_index, nocase=True, stopindex=tk.END)                                 #
                if not pos:                                                                                                       #
                    break                                                                                                         #
                end_pos = f"{pos}+{len(search_target)}c"                                                                          #
                text_area.tag_add('found', pos, end_pos)                                                                          #
                start_index = end_pos                                           # Move start index to end of last found           #
            text_area.tag_config('found', background='yellow')                                                                    #
            first_occurrence = text_area.tag_ranges('found')                                                                      #
            if first_occurrence:                                                                                                  #
                text_area.see(first_occurrence[0])                              # Scroll to first occurrence                      #
                                                                                                                                  #
    def on_search_button_clicked():                                                                                               #
        search_target = action_entry.get().strip()                              # Get the trimmed content of the entry field      #
        if not search_target:                                                   # If the search field is empty                    #
            messagebox.showwarning("Search Error", "Please enter text to search for.")                                            #
        else:                                                                                                                     #
            on_search()                                                         # Call your existing on_search function           #
                                                                                                                                  #
    def toggle_mode():                                                                                                            #
        nonlocal viewing_mode                                                                                                     #
        viewing_mode = 'binary' if viewing_mode == 'text' else 'text'                                                             #
        update_viewer(viewing_mode)                                                                                               #
        toggle_button.config(text=f"Switch to {'Text' if viewing_mode == 'binary' else 'Hex'} Mode")                              #
                                                                                                                                  #
    def update_viewer(mode):                                                                                                      #
        text_area.config(state="normal")                                                                                          #
        text_area.delete("1.0", tk.END)                                                                                           #
        if mode == 'text':                                                                                                        #
            encoding = chardet.detect(raw_data)['encoding']                                                                       #
            content = raw_data.decode(encoding, errors='replace') if encoding else ''                                             #
        else:                                                                                                                     #
            lines = []                                                                                                            #
            for i in range(0, len(raw_data), 16):                                                                                 #
                hex_part = ' '.join(f"{b:02X}" for b in raw_data[i:i+16])                                                         #
                ascii_part = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in raw_data[i:i+16])                                 #
                line = f"{i:08X}  {hex_part:<48}  {ascii_part}"                                                                   #
                lines.append(line)                                                                                                #
            content = "\n".join(lines)                                                                                            #
        text_area.insert("1.0", content)                                                                                          #
        text_area.config(state="disabled")                                                                                        #
                                                                                                                                  #
    # Main viewer window                                                                                                          #
    viewer_window = tk.Toplevel(root)                                                                                             #
    viewer_window.title(f"Viewing {filename}")                                                                                    #
    viewer_window.bind('<Control-f>', lambda event: action_entry.focus())       # Bind Ctrl-F to focus on the search entry field  #
                                                                                                                                  #    
    # Text window                                                                                                                 #
    text_area = tk.Text(viewer_window, wrap="none", font=("Consolas", 10))                                                        #
    text_area.pack(expand=True, fill="both")                                                                                      #
                                                                                                                                  #
    # Footer window                                                                                                               #
    control_frame = tk.Frame(viewer_window)                                     # Create viewing window footer frame              #
    control_frame.pack(fill=tk.X, pady=5)                                                                                         #
                                                                                                                                  #
    # "Switch Mode" button                                                                                                        #
    viewing_mode = initial_mode                                                                                                   #
    toggle_button = tk.Button(control_frame, text=f"Switch to {'Text' if viewing_mode == 'binary' else 'Hex'} Mode",              #
                              command=lambda: toggle_mode(), underline=0)                                                         #
    toggle_button.pack(side=tk.LEFT, padx=(5, 0))                                                                                 #
    viewer_window.bind('<Alt-s>', lambda event: toggle_mode())                                                                    #
                                                                                                                                  #
   # Search button                                                                                                                #
    search_button = tk.Button(control_frame, text="Search", command=on_search_button_clicked)                                     #
    search_button.pack(side=tk.LEFT, padx=(5, 5))                               # Adjust padx as needed for spacing               #
                                                                                                                                  #
    # Search entry field                                                                                                          #
    action_entry = tk.Entry(control_frame, width=60)                                                                              #
    action_entry.bind("<FocusIn>", on_focus_in)                                                                                   #
    action_entry.bind("<FocusOut>", on_focus_out)                                                                                 #
    action_entry.bind("<Return>", on_search)                                    # Bind Enter to on_search                         #
    action_entry.pack(side=tk.LEFT, padx=(0, 5))                                                                                  #
                                                                                                                                  #
    update_viewer(viewing_mode)                                                                                                   #
                                                                                                                                  #
def is_binary(filename):                                                                                                          #
    """                                                                                                                           #
    Attempt to determine if a file is binary or text.                                                                             #
    Reads a sample of the file's contents and checks for non-text characters.                                                     #
    """                                                                                                                           #
    try:                                                                                                                          #
        with open(filename, 'rb') as file:                                                                                        #
            sample = file.read(1024)                                            # Read the first 1024 bytes of the file           #
            if b'\0' in sample:                                                                                                   #
                return True                                                     # Found null byte, likely a binary file           #
            detected = chardet.detect(sample)                                   # detect encoding and check if it's binary        #
            if detected['encoding'] is None:                                                                                      #
                return True                                                     # Encoding could not be detected, likely binary   #
    except Exception as e:                                                                                                        #
        print(f"Error checking if file is binary: {e}")                                                                           #
    return False                                                                                                                  #
    debug_print("File encoding: {detected}")                                                                                      #
                                                                                                                                  #
def file_uncompress(filename, temp_dir):                                        # Decompress *.?Q? and *.?Z? using mlbr           #
    """                                                                                                                           #
    :param filename: Path to the file to be decompressed.                                                                         #
    :param temp_dir: Temporary directory where the decompressed file will be placed.                                              #
    """                                                                                                                           #
    try:                                                                                                                          #
        cmd = ['mlbr', '-x', '-D', temp_dir, '-k', filename]                    # Construct the mlbr command                      #
        debug_print("mlbr command:", ' '.join(cmd))                                                                               #
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)# and execute it                                  #
        output = result.stdout.strip()                                                                                            #
        debug_print("mlbr output:", output)                                                                                       #
                                                                                                                                  #
        # Use regular expression to extract the decompressed filename from mlbr's output                                          #
        match = re.search(r'\n(.+?)\s+\d+\s+(Squeezed|Crunched)\s+\((.+?)\s+\d+\)', output, re.IGNORECASE)                        #
        if match:                                                                                                                 #
            decompressed_filename = match.group(1).strip()                      # Get the decompressed filename                   #
            decompressed_file_path = os.path.join(temp_dir, decompressed_filename)                                                #
            return decompressed_file_path                                                                                         #
        else:                                                                                                                     #
            return filename                                                                                                       #
    except subprocess.CalledProcessError as e:                                                                                    #
        print(f"Error decompressing file '{filename}': {e}")                                                                      #
        return filename                                                                                                           #
                                                                                                                                  #
def view_selected_file():                                                                                                         #
    selected_items = tree.selection()                                                                                             #
    if not selected_items:                                                                                                        #
        messagebox.showinfo("No File Selected", "Please select a file to view.")                                                  #
        return                                                                                                                    #
                                                                                                                                  #
    for item_id in selected_items:                                                                                                #
        item_values = tree.item(item_id, 'values')                                                                                #
        usernum, filename, _ = item_values                                                                                        #
                                                                                                                                  #
        src_path = f"{usernum}:{filename}"                                                                                        #
        temp_dir = tempfile.mkdtemp()                                                                                             #
        dest_path = os.path.join(temp_dir, filename)                                                                              #
                                                                                                                                  #
        try:                                                                                                                      #
            # Copy the file from the disk image to the temporary directory                                                        #
            subprocess.run(['cpmcp', '-f', imgformat, current_filename, src_path, dest_path], check=True)                         #
                                                                                                                                  #
            # Determine if the file needs to be decompressed and update dest_path accordingly                                     #
            if len(filename.split(".")) > 1 and filename.split(".")[1][1].lower() in ['q', 'z']:        # File extension has a Q? #
#                unsqueezed_filename = file_uncompress(dest_path)               # Adjusted to pass full path                      #
                dest_path = file_uncompress(dest_path, temp_dir)                # Pass temp_dir to file_uncompress                #
            raw_data = open(dest_path, 'rb').read()                             # Attempt to automatically detect encoding        #
            result = chardet.detect(raw_data)                                                                                     #
            encoding = result['encoding']                                                                                         #
                                                                                                                                  #
            if encoding:                                                                                                          #
                with open(dest_path, 'r', encoding=encoding, errors='replace') as file:                                           #
                    file_contents = file.read()                                                                                   #
#                    display_file_viewer(filename, file_contents)                                                                 #
                    display_viewer(filename, raw_data, "text")                                                                    #
            else:                                                                                                                 #
#                display_binary_viewer(filename, raw_data)                      # If encoding not detected, default to binary     #
                display_viewer(filename, raw_data, "binary")                                                                      #
#                display_hex_viewer(filename, raw_data)                                                                           #
        except Exception as e:                                                                                                    #
            messagebox.showerror("Error", f"Failed to view '{filename}': {e}")                                                    #
        finally:                                                                                                                  #
            os.remove(dest_path)                                                # Cleanup: remove the copied/decompressed file    #
            shutil.rmtree(temp_dir)                                             # and the temporary directory                     #                                                  #
                                                                                                                                  #
def display_hex_viewer(filename, binary_data):                                                                                    #
    viewer_window = tk.Toplevel(root)                                                                                             #
    viewer_window.title(f"Viewing {filename} (Hex)")                                                                              #
    text_area = tk.Text(viewer_window, wrap="none", font=("Consolas", 10))                                                        #
    text_area.pack(expand=True, fill="both")                                                                                      #
                                                                                                                                  #
    hex_data = []                                                                                                                 #
    ascii_data = []                                                                                                               #
    for i, byte in enumerate(binary_data):                                                                                        #
        if i % 16 == 0:                                                                                                           #
            hex_data.append(f"{i:08x}")                                         # Start new line with offset                      #
        hex_data.append(f"{byte:02x}")                                                                                            #
        ascii_char = chr(byte) if 32 <= byte <= 126 else '.'                                                                      #
        ascii_data.append(ascii_char)                                                                                             #
                                                                                                                                  #
        if (i + 1) % 16 == 0 or i == len(binary_data) - 1:                                                                        #
            # End of line or end of file, add ASCII representation and reset for the next line                                    #
            hex_line = " ".join(hex_data[1:])                                   # Skip offset for joining                         #
            ascii_line = "".join(ascii_data)                                                                                      #
            full_line = f"{hex_data[0]}  {hex_line:<48}  {ascii_line}\n"                                                          #
            text_area.insert("end", full_line)                                                                                    #
            hex_data.clear()                                                                                                      #
            ascii_data.clear()                                                                                                    #
                                                                                                                                  #
    text_area.config(state="disabled")                                          # Make text area read-only                        #
                                                                                                                                  #
    scrollbar = tk.Scrollbar(viewer_window, command=text_area.yview)                                                              #
    scrollbar.pack(side="right", fill="y")                                                                                        #
    text_area.config(yscrollcommand=scrollbar.set)                                                                                #
                                                                                                                                  #
                                                                                                                                  #
def display_binary_viewer(filename, data):                                                                                        #
    viewer_window = tk.Toplevel(root)                                                                                             #
    viewer_window.title(f"Viewing {filename} (Binary)")                                                                           #
    text_area = tk.Text(viewer_window, wrap="none", font=("Consolas", 10))                                                        #
    text_area.pack(expand=True, fill="both")                                                                                      #
                                                                                                                                  #
    hex_data = []                                                               # Convert data to hex and ASCII side by side      #
    ascii_data = []                                                                                                               #
    for byte in data:                                                                                                             #
        hex_data.append(f"{byte:02X}")                                                                                            #
        ascii_data.append(chr(byte) if 32 <= byte <= 126 else '.')                                                                #
                                                                                                                                  #
    lines = []                                                                  # Group data into lines of 16 bytes               #
    for i in range(0, len(hex_data), 16):                                                                                         #
        hex_part = " ".join(hex_data[i:i+16])                                                                                     #
        ascii_part = "".join(ascii_data[i:i+16])                                                                                  #
        line = f"{hex_part:<48} {ascii_part}"                                                                                     #
        lines.append(line)                                                                                                        #
                                                                                                                                  #
    text_area.insert("1.0", "\n".join(lines))                                                                                     #
    text_area.config(state="disabled")                                                                                            #
                                                                                                                                  #
    scrollbar = tk.Scrollbar(viewer_window, command=text_area.yview)            # Add scrollbar                                   #
    scrollbar.pack(side="right", fill="y")                                                                                        #
    text_area.config(yscrollcommand=scrollbar.set)                                                                                #
                                                                                                                                  #
def display_file_viewer(filename, contents):                                                                                      #
    viewer_window = tk.Toplevel(root)                                                                                             #
    viewer_window.title(f"Viewing {filename}")                                                                                    #
    text_area = tk.Text(viewer_window, wrap="none")                                                                               #
    text_area.pack(expand=True, fill="both")                                                                                      #
    text_area.insert("1.0", contents)                                                                                             #
    text_area.config(state="disabled")                                          # Make text area read-only                        #
                                                                                                                                  #
def update_listbox_font():                                                      # Prompt the user for font, size, and weight      #
    font_spec = simpledialog.askstring("Font", "Enter font (e.g., 'Arial 12 bold'):")                                             #
                                                                                                                                  #
    if font_spec:                                                               # Check if the user provided a value              #
        try:                                                                    # Create a font obj with the user's specifications#
            new_font = tkFont.Font(font=font_spec)                                                                                #
            listbox.config(font=new_font)                                                                                         #
        except tk.TclError:                                                                                                       #
            tk.messagebox.showerror("Error", "Invalid font specification.")                                                       #
#----------------------------------------------------------------------------------------------------------------------------------
#                                         =================================
#----------------------------------------------------------------------------------------------------------------------------------
# Disk image manipulation                                                                                                         #
#------------------------                                                                                                         #
def update_recent_files_menu():                                                                                                   #
    global recent_files_menu, recent_files                                                                                        #
    recent_files_menu.delete(0, tk.END)                                         # Clear existing entries                          #
                                                                                                                                  #
    if recent_files:  # Check if there are recent files                                                                           #
        for index, (file, format) in enumerate(recent_files):                                                                     #
            recent_files_menu.add_command(                                                                                        #
                label=f"{index + 1}. {os.path.basename(file)} ({format})",                                                        #
                command=lambda file=file, format=format: open_recent_file(file, format),                                          #
                underline=0                                                                                                       #
            )                                                                                                                     #
    else: # No recently opened files, so add disabled menu item with placeholder text                                             #
        recent_files_menu.add_command(label="No recent files", state="disabled")                                                  #
                                                                                                                                  #
def open_recent_file(filepath, format):                                                                                           #
    global current_filename, imgformat                                                                                            #
    current_filename = filepath                                                                                                   #
    imgformat = format                                                                                                            #
    open_image(filepath, format, showDialog=False)                              # Reuse open_image function, or adjust as needed  #
                                                                                                                                  #
def open_image(filepath=None, format=None, showDialog=True):                                                                      #
    global current_filename, recent_files, last_used_directory, imgformat, temp_dir                                               #
    # If filepath is None or showDialog is True, open the dialog                                                                  #
    if filepath is None or showDialog:                                                                                            #
        filetypes = [('CP/M Image', '*.img'), ('CP/M Image', '.IMG'), ('CP/M Image', '.ima'), ('CP/M Image', '.IMA'),             #
                     ('CP/M Image', '.DSK'), ('CP/M Image', '.dsk'), ('All Files', '*')]                                          #
        filename = askopenfilename_case_insensitive(filetypes=filetypes, initialdir=last_used_directory)                          #
    else:                                                                                                                         #
        filename = filepath                                                                                                       #
                                                                                                                                  #
    if filename:                                                                                                                  #
        # If an image is already open, close it and cleanup its temp directory first                                              #
        if current_filename:                                                                                                      #
            close_image()                                                                                                         #
                                                                                                                                  #
        current_filename = filename                                                                                               #
        last_used_directory = os.path.dirname(filename)                                                                           #
                                                                                                                                  #
        # Create a new temporary directory for the opened image                                                                   #
        if temp_dir:  # If a temp directory already exists, clean it up first                                                     #
            shutil.rmtree(temp_dir, ignore_errors=True)                                                                           #
        temp_dir = tempfile.mkdtemp()                                                                                             #
                                                                                                                                  #
        # Update recent files                                                                                                     #
        recent_file = (current_filename, imgformat)                                                                               #
        if recent_file not in recent_files:                                                                                       #
            recent_files.insert(0, recent_file)  # Add to the start of the list                                                   #
            recent_files = recent_files[:5]  # Keep only the last five entries                                                    #
        update_recent_files_menu()  # Call the function to update the menu                                                        #
                                                                                                                                  #
        populate_listbox(current_filename)                                                                                        #
        update_window_title()                                                                                                     #
        return current_filename                                                                                                   #
    return None                                                                                                                   #
                                                                                                                                  #
def open_file_or_dialog():                                                                                                        #
    global current_filename                                                                                                       #
    if current_filename and not tree.get_children():                            #If filename provided on command line and treeview#
        populate_listbox(current_filename)                                      #empty (i.e. no file currently open) open filename#
        update_window_title()                                                                                                     #
                                                                                                                                  #
def close_image():                                                                                                                #
    global current_filename, temp_dir                                                                                             #
    current_filename = ""                                                                                                         #
    tree.delete(*tree.get_children())                                           # Assuming you're using a treeview                #
                                                                                                                                  #
    update_window_title()                                                                                                         #
    # Cleanup the temporary directory                                                                                             #
    if temp_dir:                                                                                                                  #
        shutil.rmtree(temp_dir, ignore_errors=True)                                                                               #
        temp_dir = None                                                                                                           #
                                                                                                                                  #
def view_disk_image_in_hex():                                                                                                     #
    if not current_filename:                                                                                                      #
        messagebox.showinfo("No Image Open", "Please open an image file before attempting to view it.")                           #
        return                                                                                                                    #
                                                                                                                                  #
    try:                                                                                                                          #
        with open(current_filename, 'rb') as file:                                                                                #
            raw_data = file.read()                                                                                                #
            display_viewer(os.path.basename(current_filename), raw_data, initial_mode='binary')                                   #
    except Exception as e:                                                                                                        #
        messagebox.showerror("Error", f"Failed to view disk image: {e}")                                                          #
                                                                                                                                  #
#----------------------------------------------------------------------------------------------------------------------------------

def save_config():                                                              # update config file
    config = configparser.ConfigParser()

    config['Settings'] = {                                                      # store these settings
        'initial_text_color': initial_text_color,
        'initial_bg_color': initial_bg_color,
        'initial_font': ' '.join(map(str, initial_font)),
        'initial_border_width': str(initial_border_width),
        'initial_padding_x': str(initial_padding_x),
        'initial_padding_y': str(initial_padding_y),
        'initial_width': str(initial_width),
        'initial_height': str(initial_height),
    }

    config['RecentFiles'] = {
        'files': ';'.join([f"{path}|{format}" for path, format in recent_files])
    }

    with open(config_file_path, 'w') as configfile:
        config.write(configfile)

def load_config():
    global initial_text_color, initial_bg_color, initial_font
    global initial_border_width, initial_padding_x, initial_padding_y
    global initial_width, initial_height, recent_files

    config = configparser.ConfigParser()
    config.read(config_file_path)

    if 'Settings' in config:
        settings = config['Settings']
        initial_text_color = settings.get('initial_text_color', 'black')
        initial_bg_color = settings.get('initial_bg_color', 'white')
        initial_font = tuple(settings.get('initial_font', 'Mono 12 normal').split())
        initial_border_width = int(settings.get('initial_border_width', 2))
        initial_padding_x = int(settings.get('initial_padding_x', 5))
        initial_padding_y = int(settings.get('initial_padding_y', 5))
        initial_width = int(settings.get('initial_width', 50))
        initial_height = int(settings.get('initial_height', 30))

    if 'RecentFiles' in config:
        files = config['RecentFiles'].get('files', '')
        recent_files = [(path, format) for path, format in 
                        (file.split('|') for file in files.split(';') if file)]
        
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

    if tree.get_children():
        first_item = tree.get_children()[0]
        tree.focus(first_item)  # Set focus to the TreeView and specifically to the first item
#        tree.selection_set(first_item)  # Select the first item
        tree.focus_set()

def on_select(event):
    widget = event.widget
    selected_indices = widget.curselection()

    unselectable_indices = [0, 1]                                               # Define unselectable indices for header lines

    last_index = widget.size() - 1                                              # Calculate and add indices for footer lines
    unselectable_indices.extend([last_index - 1, last_index])

    for index in selected_indices:                                              # Deselect if any unselectable indices are selected
        if index in unselectable_indices:
            widget.selection_clear(index)

def translate_filename(filename):                                               # translate a filename between CP/M and host OS formats

    orig_name = filename                                                        # preserve original name
    
    character_mappings = [                                                      # CP/M-to-host char mappings
        ('/', '_'),
        ('&', '%'),
        ('$', '='),
    ]
    for original_char, translated_char in character_mappings:                   # translate CP/M-to-host
        filename = filename.replace(original_char, translated_char)
        
    if filename != orig_name:                                                   # if something changed, we're done
        return filename
    
    character_mappings = [                                                      # else repeat with host-to-CP/M char mappings
        ('_', '/'),
        ('%', '&'),
        ('=', '$')
    ]
    for original_char, translated_char in character_mappings:
        filename = filename.replace(original_char, translated_char)
        
    return filename

def import_files():
    debug_print("IMPORTING FILE")
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
    translated_filename=translate_filename(corrected_filename) # translate filename to CP/M format
    
    usernum = prompt_user_number()
    if usernum is None:
        return  # User cancelled the usernum dialog

    # Execute the cpmcp command
    try:
        cmd = ['cpmcp', '-f', imgformat, current_filename, filename_to_import, f'{usernum}:{translated_filename}']
        debug_print("Executing command:", ' '.join(cmd))                        # Print the command for troubleshooting
        result = subprocess.run(cmd, check=True, text=True, capture_output=True)
        if "device full" in result.stderr.lower():
            messagebox.showerror("Insufficient room", "The CP/M device is full.")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Import Error", f"Failed to import '{filename_to_import}': {e}")
    refresh_listbox()
    
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
        translated_filename=translate_filename(filename) # translate filename to host format
        dest_path = os.path.join(destination_directory, translated_filename)    # copy to here

        # Execute the cpmcp command
        try:
            cmd = ['cpmcp', '-f', imgformat, current_filename, src_path, dest_path]
            debug_print("dest_path: ", dest_path)
            debug_print("Executing command:", ' '.join(cmd))                    # Print the command for troubleshooting
            debug_print("Original name: ", filename, "Translated name: ", translated_filename)
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Extraction Error", f"Failed to extract '{filename}': {e}")

    messagebox.showinfo("Extraction Complete", "Selected files have been extracted.")

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
    
    restricted_chars = '<>,;:=?*[]%|()\\'                                       # Define CP/M restricted characters and 8.3 filename pattern
    pattern = re.compile("^[^.]{1,8}(.[^.]*)?$")                                # Basic 8.3 pattern check
    
    filename = initial_filename
    while True:
        if any(char in restricted_chars for char in filename) or not pattern.match(filename):
            messagebox.showerror("Invalid Filename", "Filename must comply with 8.3 format and not contain restricted characters.")
            filename = simpledialog.askstring("Correct Filename", "Enter a new filename:", initialvalue=filename)
            if filename is None:  # User cancelled
                return None
        else:
            return filename

def confirm_delete():
    return messagebox.askokcancel("Confirm Delete", "Are you sure you want to delete the selected item(s)?")

def quit_application():
    if confirm_quit():
        root.quit()

def confirm_quit():
    return messagebox.askokcancel("Quit", "Are you sure you want to quit?")

def on_close(event=None):
    save_config()
    if confirm_quit():
        root.quit()

def askopenfilename_case_insensitive(**options):
    if 'filetypes' in options:
        filetypes = options['filetypes']
        new_filetypes = [(ftype[0], ftype[1].lower() + ftype[1][1:]) if ftype[1].startswith('*') else ftype for ftype in filetypes]
        options['filetypes'] = new_filetypes
    return filedialog.askopenfilename(**options)

def format_changed(new_format):
    global imgformat, current_filename, recent_files
    imgformat = new_format
    
    for i, (filename, format) in enumerate(recent_files): # Find and update the format for the current file in the recent_files list
        if filename == current_filename:
            recent_files[i] = (filename, imgformat)                             # Update the format
            break
    update_recent_files_menu()                                                  # Refresh the Open Recents menu

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

#----------------------------------------------------------------------------------------------------------------------------------
# App UI creation                                                                                                                 #
#----------------                                                                                                                 #
                                                                                                                                  #
  # Main App Window                                                                                                               #
                                                                                                                                  #
root = tk.Tk()                                                                                                                    #
root.title("CPMImage")                                                                                                            #
root.resizable(True, True)                                                                                                        #
root.geometry("400x400")                                                                                                          #
                                                                                                                                  #
  # Main Menu                                                                                                                     #
                                                                                                                                  #
menubar = tk.Menu(root)                                                                                                           #
root.config(menu=menubar)                                                                                                         #
                                                                                                                                  #
file_menu = tk.Menu(menubar, tearoff=0)                                                                                           #
file_menu.add_command(label="New Image...", command=create_new_image, accelerator="Ctrl+N", underline=0)                          #
file_menu.add_command(label="Open Image...", command=open_image, accelerator="Ctrl+O", underline=0)                               #
recent_files_menu = tk.Menu(file_menu, tearoff=0)                                                                                 #
file_menu.add_cascade(label="Open Recents", menu=recent_files_menu, underline=5)                                                  #
file_menu.add_command(label="Close Image", command=close_image, accelerator="Ctrl+W", underline=0)                                #
file_menu.add_separator()                                                                                                         #
file_menu.add_command(label="View Image (Hex)", command=view_disk_image_in_hex, underline=12)                                     #
file_menu.add_separator()                                                                                                         #
file_menu.add_command(label="Save Image", command=lambda: print("Save Image"), accelerator="Ctrl+S", underline=0)                 #
file_menu.add_command(label="Save Image As...", command=lambda: print("Save Image As"), accelerator="Ctrl+Shift+S", underline=5)  #
file_menu.add_separator()                                                                                                         #
file_menu.add_command(label="Quit", command=quit_application, accelerator="Ctrl+Q", underline=0)                                  #
menubar.add_cascade(label="File", menu=file_menu, underline=0)                                                                    #
                                                                                                                                  #
image_menu = tk.Menu(menubar, tearoff=0)                                                                                          #
image_menu.add_command(label="Extract", command=extract_items, accelerator="Ctrl+E", underline=0)                                 #
image_menu.add_command(label="Import...", command=import_files, accelerator="Ctrl+I", underline=0)                                #
image_menu.add_separator()                                                                                                        #
image_menu.add_command(label="View File", command=view_selected_file, accelerator="Ctrl+V",underline=0)                           #
image_menu.add_command(label="Delete item(s)", command=delete_items, accelerator="Delete", underline=0)                           #
image_menu.add_separator()                                                                                                        #
image_menu.add_command(label="Refresh", command=lambda: populate_listbox(current_filename), accelerator="F5", underline=0)        #
menubar.add_cascade(label="Image", menu=image_menu, underline=0)                                                                  #
                                                                                                                                  #
format_menu = tk.Menu(menubar, tearoff=0)                                                                                         #
populate_format_menu()                                                                                                            #
menubar.add_cascade(label="Format", menu=format_menu, underline=1)                                                                #
                                                                                                                                  #
settings_menu = tk.Menu(menubar, tearoff=0)                                                                                       #
settings_menu.add_command(label="Text Color...", command=choose_text_color)                                                       #
settings_menu.add_command(label="Background Color...", command=choose_bg_color)                                                   #
settings_menu.add_command(label="Font...", command=update_listbox_font)                                                           #
settings_menu.add_command(label="Selection Background Color...", command=choose_select_bg_color)                                  #
settings_menu.add_command(label="Selection Text Color...", command=choose_select_fg_color)                                        #
settings_menu.add_command(label="Customize Border...", command=customize_border)                                                  #
settings_menu.add_command(label="Customize Padding...", command=customize_padding)                                                #
settings_menu.add_separator()                                                                                                     #
settings_menu.add_checkbutton(label="Debug Mode", command=toggle_debug_mode)    # Keep the toggle for debug mode if needed        #
menubar.add_cascade(label="Settings", menu=settings_menu)                                                                         #
                                                                                                                                  #
  # Tree view                                                                                                                     #
                                                                                                                                  #
frame = ttk.Frame(root)                                                                                                           #
frame.pack(fill='both', expand=True)                                            # This frame will contain the Treeview            #
                                                                                                                                  #
columns = ('un', 'name', 'size')                                                                                                  #
tree = ttk.Treeview(frame, columns=columns, show='headings', height=15)                                                           #
tree.pack(fill='both', expand=True)  # Pack the Treeview widget once                                                              #
tree.heading('un', text='U#')                                                                                                     #
tree.heading('name', text='Name')                                                                                                 #
tree.heading('size', text='Size (K)')                                                                                             #
tree.column('un', width=30, anchor='center')                                                                                      #
tree.column('name', width=150, anchor='w')                                                                                        #
tree.column('size', width=100, anchor='center')                                                                                   #
for col in columns:                                                                                                               #
    tree.heading(col, text=col.capitalize(), command=lambda _col=col: treeview_sort_column(tree, _col, False))                    #
                                                                                                                                  #
  # Key bindings                                                                                                                  #
                                                                                                                                  #
root.bind_all("<Control-q>", lambda event: on_close())                                                                            #
root.bind_all("<Control-o>", lambda event: open_image())                                                                          #
root.bind_all("<Control-w>", lambda event: close_image())                                                                         #
root.bind_all("<Control-e>", lambda event: extract_items())                                                                       #
root.bind_all("<Control-i>", lambda event: import_files())                                                                        #
root.bind_all("<F5>",        lambda event: populate_listbox(current_filename))                                                    #
root.bind_all("<Control-r>", lambda event: populate_listbox(current_filename))                                                    #
root.protocol("WM_DELETE_WINDOW", on_close)                                                                                       #
tree.bind('<Control-a>', select_all)                                                                                              #
                                                                                                                                  #
  # Footer                                                                                                                        #
                                                                                                                                  #
footer_frame = ttk.Frame(root)                                                                                                    #
footer_frame.pack(fill=tk.X, side='bottom', expand=False)                       # Ensure footer is at the bottom                  #
footer_label = ttk.Label(footer_frame, text="Initializing...", anchor="w")                                                        #
footer_label.pack(fill=tk.X, padx=5, pady=5)                                    # Ensure label fills the footer frame             #
#----------------------------------------------------------------------------------------------------------------------------------

def cleanup_on_exit():                                                          # registered to atexit.register so it will run 
    global temp_dir                                                             # when app exits or crashes
    if temp_dir:
        shutil.rmtree(temp_dir, ignore_errors=True)

atexit.register(cleanup_on_exit)

open_file_or_dialog()
load_config()                                                                   # load any saved configuration settings
update_recent_files_menu()                                                      # Make sure this is called after loading the config
root.mainloop()
