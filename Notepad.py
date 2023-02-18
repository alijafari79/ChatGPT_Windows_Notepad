#######################################################################
##########/ DEVELOPED BY ALI JAFARI WITH THE HELP of ChatGPT /#########
#######################################################################

##########/ DESCRIPTION /##############################################
#######################################################################
# Notepad.py
# adding replace functionality
# replace fixed.
# adding blue bg for replaced words.
# remove replace background after 3 second.(using cancel_replace in an other thread).
# set focus to the text field at first.
# binding find function with CTRL+F.
# added splash.
#######################################################################

from tkinter import *
from tkinter import filedialog
from tkinter import font
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from tkinter.filedialog import askopenfilename, asksaveasfilename
import ctypes as ct
import threading
from time import sleep
from tkinter import simpledialog
from PIL import Image, ImageTk

is_running          = ""
Width, Height       = 700,450
xoffset, yoffset    = 0, 0


def dark_title_bar(window, enable_dark=1):

    window.update()
    DWMWA_USE_IMMERSIVE_DARK_MODE = 20
    set_window_attribute = ct.windll.dwmapi.DwmSetWindowAttribute
    get_parent = ct.windll.user32.GetParent
    hwnd = get_parent(window.winfo_id())
    rendering_policy = DWMWA_USE_IMMERSIVE_DARK_MODE

    value = enable_dark
    value = ct.c_int(value)
    set_window_attribute(hwnd, rendering_policy, ct.byref(value), ct.sizeof(value))



