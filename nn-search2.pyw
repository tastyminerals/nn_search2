#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
Created on Fri Nov 06 20:00:00 2015
@author: tastyminerals@gmail.com
"""

import os
import re
import sys
import ttk
import Tkinter as tk
import tkFileDialog as tkf
import tkMessageBox
from PIL import ImageTk as itk
from tkFileDialog import askopenfilename


class NNSearch(ttk.Frame):

    def __init__(self, master):
        ttk.Frame.__init__(self, master)
        self.grid(sticky='nsew')  # FIXIT: probably not needed
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        self.rowconfigure(3, weight=1)
        master.minsize(height=300, width=400)
        self.build_gui()

    def press_return(self, *args):
        """
        Trigger query processing when <Enter> or "Search" button is pressed.
        """
        self.query = self.Entry.get().strip()  # get query from entry widget
        # self.Entry.delete(0, 'end')  # removes query from entry widget

    def ctrl_a(self, callback=False):
        """
        Select all in entry or text widget.
        Overwrite tkinter default 'ctrl+/' keybind.
        """
        # checking which text widget has focus
        if self.Entry is self.focus_get():
            self.Entry.select_range(0, 'end')
        elif self.Text is self.focus_get():
            self.Text.tag_add('sel', '1.0', 'end')
        return 'break'

    def ctrl_c(self, callback=False):
        """
        Copy selected text.
        Overwrite tkinter default keybind.
        """
        try:
            # checking which text widget has focus
            if self.Entry is self.focus_get():
                self.clipboard_clear()
                text = self.Entry.get(tk.SEL_FIRST, tk.SEL_LAST)
                self.clipboard_append(text)
            elif self.Text is self.focus_get():
                self.clipboard_clear()
                text = self.Text.get(tk.SEL_FIRST, tk.SEL_LAST)
                self.clipboard_append(text)
            return 'break'
        except:
            print('Nothing to copy.')
            pass

    def ctrl_d(self):
        """
        Delete selected text.
        """
        if self.Entry is self.focus_get():
            self.Entry.delete(tk.SEL_FIRST, tk.SEL_LAST)
        elif self.Text is self.focus_get():
            self.Text.delete(tk.SEL_FIRST, tk.SEL_LAST)
        return 'break'

    def ctrl_x(self, callback=False):
        """
        Cut selected text.
        Overwrite tkinter keybind.
        """
        # checking which text widget has focus
        if self.Entry is self.focus_get():
            self.ctrl_c()
            self.ctrl_d()
        elif self.Text is self.focus_get():
            self.ctrl_c()
            self.ctrl_d()
        return 'break'

    def ctrl_v(self, callback=False):
        """
        Paste copied text.
        Overwrite tkinter default keybind.
        """
        # checking which text widget has focus
        try:
            if self.Entry is self.focus_get():
                self.Entry.insert(tk.INSERT, self.Main.clipboard_get())
            elif self.Text is self.focus_get():
                self.Text.insert(tk.INSERT, self.Main.clipboard_get())
            return 'break'
        except tk.TclError:
            tkMessageBox.showinfo('nn-search 2.0', 'Nothing to paste.')
            return

    def ctrl_z(self, callback=False):
        """
        Undo the last modification in the text widget.
        Overwrite tkinter default keybind.
        """
        try:
            # checking which text widget has focus
            if self.Entry is self.focus_get():
                self.Entry.edit_undo()
            elif self.Text is self.focus_get():
                self.Text.edit_undo()
            return 'break'
        except (tk.TclError, AttributeError):
            tkMessageBox.showinfo('nn-search 2.0', 'Nothing to undo.')
            return

    def ctrl_u(self, callback=False):
        """
        Undo the last modification in the text widget.
        Overwrite tkinter default keybind.
        """
        try:
            # checking which text widget has focus
            if self.Entry is self.focus_get():
                self.Entry.edit_redo()
            elif self.Text is self.focus_get():
                self.Text.edit_redo()
            return 'break'
        except (tk.TclError, AttributeError):
            tkMessageBox.showinfo('nn-search 2.0', 'Nothing to redo.')
            return

    def load_file(self):
        """
        Load text file.
        # Limit text file size.
        """
        fname = tkf.askopenfilename(filetypes=(("txt file", "*.txt"),
                                    ("All files", "*.*")))

        try:
            with open(fname, 'r') as f:
                fdata = f.read()
        except Exception as err:
            print(err)
            sys.exit(1)
        print fdata

    def build_gui(self):
        """
        Create user interface including all necessary components like Frames,
        Buttons, Labels etc.
        """
        def resizable(elem, row, col, colspan, rowspan, stick):
            """
            Place the element and make it resizable.

                ARGS:
                    elem (ttk Object): ttk Object instance.
                    row (int): row on which the element is placed.
                    col (int): col on which the elemnt is placed.
                    colspan (int): how many columns are allowed to span.
                    rowspan (int): how many rows are allowed to span.
                    stick (str): element alignment within the cell.
            """
            elem.grid(row=row, column=col, rowspan=rowspan, columnspan=colspan,
                      sticky=stick)
            elem.grid_columnconfigure(col, weight=1)
            elem.grid_rowconfigure(row, weight=1)

        options = dict(sticky='nsew', pady=1, padx=1)
        # making main frame which shall contain all widgets and subframes
        self.Main = ttk.Frame(self, borderwidth='2', relief='groove')
        self.Main.grid(columnspan=2, rowspan=4, **options)
        self.Main.grid_columnconfigure(0, weight=1)
        self.Main.grid_columnconfigure(1, weight=0)  # do not get hidden
        self.Main.grid_rowconfigure(0, weight=0)
        self.Main.grid_rowconfigure(1, weight=0)
        self.Main.grid_rowconfigure(2, weight=1)
        # make a toolbar menu
        # make "File" menu
        self.MenuFrm = ttk.Frame(self.Main, borderwidth='1', relief='flat')
        resizable(self.MenuFrm, 0, 0, 2, 1, 'w')
        self.Menu0 = tk.Menu(self.MenuFrm, tearoff=False)
        self.MenuButton0 = ttk.Menubutton(self.MenuFrm, text='File',
                                          direction='below',
                                          menu=self.Menu0)
        self.load = itk.PhotoImage(file=os.path.join('icons', 'add.png'))
        self.Menu0.add_command(label="Load", image=self.load, compound='left',
                               command=self.load_file)
        self.save = itk.PhotoImage(file=os.path.join('icons', 'disk.png'))
        self.Menu0.add_command(label="Save", image=self.save, compound='left')
        self.save2 = itk.PhotoImage(file=os.path.join('icons', 'disk2.png'))
        self.Menu0.add_command(label="Save as", image=self.save2,
                               compound='left')
        self.exit = itk.PhotoImage(file=os.path.join('icons', 'exit.png'))
        self.Menu0.add_command(label="Exit", image=self.exit, compound='left',
                               command=self.quit)
        resizable(self.MenuButton0, 0, 0, 1, 1, 'n')
        # make "Edit" menu
        self.Menu1 = tk.Menu(self.MenuFrm, tearoff=False)
        self.MenuButton1 = ttk.Menubutton(self.MenuFrm, text='Edit',
                                          direction='below',
                                          menu=self.Menu1)
        self.copy = itk.PhotoImage(file=os.path.join('icons', 'copy.png'))
        self.Menu1.add_command(label="Copy (Ctrl-c)", image=self.copy,
                               compound='left', command=self.ctrl_c)
        self.cut = itk.PhotoImage(file=os.path.join('icons', 'cut.png'))
        self.Menu1.add_command(label="Cut (Ctrl-x)", image=self.cut,
                               compound='left', command=self.ctrl_x)
        self.paste = itk.PhotoImage(file=os.path.join('icons', 'paste.png'))
        self.Menu1.add_command(label="Paste (Ctrl-v)", image=self.paste,
                               compound='left', command=self.ctrl_v)
        self.undo = itk.PhotoImage(file=os.path.join('icons', 'undo.png'))
        self.Menu1.add_command(label="Undo (Ctrl-z)", image=self.undo,
                               compound='left', command=self.ctrl_z)
        self.redo = itk.PhotoImage(file=os.path.join('icons', 'redo.png'))
        self.Menu1.add_command(label="Redo (Ctrl-u)", image=self.redo,
                               compound='left', command=self.ctrl_u)
        resizable(self.MenuButton1, 0, 1, 1, 1, 'n')
        # make "Tools" menu
        self.Menu2 = tk.Menu(self.MenuFrm, tearoff=False)
        self.MenuButton2 = ttk.Menubutton(self.MenuFrm, text='Tools',
                                          direction='below',
                                          menu=self.Menu2)
        self.tagger = itk.PhotoImage(file=os.path.join('icons', 'wand.png'))
        self.Menu2.add_command(label="POS-tagger", image=self.tagger,
                               compound='left', command=None)
        resizable(self.MenuButton2, 0, 2, 1, 1, 'n')
        # make "Help" menu
        self.Menu3 = tk.Menu(self.MenuFrm, tearoff=False)
        self.MenuButton3 = ttk.Menubutton(self.MenuFrm, text='Help',
                                          direction='below',
                                          menu=self.Menu3)
        self.help = itk.PhotoImage(file=os.path.join('icons', 'help.png'))
        self.Menu3.add_command(label="Help", image=self.help, compound='left',
                               command=None)
        self.about = itk.PhotoImage(file=os.path.join('icons', 'info.png'))
        self.Menu3.add_command(label="About", image=self.about,
                               compound='left', command=None)
        resizable(self.MenuButton3, 0, 3, 1, 1, 'n')
        # make a frame for query input widget
        self.EntryFrm = ttk.Frame(self.Main, borderwidth='2', relief='groove')
        resizable(self.EntryFrm, 1, 0, 1, 1, 'we')
        # make entry widget inside entry frame
        self.Entry = ttk.Entry(self.EntryFrm, font='TkDefaultFont 12')
        self.Entry.grid(row=1, column=0, columnspan=1, **options)
        self.Entry.bind('<Control-a>', self.ctrl_a)
        self.Entry.bind('<Control-z>', self.ctrl_z)
        self.Entry.bind('<Control-u>', self.ctrl_u)
        self.Entry.bind('<Return>', self.press_return, '+')
        self.Entry.focus()  # <Return> enable when entry widget in focus
        # make search button
        self.search = itk.PhotoImage(file=os.path.join('icons', 'search.png'))
        self.Search = ttk.Button(self.EntryFrm, padding=(-5, 0),
                                 text='Search', image=self.search,
                                 compound='left', command=self.press_return)
        self.Search.grid(row=1, column=1, **options)
        # make text frame
        self.TextFrm = ttk.Frame(self.Main, borderwidth=2, relief='groove')
        resizable(self.TextFrm, 2, 0, 1, 1, 'nsew')
        # make text widget
        self.Text = tk.Text(self.TextFrm, font='TkDefaultFont 10', height=35,
                            width=100,
                            undo=True,
                            takefocus=0)
        resizable(self.Text, 2, 0, 1, 1, 'nsew')
        self.Text.bind('<Control-a>', self.ctrl_a)
        self.Text.bind('<Control-z>', self.ctrl_z)
        self.Text.bind('<Control-u>', self.ctrl_u)
        # make the right frame
        self.RightFrm = ttk.Frame(self.Main, borderwidth=2, relief='groove')
        resizable(self.RightFrm, 1, 1, 2, 2, 'nsew')
        # make inner frame that will contain "Load", "Save" buttons.
        self.InnerRightFrm0 = ttk.Frame(self.RightFrm, borderwidth=2,
                                        relief='groove')
        resizable(self.InnerRightFrm0, 0, 0, 2, 1, 'new')
        # make "Load", "Save" buttons for right frame
        self.Load = ttk.Button(self.InnerRightFrm0, padding=(0, 0),
                               text='Load', image=self.load,
                               compound='left', command=self.load_file)
        self.Load.grid(row=0, column=0, sticky='nwe', pady=1, padx=1)
        self.Save = ttk.Button(self.InnerRightFrm0, padding=(0, 0),
                               text='Save', image=self.save,
                               compound='left', command=self.press_return)
        self.Save.grid(row=1, column=0, sticky='nwe', pady=1, padx=1)
        # make inner frame that will contain view types
        self.InnerRightFrm1 = ttk.Frame(self.RightFrm, borderwidth=2,
                                        relief='groove')
        resizable(self.InnerRightFrm1, 1, 0, 2, 1, 'nwe')
        # make view widgets
        self.view_text = ttk.Label(self.InnerRightFrm1, font='TkDefaultFont 9',
                                   text='View mode')
        self.view_text.grid(row=0)
        self.view_opts = tk.IntVar()
        self.view1 = itk.PhotoImage(file=os.path.join('icons', 'view1.png'))
        self.view1Radio = ttk.Radiobutton(self.InnerRightFrm1,
                                          image=self.view1,
                                          variable=self.view_opts,
                                          value=1)
        self.view1Radio.grid(row=1)
        self.view1Radio.invoke()  # make active by default
        self.view2 = itk.PhotoImage(file=os.path.join('icons', 'view2.png'))
        self.view2Radio = ttk.Radiobutton(self.InnerRightFrm1,
                                          image=self.view2,
                                          variable=self.view_opts,
                                          value=2)
        self.view2Radio.grid(row=2)
        self.view3 = itk.PhotoImage(file=os.path.join('icons', 'view3.png'))
        self.view3Radio = ttk.Radiobutton(self.InnerRightFrm1,
                                          image=self.view3,
                                          variable=self.view_opts,
                                          value=3)
        self.view3Radio.grid(row=3)
        # make show POS-rags button
        self.show_tags = tk.IntVar()
        self.showTags = ttk.Checkbutton(self.InnerRightFrm1, text='POS-tags',
                                        padding=(0, 5), onvalue=1, offvalue=0,
                                        variable=self.show_tags)
        self.showTags.grid(row=4)
        # make inner frame that will contain various stats
        self.InnerRightFrm2 = ttk.Frame(self.RightFrm, borderwidth=2,
                                        relief='groove')
        resizable(self.InnerRightFrm2, 2, 0, 2, 1, 'new')
        # make stats labels
        self.stats = ttk.Label(self.InnerRightFrm2, text='Statistics',
                               font='TkDefaultFont 10')
        self.stats.grid(row=0, column=0)
        self.stats0 = ttk.Label(self.InnerRightFrm2, text='NOT IMPLEMENTED')
        self.stats0.grid(row=1, column=0)
        self.stats1 = ttk.Label(self.InnerRightFrm2, text='NOT IMPLEMENTED')
        self.stats1.grid(row=2, column=0)


def main():
    root = tk.Tk()
    root.title('nn-search 2.0')
    # root.geometry("1000x630")  # gui size at startup
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    root.resizable(True, True)
    root.update()
    # ttk_theme = ttk.Style()
    # you can use ttk themes here ('clam', 'alt', 'classic', 'default')
    # ttk_theme.theme_use('default')
    gui = NNSearch(root)
    gui.mainloop()

if __name__ == '__main__':
    main()
