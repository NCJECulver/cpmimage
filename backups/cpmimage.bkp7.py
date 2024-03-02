import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import re
import sys

# Global variable to store the currently opened filename
current_filename = ""
imgformat = 'ibm-3740'
debug_mode = True

# Global variable to control debug mode
debug_mode = False

# Function to handle opening a file from the command line or via dialog
def open_file_or_dialog():
    if len(sys.argv) > 1:
        filename = sys.argv[1]
        if filename:
            populate_listbox(filename)
    else:
        open_image()

# Function to toggle debug mode
def toggle_debug_mode():
    global debug_mode
    debug_mode = not debug_mode
    if debug_mode:
        print("Debug mode enabled")
    else:
        print("Debug mode disabled")

# Function to print debug messages
def debug_print(*args):
    if debug_mode:
        print(*args)
        
def open_image():
    global current_filename
    filetypes = [('All files', '*')]
    filename = askopenfilename_case_insensitive(filetypes=filetypes)
    if filename:
        current_filename = filename
        populate_listbox(filename)

def close_image():
    global current_filename
    current_filename = ""
    listbox.delete(0, tk.END)
    image_menu.entryconfig("Extract", state="disabled")

def populate_listbox(filename):
    # Clear existing items in the listbox
    debug_print("Populating list...")
    listbox.delete(0, tk.END)
    try:
        # Run cpmls command and capture its output
        debug_print(f"cpmls -f  {imgformat} {filename}")
        output = subprocess.check_output(['cpmls', '-f', imgformat, filename], universal_newlines=True)
        debug_print( output )
        
        lines = output.splitlines()
        i = 0
        while i < len(lines):
            line = lines[i]
            # Check if the line starts with a number and a colon
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
        # Handle error if cpmls command fails
        listbox.insert(tk.END, f"Error: {e}")
        image_menu.entryconfig("Extract", state="disabled")

def extract_image():
    global current_filename
    if not current_filename:
        return

    selected_items = [listbox.get(idx) for idx in listbox.curselection()]
    if not selected_items:
        return

    try:
        for item in selected_items:
            # Check if the item starts with a user number
            user_match = re.match(r'^(\d+):(.*)$', item)
            if user_match:
                # Extract the user number and item name
                usernum = user_match.group(1)
                itemname = user_match.group(2)
                # Run subprocess with user number included in the first occurrence of item
                subprocess.run(['cpmcp', '-f', imgformat, current_filename, f'{usernum}{itemname}', itemname])
            else:
                # If no user number found, run subprocess with item as is
                subprocess.run(['cpmcp', '-f', imgformat, current_filename, item, item])
    except subprocess.CalledProcessError as e:
        print(f"Error extracting item '{item}': {e}")

def quit_application():
    if messagebox.askokcancel("Quit", "Are you sure you want to quit?"):
        root.quit()

def askopenfilename_case_insensitive(**options):
    # Wrap the tk filedialog.askopenfilename function to make it case-insensitive
    if 'filetypes' in options:
        filetypes = options['filetypes']
        new_filetypes = []
        for filetype in filetypes:
            new_filetype = list(filetype)
            pattern = new_filetype[1]
            if pattern.startswith('*'):
                new_filetype[1] = pattern.lower() + pattern[1:]
            new_filetypes.append(tuple(new_filetype))
        options['filetypes'] = new_filetypes
    return filedialog.askopenfilename(**options)

def set_img_format(format):
    global imgformat
    imgformat = format
    debug_print("Format changed to", imgformat)
    refresh_listbox()

def refresh_listbox():
    debug_print( "Refreshing 1...")
    if current_filename:
        debug_print( "Refreshing 2...")
        populate_listbox(current_filename)

def format_changed(new_format):
    global imgformat
    imgformat = new_format
    print("Format changed to", imgformat)
    refresh_listbox()

def open_file_or_dialog():
    if len(sys.argv) > 1:
        filename = sys.argv[1]
        if filename:
            populate_listbox(filename)
    else:
        open_image()

# Function to confirm quit action
def confirm_quit():
    return messagebox.askokcancel("Quit", "Are you sure you want to quit?")

