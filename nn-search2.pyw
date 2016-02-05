#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
Created on Fri Nov 06 20:00:00 2015
@author: tastyminerals@gmail.com
"""
from __future__ import division
import model
import os
import re
import sys
import threading as thr
import ttk
import Tkinter as tk
import tkFileDialog as tkf
import tkMessageBox
import Queue
from PIL import ImageTk as itk
from tkFileDialog import askopenfilename

#from pycallgraph import PyCallGraph
#from pycallgraph.output import GraphvizOutput

class NNSearch(ttk.Frame):

    def __init__(self, master):
        # init some instance vars
        self.stats_ready = False  # protect from stats recalculation
        self.model_queue = Queue.Queue()
        self.model_thread = None
        self.model_results = None
        self.textstats = {}
        self.is_file_loaded = False

        # build UI
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
        except TypeError:
            print('Nothing to copy.')
        return 'break'

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

    def insert_text(self, text):
        """
        Insert given text into the Text widget.
        """
        para = text.split('\n\n')
        for par in para:
            self.Text.insert(tk.END, par)
        self.Text.insert(tk.END, '\n')

    def centrify_widget(self, widget):
        """
        Centrify the position of a given widget.

        Args:
            *widget* (tk.Widget) -- tk widget object

        """
        widget.update_idletasks()
        width = widget.winfo_screenwidth()
        height = widget.winfo_screenheight()
        xy = tuple(int(c) for c in widget.geometry().split('+')[0].split('x'))
        xpos = width/2 - xy[0]/2
        ypos = height/2 - xy[1]/2
        widget.geometry("%dx%d+%d+%d" % (xy + (xpos, ypos)))

    def show_message(self, msg, icon):
        """
        Show a warning window with a given message.

        Args:
            | *msg* (str) -- a message to display
            | *icon* (str) -- icon name

        """
        self.message = tk.Toplevel()
        self.message.title('Warning!')
        self.message.resizable(0, 0)
        self.warnFr = ttk.Frame(self.message, borderwidth=2, relief='groove')
        self.warnFr.grid(sticky='nsew')
        ttk.Label(self.warnFr, font='TkDefaultFont 10', text=msg).grid()
        self.err_img = itk.PhotoImage(file=os.path.join('icons', icon))
        ttk.Label(self.warnFr, image=self.err_img).grid()
        ttk.Button(self.warnFr, padding=(0, 2), text='OK',
                   command=self.message.destroy).grid()
        self.centrify_widget(self.message)
        return

    def load_data(self):
        """
        Open a file dialog window.
        Load a file. Handle file loading errors accordingly.
        Invoke data preprocessing and pos-tagging functions.

        <I think it is better to do main text processing together with the
        file loading operation. This reduces query search response time.>

        Returns:
            | *loaded_text* (str) -- preprocessed text
            | if IOError, OSError return None

        """
        types = (("txt file", "*.txt"),
                 ("Microsoft Word file", ("*.doc", "*.docx")),
                 ("PDF file", "*.pdf"),
                 ("All files", "*.*"))
        fpath = tkf.askopenfilename(filetypes=types)
        try:
            # limit the file size to 10 mb
            fsize = os.path.getsize(fpath) / (1024 * 1024)
            if fsize > 10:
                self.show_message("The file is too big!", 'warning.png')
                return None
            loaded_text = model.read_input_file(fpath)
            fname = os.path.basename(fpath)
            if len(fname) > 20:
                fname = fname[:17] + '...'
        except (IOError, OSError):
            msg = "Oops! you didn't provide any file to read!"
            self.show_message(msg, 'warning.png')
            return

        # update the file stats
        self.set_file_loaded(True)
        self.stats0.config(text="Name: {0}".format(fname))
        self.stats1.config(text="Size: {0}kb".format(round(fsize * 1024, 1)))

        # insert read text into Text widget
        self.insert_text(loaded_text)

        # reset text statistics after we loaded a new file
        self.set_stats_ready(False)

        # get accumulated text from Text widget and run text processing
        loaded_text = self.Text.get("1.0",'end-1c')
        self.process_command(model.process_text, self.model_queue, loaded_text)
        self.Text.edit_modified(False)  # reset after file load

    def check_thread_save_results(self):
        """
        Check every 10ms if model thread is alive.
        Destroy progress bar when model thread finishes.
        Unlock UI widgets.
        """
        if self.model_thread.is_alive():
            self.after(10, self.check_thread_save_results)
        else:
            # get the results of model processing
            self.model_results = self.model_queue.get()
            self.progress_bar.stop()
            self.prog_win.destroy()
            self.lock_ui(False)

    def process_command(self, func, *args):
        """
        Process given arguments.
        Start the indeterminate progress bar.
        Lock UI widgets.
        <Some UI widgets are connected to this function. The purpose of this
        function is to display a progress bar while running model functions in
        a separate thread>.
        """
        self.lock_ui(True)
        self.prog_win = tk.Toplevel()
        self.prog_win.title('Exercise some patience...')
        self.prog_win.resizable(0, 0)
        self.progFr = ttk.Frame(self.prog_win, borderwidth=2, relief='groove')
        self.progFr.grid(sticky='nsew')
        msg = "Processing..."
        ttk.Label(self.progFr, font='TkDefaultFont 10', text=msg).grid()
        self.prog_img = itk.PhotoImage(file=os.path.join('icons', 'proc.png'))
        ttk.Label(self.progFr, image=self.prog_img).grid()
        self.progress_bar = ttk.Progressbar(self.progFr, orient=tk.HORIZONTAL,
                                            mode='indeterminate',
                                            takefocus=True)
        self.progress_bar.grid()
        self.centrify_widget(self.prog_win)
        self.progress_bar.start()

        # now handle the button command
        self.model_thread = thr.Thread(target=func, args=args)
        # start new model thread while running UI
        self.model_thread.start()
        # check if model_thread finished
        self.after(10, self.check_thread_save_results)

    def recalc_stats(self):
        """
        Recalculate text stats.
        """
        accumulated_text = self.Text.get("1.0", 'end-1c')
        self.process_command(model.process_text, self.model_queue,
                             accumulated_text)
        self.set_stats_ready(False)

        if self.Text.edit_modified() or not self.is_file_loaded:
            # update the file stats
            self.stats0.config(text="Name: {0}".format('Text field'))
            acc_size = round(len(accumulated_text) / 1024, 1)
            self.stats1.config(text="Size: {0}kb".format(acc_size))

    def show_stats(self):
        """
        Create a new TopLevel window.
        Calculate text stats and insert them as Label widgets.
        Add "Close" button. Check if we already calculated stats, if yes then
        reuse instead of recalculating.
        """
        try:
            if not self.stats_ready:
                self.textstats = model.get_stats(self.model_results[0])
                self.set_stats_ready(True)
        except TypeError:
            self.show_message('No data provided!', 'error.png')
            return

        # display "Calculating" message for each stat categrory in the pop-up
        ltext = 'Tokens count:\nWords count:\nSentences count: \n' +\
                '-------------------------------\n' +\
                'Lexical diversity [0,1]:\nSubjectivity [0,1]: \n' +\
                'Polarity [-1,1]: \nCorrectness [0,1]: \n'
        rtext = '{0}\n{1}\n{2}\n---------\n{3}\n{4}\n{5}\n{6}'

        # update the information to calculated stats
        stats_text = rtext.format(self.textstats.get('tokens'),
                                  self.textstats.get('words'),
                                  self.textstats.get('sents'),
                                  self.textstats.get('diversity'),
                                  self.textstats.get('subj'),
                                  self.textstats.get('polar'),
                                  self.textstats.get('corr'))
        # create a pop-up window
        self.stats_win = tk.Toplevel()
        # centering window position
        self.stats_win.title("Statistics")
        self.stats_win.resizable(0, 0)
        self.statsFr = ttk.Frame(self.stats_win, borderwidth=2,
                                 relief='groove')
        self.statsFr.grid()
        self.statsFrInn1 = ttk.Frame(self.statsFr, borderwidth=2,
                                     relief='groove')
        self.statsFrInn1.grid(row=0, column=0, sticky='ns')
        self.statsFrInn2 = ttk.Frame(self.statsFr, borderwidth=2,
                                     relief='groove')
        self.statsFrInn2.grid(row=0, column=1, sticky='ns')
        self.ltext = ttk.Label(self.statsFrInn1, font='TkDefaultFont 10',
                               text=ltext)
        self.ltext.grid()
        self.rtext = ttk.Label(self.statsFrInn2, font='TkDefaultFont 10 bold',
                               text=stats_text)
        self.rtext.grid()
        ttk.Button(self.statsFr, text='Close', padding=(0, 0),
                   command=self.stats_win.destroy).grid(sticky='s')
        self.centrify_widget(self.stats_win)

    def mk_graphs(self):
        try:
            if not self.stats_ready:
                self.textstats = model.get_stats(self.model_results[0])
                self.set_stats_ready(True)
        except TypeError:
            self.show_message('No data provided!', 'error.png')
            return
        model.plot_tags(self.textstats.get('tags'))

    def build_gui(self):
        """
        Create user interface including all necessary components like Frames,
        Buttons, Labels etc.
        """
        def put_resizable(elem, row, col, colspan, rowspan, stick):
            """
            Place the element and make it resizable.

            Args:
                | *elem* (ttk Object) -- ttk Object instance
                | *row* (int) -- row on which the element is placed
                | *col* (int) -- col on which the elemnt is placed
                | *colspan* (int) -- how many columns are allowed to span
                | *rowspan* (int) -- how many rows are allowed to span
                | *stick* (str) -- element alignment within the cell

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
        put_resizable(self.MenuFrm, 0, 0, 2, 1, 'w')
        self.Menu0 = tk.Menu(self.MenuFrm, tearoff=False)
        self.MenuButton0 = ttk.Menubutton(self.MenuFrm, text='File',
                                          direction='below',
                                          menu=self.Menu0)
        self.load = itk.PhotoImage(file=os.path.join('icons', 'load.png'))
        self.Menu0.add_command(label="Load", image=self.load, compound='left',
                               command=self.load_data)
        self.save = itk.PhotoImage(file=os.path.join('icons', 'disk.png'))
        self.Menu0.add_command(label="Save", image=self.save, compound='left')
        self.save2 = itk.PhotoImage(file=os.path.join('icons', 'disk2.png'))
        self.Menu0.add_command(label="Save as", image=self.save2,
                               compound='left')
        self.exit = itk.PhotoImage(file=os.path.join('icons', 'exit.png'))
        self.Menu0.add_command(label="Exit", image=self.exit, compound='left',
                               command=self.quit)
        put_resizable(self.MenuButton0, 0, 0, 1, 1, 'n')
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
        put_resizable(self.MenuButton1, 0, 1, 1, 1, 'n')
        # make "Tools" menu
        self.Menu2 = tk.Menu(self.MenuFrm, tearoff=False)
        self.MenuButton2 = ttk.Menubutton(self.MenuFrm, text='Tools',
                                          direction='below',
                                          menu=self.Menu2)
        self.tagger = itk.PhotoImage(file=os.path.join('icons', 'wand.png'))
        self.Menu2.add_command(label="POS-tagger", image=self.tagger,
                               compound='left', command=None)
        put_resizable(self.MenuButton2, 0, 2, 1, 1, 'n')
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
        put_resizable(self.MenuButton3, 0, 3, 1, 1, 'n')
        # make a frame for query input widget
        self.EntryFrm = ttk.Frame(self.Main, borderwidth='2', relief='groove')
        put_resizable(self.EntryFrm, 1, 0, 1, 1, 'we')
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
        self.search_butt= ttk.Button(self.EntryFrm, padding=(-5, 0),
                                     text='Search', image=self.search,
                                     compound='left', command=self.press_return)
        self.search_butt.grid(row=1, column=1, **options)
        # make text frame
        self.TextFrm = ttk.Frame(self.Main, borderwidth=2, relief='groove')
        put_resizable(self.TextFrm, 2, 0, 1, 1, 'nsew')
        # make text widget
        self.Text = tk.Text(self.TextFrm, font='TkDefaultFont 10', height=35,
                            width=100,
                            undo=True,
                            takefocus=0)
        put_resizable(self.Text, 2, 0, 1, 1, 'nsew')
        self.Text.bind('<Control-a>', self.ctrl_a)
        self.Text.bind('<Control-z>', self.ctrl_z)
        self.Text.bind('<Control-u>', self.ctrl_u)
        self.Text.edit_modified(False)  # set Text widget -- not modified
        # make a scrollbar for text widget
        self.scroll = ttk.Scrollbar(self.TextFrm, command=self.Text.yview)
        self.Text.config(yscrollcommand=self.scroll.set)
        self.scroll.grid(row=2,column=1, sticky='ens')
        # make the right frame
        self.RightFrm = ttk.Frame(self.Main, borderwidth=2, relief='groove')
        put_resizable(self.RightFrm, 1, 1, 2, 2, 'new')
        # make inner frame that will contain "Load", "Save" buttons.
        self.InnerRightFrm0 = ttk.Frame(self.RightFrm, borderwidth=2,
                                        relief='groove')
        put_resizable(self.InnerRightFrm0, 0, 0, 2, 1, 'new')
        # add a label for "Load", "Save" frame
        self.flab = ttk.Label(self.InnerRightFrm0,
                              font='TkDefaultFont 10 bold',
                              text='File load/save')
        self.flab.grid(row=0)
        # make "Load", "Save" buttons for right frame
        self.load_butt = ttk.Button(self.InnerRightFrm0, padding=(0, 0),
                                    text='Load', image=self.load,
                                    compound='left', command=self.load_data)
        self.load_butt.grid(row=1, column=0, sticky='nwe', pady=1, padx=1)
        self.save_butt = ttk.Button(self.InnerRightFrm0, padding=(0, 0),
                                    text='Save', image=self.save,
                                    compound='left', command=self.press_return)
        self.save_butt.grid(row=2, column=0, sticky='nwe', pady=1, padx=1)
        # make inner frame that will contain view types
        self.InnerRightFrm1 = ttk.Frame(self.RightFrm, borderwidth=2,
                                        relief='groove')
        put_resizable(self.InnerRightFrm1, 1, 0, 2, 1, 'nwe')
        # make view widgets
        self.vlab = ttk.Label(self.InnerRightFrm1,
                              font='TkDefaultFont 10 bold',
                              text='View mode')
        self.vlab.grid(row=0)
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
        self.tags_butt = ttk.Checkbutton(self.InnerRightFrm1, text='POS-tags',
                                         padding=(0, 5), onvalue=1, offvalue=0,
                                         variable=self.show_tags)
        self.tags_butt.grid(row=4)
        # make inner frame that will contain back and stats buttons
        self.InnerRightFrm2 = ttk.Frame(self.RightFrm, borderwidth=2,
                                        relief='groove')
        put_resizable(self.InnerRightFrm2, 2, 0, 2, 1, 'we')
        # add text statistics label
        self.slab = ttk.Label(self.InnerRightFrm2,
                              font='TkDefaultFont 10 bold',
                              text='Statistics')
        self.slab.grid(row=0)
        # make "Stats" buttons
        self.recimg = itk.PhotoImage(file=os.path.join('icons', 'recalc.png'))
        self.recalc_butt = ttk.Button(self.InnerRightFrm2, padding=(0, 5),
                                      text='Recalculate!', image=self.recimg,
                                      compound='left',
                                      command=self.recalc_stats)
        self.recalc_butt.grid(row=1, column=0, sticky='nwe', pady=10, padx=0)

        self.simg1 = itk.PhotoImage(file=os.path.join('icons', 'stats.png'))
        self.stats_butt1 = ttk.Button(self.InnerRightFrm2, padding=(0, 0),
                                      text='Numbers', image=self.simg1,
                                      compound='left',
                                      command=self.show_stats)
        self.stats_butt1.grid(row=2, column=0, sticky='nwe', pady=1, padx=1)

        self.simg2 = itk.PhotoImage(file=os.path.join('icons', 'stats2.png'))
        self.stats_butt2 = ttk.Button(self.InnerRightFrm2, padding=(0, 0),
                                      text='Graphs', image=self.simg2,
                                      compound='left', command=self.mk_graphs)
        self.stats_butt2.grid(row=3, column=0, sticky='nwe', pady=1, padx=1)
        self.simg3 = itk.PhotoImage(file=os.path.join('icons', 'stats3.png'))
        self.stats_butt3 = ttk.Button(self.InnerRightFrm2, padding=(0, 0),
                                      text='Search stats', image=self.simg3,
                                      compound='left', command=None)
        self.stats_butt3.grid(row=4, column=0, sticky='nwe', pady=1, padx=1)

        # make inner frame that will contain file information
        self.InnerRightFrm3 = ttk.Frame(self.RightFrm, borderwidth=2,
                                        relief='groove')
        put_resizable(self.InnerRightFrm3, 3, 0, 2, 1, 'ew')
        # make file info labels
        self.stats = ttk.Label(self.InnerRightFrm3, text='Data source',
                               font='TkDefaultFont 10 bold')
        self.stats.grid(row=0, column=0)
        self.stats0 = ttk.Label(self.InnerRightFrm3, text='Name: not loaded')
        self.stats0.grid(row=1, column=0, sticky='w')
        self.stats1 = ttk.Label(self.InnerRightFrm3, text='Size: not loaded')
        self.stats1.grid(row=2, column=0, sticky='w')

    def lock_ui(self, lock):
        """
        Lock all UI clickable widgets when background operations are running.
        """
        if lock:
            self.MenuButton0.config(state='disabled')
            self.MenuButton1.config(state='disabled')
            self.MenuButton2.config(state='disabled')
            self.MenuButton3.config(state='disabled')
            self.search_butt.config(state='disabled')
            self.load_butt.config(state='disabled')
            self.save_butt.config(state='disabled')
            self.recalc_butt.config(state='disabled')
            self.stats_butt1.config(state='disabled')
            self.stats_butt2.config(state='disabled')
            self.stats_butt3.config(state='disabled')
        else:
            self.MenuButton0.config(state='normal')
            self.MenuButton1.config(state='normal')
            self.MenuButton2.config(state='normal')
            self.MenuButton3.config(state='normal')
            self.search_butt.config(state='normal')
            self.load_butt.config(state='normal')
            self.save_butt.config(state='normal')
            self.recalc_butt.config(state='normal')
            self.stats_butt1.config(state='normal')
            self.stats_butt2.config(state='normal')
            self.stats_butt3.config(state='normal')

    def set_stats_ready(self, state):
        """
        Getter/Setter for self.stats_ready var

        Args:
            *state* (bool) -- True, if text statistics was calculated
        """
        self.stats_ready = state

    def set_file_loaded(self, state):
        """
        Getter/Setter for self.stats_ready var

        Args:
            *state* (bool) -- True, if text statistics was calculated
        """
        self.is_file_loaded = state


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
    #graphviz = GraphvizOutput()
    #graphviz.output_file = 'nn-search.png'
    #with PyCallGraph(output=graphviz):
    #    main()
