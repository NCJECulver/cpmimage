import tkinter as tk
from tkinter import filedialog
import subprocess

def open_image():
    filetypes = [('Image files', '*.img;*.ima;*.dsk;*.IMG;*.IMA;*.DSK'), ('All files', '*.*')]
    filename = filedialog.askopenfilename(filetypes=filetypes)
    if filename:
        populate_listbox(filename)

def populate_listbox(filename):
    # Clear existing items in the listbox
    listbox.delete(0, tk.END)
    try:
        # Run cpmls command and capture its output
        output = subprocess.check_output(['cpmls', '-f', 'ibm-3740', filename], universal_newlines=True)
        # Split the output into lines and populate the listbox
        for line in output.splitlines():
            listbox.insert(tk.END, line)
    except subprocess.CalledProcessError as e:
        # Handle error if cpmls command fails
        listbox.insert(tk.END, f"Error: {e}")

# Create main window
root = tk.Tk()
root.title("CPMImage")

# Set window resizable
root.resizable(True, True)

# Create menu bar
menubar = tk.Menu(root)

# Create File menu
file_menu = tk.Menu(menubar, tearoff=0)
file_menu.add_command(label="New Image...", command=lambda: print("New Image"))
file_menu.add_command(label="Open Image...", command=open_image)
file_menu.add_command(label="Close Image", command=lambda: print("Close Image"))
file_menu.add_separator()
file_menu.add_command(label="Save Image", command=lambda: print("Save Image"))
file_menu.add_command(label="Save Image As...", command=lambda: print("Save Image As"))
file_menu.add_separator()
file_menu.add_command(label="Exit", command=root.quit)
menubar.add_cascade(label="File", menu=file_menu)

# Create Options menu
options_menu = tk.Menu(menubar, tearoff=0)
options_menu.add_command(label="Sort by Name", command=lambda: print("Sort by Name"))
options_menu.add_command(label="Sort by Type", command=lambda: print("Sort by Type"))
options_menu.add_command(label="Sort by User", command=lambda: print("Sort by User"))
options_menu.add_command(label="Sort by Size", command=lambda: print("Sort by Size"))
menubar.add_cascade(label="Options", menu=options_menu)

# Configure root to use the menu bar
root.config(menu=menubar)

# Create listbox
listbox = tk.Listbox(root, width=100, height=30)
listbox.pack(fill=tk.BOTH, expand=True)

# Run the application
root.mainloop()