# Create main window
root = tk.Tk()
root.title("CPMImage")

# Set window resizable
root.resizable(True, True)

# Create menu bar
menubar = tk.Menu(root)

# Create File menu
file_menu = tk.Menu(menubar, tearoff=0)
file_menu.add_command(label="New Image...", command=lambda: print("New Image"), accelerator="Ctrl+N", underline=0)
file_menu.add_command(label="Open Image...", command=open_image, accelerator="Ctrl+O", underline=0)
file_menu.add_command(label="Close Image", command=close_image, accelerator="Ctrl+W", underline=0)
file_menu.add_separator()
file_menu.add_command(label="Save Image", command=lambda: print("Save Image"), accelerator="Ctrl+S", underline=0)
file_menu.add_command(label="Save Image As...", command=lambda: print("Save Image As"), accelerator="Ctrl+Shift+S", underline=5)
file_menu.add_separator()
file_menu.add_command(label="Quit", command=quit_application, accelerator="Ctrl+Q", underline=0)
menubar.add_cascade(label="File", menu=file_menu, underline=0)

# Create Image menu
image_menu = tk.Menu(menubar, tearoff=0)
image_menu.add_command(label="Extract", command=extract_image, state="disabled", accelerator="Ctrl+E", underline=0)
image_menu.add_command(label="Refresh", command=lambda: populate_listbox(current_filename), accelerator="F5", underline=0)
menubar.add_cascade(label="Image", menu=image_menu, underline=0)

# Create Format menu
format_menu = tk.Menu(menubar, tearoff=0)
format_menu.add_radiobutton(label="ibm-3740", command=lambda: format_changed('ibm-3740'), variable=imgformat)
format_menu.add_radiobutton(label="kpiv", command=lambda: format_changed('kpiv'), variable=imgformat)
format_menu.add_radiobutton(label="osborne1", command=lambda: format_changed('osborne1'), variable=imgformat)
menubar.add_cascade(label="Format", menu=format_menu, underline=1)

# Create Options menu
options_menu = tk.Menu(menubar, tearoff=0)
options_menu.add_command(label="Sort by Name", command=lambda: print("Sort by Name"), accelerator="Ctrl+N", underline=5)
options_menu.add_command(label="Sort by Type", command=lambda: print("Sort by Type"), accelerator="Ctrl+T", underline=5)
options_menu.add_command(label="Sort by User", command=lambda: print("Sort by User"), accelerator="Ctrl+U", underline=5)
options_menu.add_command(label="Sort by Size", command=lambda: print("Sort by Size"), accelerator="Ctrl+Shift+S", underline=5)
menubar.add_cascade(label="Options", menu=options_menu, underline=1)

# Create Debug menu
debug_menu = tk.Menu(menubar, tearoff=0)
debug_menu.add_checkbutton(label="Debug Mode", command=toggle_debug_mode)
menubar.add_cascade(label="Debug", menu=debug_menu)

# Bind keyboard shortcuts
root.bind_all("<Control-q>", lambda event: quit_application())
root.bind_all("<Control-n>", lambda event: print("Ctrl+N pressed"))
root.bind_all("<Control-o>", lambda event: open_image())
root.bind_all("<Control-w>", lambda event: close_image())
root.bind_all("<Control-s>", lambda event: print("Ctrl+S pressed"))
root.bind_all("<Control-Shift-s>", lambda event: print("Ctrl+Shift+S pressed"))
root.bind_all("<Control-e>", lambda event: extract_image())
root.bind_all("<F5>", lambda event: populate_listbox(current_filename))

# Bind Alt-F4 to confirm quit action
root.protocol("WM_DELETE_WINDOW", confirm_quit)

# Configure root to use the menu bar
root.config(menu=menubar)

# Create listbox
listbox = tk.Listbox(root, selectmode=tk.MULTIPLE, width=50, height=30)
listbox.pack(fill=tk.BOTH, expand=True)

# Function call to open file or dialog after main event loop
open_file_or_dialog()

# Run the application
root.mainloop()
