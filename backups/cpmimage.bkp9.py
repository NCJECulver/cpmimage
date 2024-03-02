import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import re
import sys

current_filename = ""
imgformat = 'ibm-3740'
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
    filename = sys.argv[1] if len(sys.argv) > 1 else None
    if filename:
        current_filename = filename
        populate_listbox(filename)
    else:
        filename = open_image()
        if filename:
            current_filename = filename

def open_image():
    filetypes = [('All files', '*')]
    filename = askopenfilename_case_insensitive(filetypes=filetypes)
    if filename:
        populate_listbox(filename)
        return filename
    return None

def close_image():
    global current_filename
    current_filename = ""
    listbox.delete(0, tk.END)
    image_menu.entryconfig("Extract", state="disabled")

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
        image_menu.entryconfig("Extract", state="disabled")

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
                subprocess.run(['cpmcp', '-f', imgformat, current_filename, f'{usernum}{itemname}', itemname])
            else:
                subprocess.run(['cpmcp', '-f', imgformat, current_filename, item, item])
    except subprocess.CalledProcessError as e:
        print(f"Error extracting item '{item}': {e}")

    listbox.selection_clear(0, tk.END)
    image_menu.entryconfig("Extract", state="disabled" if not listbox.curselection() else "normal")

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
    print("Format changed to", imgformat)
    refresh_listbox()

def refresh_listbox():
    if current_filename:
        populate_listbox(current_filename)

root = tk.Tk()
root.title("CPMImage")
root.resizable(True, True)

menubar = tk.Menu(root)

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

image_menu = tk.Menu(menubar, tearoff=0)
image_menu.add_command(label="Extract", command=extract_items, state="disabled", accelerator="Ctrl+E", underline=0)
image_menu.add_command(label="Refresh", command=lambda: populate_listbox(current_filename), accelerator="F5", underline=0)
menubar.add_cascade(label="Image", menu=image_menu, underline=0)

format_menu = tk.Menu(menubar, tearoff=0)
format_menu.add_radiobutton(label="ibm-3740", command=lambda: format_changed('ibm-3740'), variable=imgformat)
format_menu.add_radiobutton(label="kpiv", command=lambda: format_changed('kpiv'), variable=imgformat)
format_menu.add_radiobutton(label="osborne1", command=lambda: format_changed('osborne1'), variable=imgformat)
menubar.add_cascade(label="Format", menu=format_menu, underline=1)

options_menu = tk.Menu(menubar, tearoff=0)
options_menu.add_command(label="Sort by Name", command=lambda: print("Sort by Name"), accelerator="Ctrl+N", underline=5)
options_menu.add_command(label="Sort by Type", command=lambda: print("Sort by Type"), accelerator="Ctrl+T", underline=5)
options_menu.add_command(label="Sort by User", command=lambda: print("Sort by User"), accelerator="Ctrl+U", underline=5)
options_menu.add_command(label="Sort by Size", command=lambda: print("Sort by Size"), accelerator="Ctrl+Shift+S", underline=5)
menubar.add_cascade(label="Options", menu=options_menu, underline=1)

debug_menu = tk.Menu(menubar, tearoff=0)
debug_menu.add_checkbutton(label="Debug Mode", command=toggle_debug_mode)
menubar.add_cascade(label="Debug", menu=debug_menu)

root.bind_all("<Control-q>", lambda event: on_close())
root.bind_all("<Control-o>", lambda event: open_image())
root.bind_all("<Control-w>", lambda event: close_image())
root.bind_all("<Control-e>", lambda event: extract_items())
root.bind_all("<F5>", lambda event: populate_listbox(current_filename))

root.protocol("WM_DELETE_WINDOW", on_close)

root.config(menu=menubar)

listbox = tk.Listbox(root, selectmode=tk.MULTIPLE, width=50, height=30)
listbox.pack(fill=tk.BOTH, expand=True)

open_file_or_dialog()

root.mainloop()