def show_splash():
    global xoffset, yoffset
    splash = tk.Tk()
    dark_title_bar(splash)
    splash.geometry(f"{Width}x{Height}")
    xoffset, yoffset = splash.winfo_x(),splash.winfo_y()
    splash.title("Welcome")
    splash.iconbitmap("icon.ico")
    splash.configure(bg='#fff')

    image = Image.open("img.png")
    image = image.resize((Height//2, Height//2))
    image = ImageTk.PhotoImage(image)

    label = tk.Label(splash, image=image, bg='#fff')
    label.pack(pady=Height//2-Height//4)
    splash.after(4000,splash.withdraw)
    splash.after(500,splash.destroy)
    splash.mainloop()
    print("End")


class Notepad:
    def __init__(self, master):
        global is_running
        self.master = master
        self.master.title("Notepad")
        self.theme = "dark monaki"
        self.bg = "#fff"
        self.font_size = tk.StringVar(self.master)
        self.font_size.set(20)
        self.font = ("Times New Roman", self.font_size.get())
        self.textValue = ""
        is_running = True
        self.replace_bg_color = "#0aceff"
        self.find_bg_color = "yellow"
        
        self.enable_fontsize = False

        # Create a scrollbar for the text field
        scrollbar = tk.Scrollbar(self.master)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Create the Text widget
        self.text = Text(self.master, wrap=WORD,height=4, width=4, yscrollcommand=scrollbar.set)
        self.text.pack(fill=BOTH, expand=1)
        self.change_font(self.font)

        self.master.bind('<Control-s>', self.save_file)
        self.text.bind("<Control-f>", self.find)
        self.master.bind("<Control-Shift-s>", self.save_as)

        # Create the menu bar
        menu_bar = Menu(self.master,background='#ff8000', foreground='black', activebackground='white', activeforeground='black')
        self.master.config(menu=menu_bar)

        # Create the File menu
        file_menu = Menu(menu_bar,tearoff=0)
        menu_bar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New", command=self.new_file)
        file_menu.add_command(label="Open", command=self.open_file)
        file_menu.add_command(label="Save", command=self.save_file)
        file_menu.add_command(label="Save As...", command=self.save_as)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.master.quit)

        # Create the Preferences menu
        preferences_menu = Menu(menu_bar,tearoff=0)
        menu_bar.add_cascade(label="Preferences", menu=preferences_menu)

        font = Menu(preferences_menu, tearoff=0)
        font.add_command(label="Change Font", command=self.change_font)

        self.font_menu = Menu(preferences_menu,tearoff=0)
        preferences_menu.add_cascade(label="Font", menu=self.font_menu)
        self.font_menu.add_command(label='Arial', command=lambda: self.change_font(('Arial',self.font_size.get())))
        self.font_menu.add_command(label='Comic Sans MS', command=lambda: self.change_font(('Comic Sans MS',self.font_size.get())))
        self.font_menu.add_command(label='Courier New', command=lambda: self.change_font(('Courier New', self.font_size.get())))
        self.font_menu.add_command(label='Tahoma', command=lambda: self.change_font(('Tahoma', self.font_size.get())))
        self.font_menu.add_command(label='Times New Roman', command=lambda: self.change_font(("Times New Roman", self.font_size.get())))

        theme_menu = Menu(preferences_menu,tearoff=0)
        preferences_menu.add_cascade(label="Themes", menu=theme_menu)
        theme_menu.add_command(label="Dark Monaki", command=lambda: self.change_theme("dark monaki"))
        theme_menu.add_command(label="Dark White", command=lambda: self.change_theme("dark white"))
        theme_menu.add_command(label="White", command=lambda: self.change_theme("white"))

        edit_menu = Menu(menu_bar,tearoff=0)
        menu_bar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Undo", accelerator="\tCtrl+Z", command=self.undo)
        edit_menu.add_command(label="Redo", accelerator="\tCtrl+Y", command=self.redo)
        edit_menu.add_command(label="Copy", accelerator="\tCtrl+C", command=self.copy)
        edit_menu.add_command(label="Paste", accelerator="\tCtrl+V", command=self.paste)
        edit_menu.add_command(label="Find", accelerator="\tCtrl+F", command=self.find)
        edit_menu.add_command(label="Replace", accelerator="\tCtrl+H", command=self.replace)

        help_menu = Menu(menu_bar,tearoff=0)
        menu_bar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About Notepad", command=self.show_help)

        if self.enable_fontsize :
            font_size_label = tk.Label(self.master, text="Font Size: ")
            font_size_label.pack(side="left")
            self.spinbox = Spinbox(self.master, from_=8, to=17, width=3, textvariable=self.font_size)
            self.spinbox.pack(side="left", padx=5)
            self.spinbox.delete(0, tk.END)
            self.spinbox.insert(0, 15)
        self.text.focus_set()
    def new_file(self):
        self.text.delete(1.0, END)

    def open_file(self):
        file = askopenfilename(parent=self.master, defaultextension=".txt", filetypes=[("All Files", "*.*"), ("Text Documents", "*.txt")])
        if file == "":
            file = None
        else:
            self.file_name = file
            self.master.title(f"Notepad - {self.file_name}")
            self.text.delete(1.0, END)
            with open(file, "r") as f:
                self.text.insert(1.0, f.read())

    def save_file(self, path=0):
        file = filedialog.asksaveasfile(mode='w')
        if file != None:
            data = self.text.get(1.0, END)
            file.write(data)
            file.close()
    
    def save_as(self):
        options = {
        'defaultextension': '.txt',
        'filetypes': [('All Files', '*.*'), ('Text Documents', '*.txt')],
        'initialfile': 'untitled.txt',
        'title': 'Save as'
        }
        file = asksaveasfilename(defaultextension=".txt", **options)
        if file == "":
            file = None
        else:
            self.file_name = file
            self.master.title(f"Notepad - {self.file_name}")
            with open(file, "w") as f:
                f.write(self.text.get(1.0, END))

        

    def show_help(self) :
        messagebox.showinfo("Notepad","Notepad - Developed By Ali Jafari ©")

    def change_font(self, font=None):
        print(font)
        if font == None:
            font = font.askfont(self.master)

        self.text.config(font=font)

    def change_theme(self, theme):
        if theme == "dark monaki":
            self.bg = "#333"
            self.text.configure(insertbackground="#fff")
            self.text.config(bg=self.bg, fg="#eee")
        elif theme == "dark white":
            self.bg="#ddd"
            self.text.config(bg=self.bg, fg="#1e1e1e")
        elif theme == "white":
            self.bg="#fff"
            self.text.configure(insertbackground="#000")
            self.text.config(bg=self.bg, fg="#000000")

    def undo(self):
        self.text.edit_undo()

    def redo(self):
        self.text.edit_redo()

    def copy(self):
        self.text.event_generate("<<Copy>>")

    def paste(self):
        self.text.event_generate("<<Paste>>")

    def find(self, test):
        print(test)
        self.find_popup = Toplevel()
        self.find_popup.geometry("400x100")
        self.find_popup.title("Find")
        self.find_popup.grab_set()
        self.find_popup.iconbitmap("search.ico")
        self.find_popup.resizable(0, 0)
        dark_title_bar(self.find_popup)

        find_label = Label(self.find_popup, text="Find:")
        find_label.pack(pady=10, padx=10, side=LEFT)

        self.find_entry = Entry(self.find_popup)
        self.find_entry.pack(pady=10, padx=(5,5), side=LEFT,ipadx=10, ipady=2)
        self.find_entry.focus_set()
        button_frame = Frame(self.find_popup)
        button_frame.pack(pady=10, side=LEFT)

        ok_button = Button(button_frame, text="OK", command=self.find_word, height=1, width=8,relief="solid")
        ok_button.pack(side=LEFT, padx=(20,5))

        cancel_button = Button(button_frame, text="Cancel", command=self.cancel_find, height=1, width=8)
        cancel_button.pack(side=LEFT, padx=(5,20))


    def cancel_find(self, close=True) :
        self.find_popup.destroy()
        self.text.tag_config("found", background="")

    # removes all marks for previous search:
    def find_word(self):
        word = self.find_entry.get()
        start = '1.0'
        try:self.text.tag_remove('found', '1.0', 'end')
        except Exception as e : print(e)
        while True:
            pos = self.text.search(word, start, stopindex='end', nocase=True)
            if not pos:
                break
            start = pos + '+1c'
            self.text.tag_add('found', pos, pos + '+{}c'.format(len(word)))
            self.text.tag_config("found", background=self.find_bg_color)
            self.text.mark_set('insert', pos)
            self.text.see('insert')

    def replace(self):
        # Create the replace popup
        self.replace_popup = Toplevel(self.master)
        self.replace_popup.geometry("350x130")
        self.replace_popup.title("Replace")
        self.replace_popup.resizable(0, 0)
        self.replace_popup.iconbitmap("./replace.ico")
        dark_title_bar(self.replace_popup)

        find_label = tk.Label(self.replace_popup, text="Find :")
        find_label.grid(row=0, column=0, padx=(10,0), pady=7, sticky="w")
        
        self.find_entry = tk.Entry(self.replace_popup)
        self.find_entry.grid(row=0, column=1, padx=(0,2), pady=7,ipadx=10, ipady=2)
        
        replace_label = tk.Label(self.replace_popup, text="Replace :")
        replace_label.grid(row=1, column=0, padx=(10,0), pady=7, sticky="w")
        
        self.replace_entry = tk.Entry(self.replace_popup)
        self.replace_entry.grid(row=1, column=1, padx=(0,2), pady=7,ipadx=10, ipady=2)
        
        ok_button = tk.Button(self.replace_popup, text="Replace", command=lambda: self.replace_text(), height=1, width=8,relief="solid")
        ok_button.grid(row=0, column=2, padx=5, pady=7)
        
        cancel_button = tk.Button(self.replace_popup, text="Cancel", command=self.cancel_replace, height=1, width=8)
        cancel_button.grid(row=1, column=2, padx=5, pady=7)

        self.case_sensitive_var = tk.IntVar()
        case_sensitive_checkbox = tk.Checkbutton(
        self.replace_popup,
        text="Case Sensitive",
        variable=self.case_sensitive_var
        )
        case_sensitive_checkbox.grid(row=2, column=0, padx=10, pady=10)

        self.find_entry.focus_set()

    def replace_text(self):

        find_text = self.find_entry.get()
        replace_text = self.replace_entry.get()
        case_sensitive = self.case_sensitive_var.get()

        if case_sensitive:
            start = self.text.search(find_text, '1.0', END)
            while start:
                end = f"{start}+{len(find_text)}c"
                self.text.delete(start, end)
                self.text.insert(start, replace_text)
                self.text.tag_add('replace', start, start + '+{}c'.format(len(replace_text)))
                self.text.tag_config("replace", background=self.replace_bg_color)
                self.text.mark_set('insert', end)
                self.text.see('insert')
                start = self.text.search(find_text, start, END)
        else:
            self.text.tag_remove("highlight", "1.0", END)
            start = "1.0"
            while True:
                start = self.text.search(find_text, start, nocase=1, stopindex=END)
                if not start:
                    break
                end = f"{start}+{len(find_text)}c"
                self.text.delete(start, end)
                self.text.insert(start, replace_text)
                self.text.tag_add('replace', start, start + '+{}c'.format(len(replace_text)))
                self.text.tag_config("replace", background=self.replace_bg_color)
                self.text.mark_set('insert', end)
                self.text.see('insert')
                start = end

        delay = 3 # delay to remove yellow backgrounds
        close = False
        t=threading.Thread(target=self.cancel_replace, args=(delay,close))
        t.start()

    def cancel_replace(self, delay=0, close=True) :
        if close : self.replace_popup.destroy()
        sleep(delay)
        self.text.tag_config("replace", background="")


if __name__ == '__main__':
    show_splash()
    root = tk.Tk()
    dark_title_bar(root)
    root.geometry(f"{Width}x{Height}+{xoffset}+{yoffset}")
    root.iconbitmap("icon.ico")
    root.lift()
    root.focus_force()
    notepad = Notepad(root)
    root.mainloop()

