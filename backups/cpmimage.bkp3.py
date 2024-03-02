import tkinter as tk
from tkinter import filedialog
import subprocess
import re

# Global variable to store the currently opened filename
current_filename = ""

def open_image(event=None):
    global current_filename
    filetypes = [('Image files', '*.img;*.ima;*.dsk;*.IMG;*.IMA;*.DSK'), ('All files', '*.*')]
    filename = filedialog.askopenfilename(filetypes=filetypes)
    if filename:
        current_filename = filename
        populate_listbox(filename)
        image_menu.entryconfig("Extract", state="normal")

def close_image(event=None):
    global current_filename
    current_filename = ""
    listbox.delete(0, tk.END)
    image_menu.entryconfig("Extract", state="disabled")

def populate_listbox(filename):
    # Clear existing items in the listbox
    listbox.delete(0, tk.END)
    try:
        # Run cpmls command and capture its output
        output = subprocess.check_output(['cpmls', '-f', 'ibm-3740', filename], universal_newlines=True)
        
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
            subprocess.run(['cpmcp', '-f', 'ibm-3740', current_filename, f'0:{item}', item])
    except subprocess.CalledProcessError as e:
        print(f"Error extracting item '{item}': {e}")

def select_item(event):
    global selected_items
    selected_items = [listbox.get(idx) for idx in listbox.curselection()]

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
file_menu.add_command(label="Exit", command=root.quit, accelerator="Ctrl+Q", underline=1)
menubar.add_cascade(label="File", menu=file_menu)

# Create Image menu
image_menu = tk.Menu(menubar, tearoff=0)
image_menu.add_command(label="Extract", command=extract_image, state="disabled", accelerator="Ctrl+E", underline=0)
menubar.add_cascade(label="Image", menu=image_menu)

# Create Options menu
options_menu = tk.Menu(menubar, tearoff=0)
options_menu.add_command(label="Sort by Name", command=lambda: print("Sort by Name"), accelerator="Ctrl+N", underline=0)
options_menu.add_command(label="Sort by Type", command=lambda: print("Sort by Type"), accelerator="Ctrl+T", underline=0)
options_menu.add_command(label="Sort by User", command=lambda: print("Sort by User"), accelerator="Ctrl+U", underline=0)
options_menu.add_command(label="Sort by Size", command=lambda: print("Sort by Size"), accelerator="Ctrl+Shift+S", underline=0)
menubar.add_cascade(label="Options", menu=options_menu)

# Bind keyboard shortcuts
root.bind_all("<Control-n>", lambda event: print("Ctrl+N pressed"))
root.bind_all("<Control-o>", lambda event: open_image())
root.bind_all("<Control-w>", lambda event: close_image())
root.bind_all("<Control-s>", lambda event: print("Ctrl+S pressed"))
root.bind_all("<Control-Shift-s>", lambda event: print("Ctrl+Shift+S pressed"))
root.bind_all("<Control-q>", lambda event: print("Ctrl+Q pressed"))
root.bind_all("<Control-e>", lambda event: extract_image())

# Configure root to use the menu bar
root.config(menu=menubar)

# Create listbox
listbox = tk.Listbox(root, selectmode=tk.MULTIPLE, width=100, height=30)
listbox.pack(fill=tk.BOTH, expand=True)

# Bind the listbox to select items
listbox.bind("<<ListboxSelect>>", select_item)

# Run the application
root.mainloop()
