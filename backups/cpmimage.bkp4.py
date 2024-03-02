import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import re

# Global variable to store the currently opened filename
current_filename = ""
imgformat = 'ibm-3740'

def open_image():
    filetypes = [('All files', '*')]
    filename = askopenfilename_case_insensitive(filetypes=filetypes)
    if filename:
        populate_listbox(filename)

def close_image():
    global current_filename
    current_filename = ""
    listbox.delete(0, tk.END)
    image_menu.entryconfig("Extract", state="disabled")

def populate_listbox(filename):
    # Clear existing items in the listbox
    listbox.delete(0, tk.END)
    try:
        # Run cpmls command and capture its output
        output = subprocess.check_output(['cpmls', '-f', imgformat, filename], universal_newlines=True)
        
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
            subprocess.run(['cpmcp', '-f', imgformat, current_filename, f'0:{item}', item])
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

# Create main window
root = tk.Tk()
root.title("CPMImage")

# Set window resizable
root.resizable(True, True)

# Create menu bar
menubar = tk.Menu(root)

def post_menu(menu, event):
    # Get the position of the title bar
    x = event.widget.winfo_rootx() + event.widget.winfo_x()
    y = event.widget.winfo_rooty() + event.widget.winfo_y() + event.widget.winfo_height()

    # Generate a virtual mouse click event at the position of the title bar
    event.widget.event_generate("<Button-1>", x=x, y=y)
    
# Create File menu
file_menu = tk.Menu(menubar, tearoff=0)
file_menu.add_command(label="New Image...", command=lambda: print("New Image"), accelerator="Ctrl+N", underline=0)
file_menu.add_command(label="Open Image...", command=open_image, accelerator="Ctrl+O", underline=5)
file_menu.add_command(label="Close Image", command=close_image, accelerator="Ctrl+W", underline=0)
file_menu.add_separator()
file_menu.add_command(label="Save Image", command=lambda: print("Save Image"), accelerator="Ctrl+S", underline=0)
file_menu.add_command(label="Save Image As...", command=lambda: print("Save Image As"), accelerator="Ctrl+Shift+S", underline=5)
file_menu.add_separator()
file_menu.add_command(label="Quit", command=quit_application, accelerator="Ctrl+Q", underline=0)
menubar.add_cascade(label="File", menu=file_menu, underline=0)
#root.bind_all("<Alt-f>", lambda event: file_menu.post(root.winfo_rootx(), root.winfo_rooty()))
#root.bind_all("<Alt-f>", lambda event: file_menu.post(event.x_root, event.y_root))
#root.bind_all("<Alt-f>", lambda event: file_menu.post(root.winfo_rootx(), root.winfo_rooty()))
#root.bind_all("<Alt-f>", lambda event: post_menu(file_menu))
root.bind_all("<Alt-f>", lambda event: post_menu(file_menu, event))

# Create Image menu
image_menu = tk.Menu(menubar, tearoff=0)
image_menu.add_command(label="Extract", command=extract_image, state="disabled", accelerator="Ctrl+E", underline=0)
menubar.add_cascade(label="Image", menu=image_menu, underline=0)
#root.bind_all("<Alt-i>", lambda event: image_menu.post(root.winfo_rootx(), root.winfo_rooty()))
#root.bind_all("<Alt-i>", lambda event: image_menu.post(event.x_root, event.y_root))
#root.bind_all("<Alt-i>", lambda event: image_menu.post(root.winfo_rootx() + 40, root.winfo_rooty()))
#root.bind_all("<Alt-i>", lambda event: post_menu(image_menu))
root.bind_all("<Alt-i>", lambda event: post_menu(image_menu, event))

# Create Format menu
format_menu = tk.Menu(menubar, tearoff=0)
format_menu.add_radiobutton(label="ibm-3740", command=lambda: set_img_format('ibm-3740'), variable=imgformat, underline=5)
format_menu.add_radiobutton(label="kpiv", command=lambda: set_img_format('kpiv'), variable=imgformat, underline=0)
format_menu.add_radiobutton(label="osborne1", command=lambda: set_img_format('osborne1'), variable=imgformat, underline=1)
menubar.add_cascade(label="Format", menu=format_menu, underline=1)
#root.bind_all("<Alt-o>", lambda event: format_menu.post(root.winfo_rootx(), root.winfo_rooty()))
#root.bind_all("<Alt-o>", lambda event: format_menu.post(event.x_root, event.y_root))
#root.bind_all("<Alt-o>", lambda event: format_menu.post(root.winfo_rootx() + 90, root.winfo_rooty()))
#root.bind_all("<Alt-o>", lambda event: post_menu(format_menu))
root.bind_all("<Alt-o>", lambda event: post_menu(format_menu, event))

# Create Options menu
options_menu = tk.Menu(menubar, tearoff=0)
options_menu.add_command(label="Sort by Name", command=lambda: print("Sort by Name"), accelerator="Ctrl+N", underline=5)
options_menu.add_command(label="Sort by Type", command=lambda: print("Sort by Type"), accelerator="Ctrl+T", underline=5)
options_menu.add_command(label="Sort by User", command=lambda: print("Sort by User"), accelerator="Ctrl+U", underline=5)
options_menu.add_command(label="Sort by Size", command=lambda: print("Sort by Size"), accelerator="Ctrl+Shift+S", underline=5)
menubar.add_cascade(label="Options", menu=options_menu, underline=1)
#root.bind_all("<Alt-p>", lambda event: options_menu.post(root.winfo_rootx(), root.winfo_rooty()))
#root.bind_all("<Alt-p>", lambda event: options_menu.post(event.x_root, event.y_root))
#root.bind_all("<Alt-p>", lambda event: options_menu.post(root.winfo_rootx() + 150, root.winfo_rooty()))
#root.bind_all("<Alt-p>", lambda event: post_menu(options_menu))
root.bind_all("<Alt-p>", lambda event: post_menu(options_menu, event))

# Bind keyboard shortcuts
root.bind_all("<Control-q>", lambda event: quit_application())
root.bind_all("<Control-n>", lambda event: print("Ctrl+N pressed"))
root.bind_all("<Control-o>", lambda event: open_image())
root.bind_all("<Control-w>", lambda event: close_image())
root.bind_all("<Control-s>", lambda event: print("Ctrl+S pressed"))
root.bind_all("<Control-Shift-s>", lambda event: print("Ctrl+Shift+S pressed"))
root.bind_all("<Control-e>", lambda event: extract_image())
root.bind_all("<Escape>", lambda event: root.focus_set())

# Configure root to use the menu bar
root.config(menu=menubar)

# Create listbox
listbox = tk.Listbox(root, selectmode=tk.MULTIPLE, width=50, height=30)
listbox.pack(fill=tk.BOTH, expand=True)

# Run the application
root.mainloop()
