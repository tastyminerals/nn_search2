#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 06 20:00:00 2015
@author: tastyminerals@gmail.com
"""
from __future__ import division
from collections import Counter
import os
import platform
import re
import sys
import threading as thr
import multiprocessing as mproc
import ttk
import Tkinter as tk
import tkFileDialog as tkf
import tkMessageBox
import Queue
from PIL import ImageTk as itk
import shutil

import model
import query
import pos_tagger


# Set various platform dependent variables.
if platform.system() == 'Windows':
    # Helvetica, Times, Arial, Georgia, Tahoma, Verdana
    TKFONT = 'Helvetica 10'
    TKTEXT_FONT = 'Verdana 10'
else:
    TKFONT = 'TkDefaultFont 10'
    TKTEXT_FONT = 'Sans 10'


def set_win_icon(window, icon_path):
    """
    Set a custom icon for a given window.
    """
    img = itk.PhotoImage(file=icon_path)
    window.tk.call('wm', 'iconphoto', window._w, img)


class NNSearch(ttk.Frame):

    def __init__(self, master):
        self.query = ''  # user query
        # stats vars
        self.fully_tagged_sents = {}  # fully POS-tagged sents dict
        self.stats_ready = False  # used not to recalc stats
        self.graphs_ready = False  # used not to recalc graphs
        self.sstats_ready = False  # do not recalc search stats
        self.textstats = {}
        self.sstats = {}
        # processing threads
        self.processed = False  # clicked 'Process!' button
        self.model_queue = Queue.PriorityQueue()
        self.process_thread = None
        self.stats_thread = None
        self.graphs_thread = None
        self.sstats_thread = None
        self.pos_tagger_proc = None
        # text and file vars
        self.loaded_text = None
        self.is_file_loaded = False
        self.current_fname = 'text_field'  # currently processed file
        # results vars
        self.model_results = None
        self.process_results = None
        self.matches = None
        self.view1_text_pos = ''
        self.view2_text = ''
        self.view2_text_pos = ''
        self.view3_text = ''
        self.view3_text_pos = ''
        # right label headers for Number stats pop-up window
        self.num_rlabl = '{0}\n{1}\n{2}\n---------\n{3}\n{4}\n{5}\n{6}'
        # right label headers for search stats pop-up window
        self.ss_rlabl = '{0}\n{1}\n{2}\n'
        # pos-tagger vars
        self.pos_fpath = ''
        self.pos_loaded_text = ''
        self.pos_dir_path = ''
        self.pos_out_dir_path = ''
        # build UI
        self.clean_up()
        ttk.Frame.__init__(self, master)
        # resizing main UI
        self.grid(sticky='nsew')
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        self.rowconfigure(3, weight=1)
        master.minsize(height=300, width=400)
        self.build_gui()
        # read Penn Treebank tags description
        self.penn_treebank = model.get_penn_treebank()

    def press_return(self, *args):
        """
        Trigger query processing when <Enter> or "Search" button is pressed.
        """
        # handle exceptions
        if not self.processed and (self.Text.edit_modified() or
                                   self.is_file_loaded):
            self.show_message('Please click "Process!" button', 'warning.png')
            return
        elif not self.processed and (not self.Text.edit_modified() and
                                     not self.is_file_loaded):
            self.show_message('No data provided!', 'error.png')
            return
        # print self.fully_tagged_sents
        self.query = self.Entry.get().strip()  # get query from entry widget
        # self.Entry.delete(0, 'end')  # removes query from entry widget
        valid = query.preprocess_query(self.query)
        if valid and valid[0] == 1:
            msg = 'Incorrect query syntax in: %s' % valid[1]
            self.show_message(msg, 'error.png')
            return
        if valid and valid[0] == 2:
            msg = 'Incorrect POS-tag used: %s' % valid[1]
            self.show_message(msg, 'error.png')
            return
        # find query matches
        matches, high_type = query.find_matches(valid, self.fully_tagged_sents)
        self.matches = matches
        if matches and not any([m for m in matches.values() if m]):
            msg = 'No matches found \n revise you query'
            self.show_message(msg, 'sad.png')
            return
        elif not matches:
            self.Text.tag_delete('style')  # reset highighting
            return
        # prepare results and add pos-tags to results
        self.prepare_view12(matches)
        self.prepare_view3(matches)
        # insert the results
        self.insert_matches(matches, high_type)

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

    def ctrl_d(self, callback=False):
        """
        Delete character.
        """
        if self.Entry is self.focus_get():
            self.Entry.delete(tk.SEL_FIRST, tk.SEL_LAST)
        elif self.Text is self.focus_get():
            self.Text.delete(tk.SEL_FIRST, tk.SEL_LAST)
        return 'break'

    def ctrl_s(self, callback=False):
        """
        Save text in the Entry widget.
        """
        if self.Text is self.focus_get():
            self.save_data()
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

    def load_file(self):
        """
        Load a file specified by the user.
        """
        types = (("txt file", "*.txt"),
                 ("Microsoft Word file", ("*.doc", "*.docx")),
                 ("PDF file", "*.pdf"),
                 ("All files", "*.*"))
        self.pos_fpath = tkf.askopenfilename(filetypes=types)
        try:
            loaded_text = model.read_input_file(self.pos_fpath)
        except TypeError:  # when clicked Load and didn't choose any file
            return
        except (OSError, IOError):
            msg = "Can not open the specified file!"
            self.show_message(msg, 'warning.png')
            return
        self.pos_loaded_text = loaded_text
        # lock input file button of pos-tagger
        self.pos_indir_butt.config(state='disabled')
        # unlock Process and Stop buttons
        self.pos_run_butt.config(state='normal')
        self.pos_stop_butt.config(state='normal')
        self.pos_dir_path = ''
        # update icon
        self.pos_icon1 = itk.PhotoImage(file=self.img_path('set.png'))
        self.pos_infile_labl.configure(image=self.pos_icon1, text='OK',
                                       compound='left')
        self.pos_infile_labl.grid(sticky='we', row=0, column=1)

    def load_input_dir(self):
        """
        Load a directory specified by the user.
        """
        self.pos_dir_path = tkf.askdirectory()
        # lock input file button of pos-tagger
        self.pos_infile_butt.config(state='disabled')
        # unlock Process and Stop buttons
        self.pos_run_butt.config(state='normal')
        self.pos_stop_butt.config(state='normal')
        self.pos_out_dir_path = ''
        self.pos_loaded_text = ''
        # update icon
        self.pos_icon2 = itk.PhotoImage(file=self.img_path('set.png'))
        self.pos_indir_labl.configure(image=self.pos_icon2, text='OK',
                                      compound='left')

    def load_output_dir(self):
        """
        Load a directory specified by the user.
        """
        self.pos_out_dir_path = tkf.askdirectory()
        # update icon
        self.pos_icon3 = itk.PhotoImage(file=self.img_path('set.png'))
        self.pos_outdir_labl.configure(image=self.pos_icon3, text='OK',
                                       compound='left')

    def check_pos_tagger_save_results(self):
        """
        Checking if the thread is alive and informing the user.
        """
        if self.pos_tagger_proc.is_alive():
            self.after(200, self.check_pos_tagger_save_results)
        elif self.pos_tagger_proc.exitcode != 0:
            self.pos_run_butt.config(text='Process', image=self.pos_runic,
                                     state='normal')
            self.pos_butt.config(state='normal')
            msg = 'POS-tagging terminated!'
            self.show_message(msg, 'thunder.png')
        else:
            self.pos_tagger_proc.join()
            self.pos_run_butt.config(text='Process', image=self.pos_runic,
                                     state='normal')
            self.pos_butt.config(state='normal')
            msg = 'POS-tagging complete!\n' +\
                  'Check the results in the "output" directory\n' +\
                  'or the directory you specified.'
            self.show_message(msg, 'pos_done.png')

    def kill_pos_proc(self):
        """
        Kill spawned pos-tagger process.
        """
        self.pos_tagger_proc.terminate()
        self.pos_run_butt.config(text='Process', image=self.pos_runic,
                         state='normal')
        self.pos_butt.config(state='normal')

    def pos_tagger_run(self):
        """
        Run pos-tagger on the specified files.
        """
        out_dir = self.pos_out_dir_path or os.path.join(os.getcwd(), 'output')
        self.thunder = itk.PhotoImage(file=self.img_path('thunder.png'))
        self.pos_run_butt.config(text='Working...', image=self.thunder,
                                 state='disabled')
        self.pos_butt.config(state='disabled')
        if self.pos_loaded_text:
            in_file_data = {self.pos_fpath: self.pos_loaded_text}
            args = [in_file_data, None, out_dir]
            # spawn a new process
            self.pos_tagger_proc = mproc.Process(target=pos_tagger.main,
                                                 args=(args, True))
            self.pos_tagger_proc.start()
            self.after(200, self.check_pos_tagger_save_results)
        elif self.pos_dir_path:
            files = [os.path.join(self.pos_dir_path, fname) for fname
                     in os.listdir(self.pos_dir_path)]
            in_dir_data = {}
            for text_file in files:
                fname = os.path.basename(text_file)
                loaded_text = model.read_input_file(text_file)
                in_dir_data[fname] = loaded_text
            args = [None, in_dir_data, out_dir]
            # spawn a new process
            self.pos_tagger_proc = mproc.Process(target=pos_tagger.main,
                                                 args=(args, True))
            self.pos_tagger_proc.start()
            # lock and change Process button
            self.after(200, self.check_pos_tagger_save_results)

    def pos_tagger_win(self):
        """
        Display a pos-tagger window.
        Implement pos-tagger using TextBlob's averaged perceptron.
        """
        self.tagger_win = tk.Toplevel()
        self.tagger_win.title('POS-tagger')
        # set custom window icon
        set_win_icon(self.tagger_win, self.img_path('wand.png'))
        # self.tagger_win.lift()
        self.tagger_win.wm_attributes('-topmost', True)
        self.tagger_win.resizable(0, 0)
        pos_taggerFr = ttk.Frame(self.tagger_win, borderwidth=2,
                                 relief='groove')
        pos_taggerFr.grid(sticky='nsew')
        # add a header
        msg = 'Standalone POS-tagger'
        ttk.Label(pos_taggerFr, font='TkDefaultFont 10 bold',
                  text=msg).grid(row=0)
        pos_taggerFrInn0 = ttk.Frame(pos_taggerFr, borderwidth=2,
                                     relief='groove')
        pos_taggerFrInn0.grid(row=1, column=0, sticky='nsew')
        self.ifile = itk.PhotoImage(file=self.img_path('input_file.png'))
        self.pos_infile_butt = ttk.Button(pos_taggerFrInn0, padding=(2, 2),
                                          compound='left',
                                          image=self.ifile, text='Input file',
                                          command=self.load_file)
        self.pos_infile_butt.grid(row=0, column=0, sticky='we', pady=2, padx=2)
        # input file label
        self.pos_icon1 = itk.PhotoImage(file=self.img_path('unset.png'))
        self.pos_infile_labl = ttk.Label(pos_taggerFrInn0,
                                         image=self.pos_icon1,
                                         compound='left',
                                         text='Not set',
                                         font=TKFONT)
        self.pos_infile_labl.grid(row=0, column=1, sticky='we')
        # input file Button
        self.idir = itk.PhotoImage(file=self.img_path('input_dir.png'))
        self.pos_indir_butt = ttk.Button(pos_taggerFrInn0, padding=(2, 2),
                                         compound='left',
                                         image=self.idir,
                                         text='Input directory',
                                         command=self.load_input_dir)
        self.pos_indir_butt.grid(row=2, column=0, sticky='we', padx=2)
        # input dir label
        self.pos_icon2 = itk.PhotoImage(file=self.img_path('unset.png'))
        self.pos_indir_labl = ttk.Label(pos_taggerFrInn0,
                                        image=self.pos_icon2,
                                        compound='left',
                                        text='Not set',
                                        font=TKFONT)
        self.pos_indir_labl.grid(row=2, column=1, sticky='we')
        # output dir Button
        self.odir = itk.PhotoImage(file=self.img_path('out_dir.png'))
        self.pos_outdir_butt = ttk.Button(pos_taggerFrInn0, padding=(2, 2),
                                          compound='left',
                                          image=self.odir,
                                          text='Output directory',
                                          command=self.load_output_dir)
        self.pos_outdir_butt.grid(row=3, column=0, sticky='we', pady=2, padx=2)
        # output dir label
        self.pos_icon3 = itk.PhotoImage(file=self.img_path('unset.png'))
        self.pos_outdir_labl = ttk.Label(pos_taggerFrInn0,
                                         image=self.pos_icon3,
                                         compound='left',
                                         text='Not set',
                                         font=TKFONT)
        self.pos_outdir_labl.grid(row=3, column=1, sticky='we')

        # Process button
        pos_taggerFrInn1 = ttk.Frame(pos_taggerFr, borderwidth=2,
                                     relief='groove')
        pos_taggerFrInn1.grid(row=2, column=0, sticky='nsew')
        self.pos_runic = itk.PhotoImage(file=self.img_path('run_tagger.png'))
        self.pos_run_butt = ttk.Button(pos_taggerFrInn1, padding=(3, 3),
                                       compound='left',
                                       image=self.pos_runic,
                                       text='Process',
                                       command=self.pos_tagger_run)
        self.pos_run_butt.grid(row=0, column=0, sticky='we', pady=2)
        self.pos_run_butt.config(state='disabled')
        # Stop button
        self.pos_stopic = itk.PhotoImage(file=self.img_path('stop_tagger.png'))
        self.pos_stop_butt = ttk.Button(pos_taggerFrInn1, padding=(3, 3),
                                        compound='left',
                                        image=self.pos_stopic,
                                        text='Stop',
                                        command=self.kill_pos_proc)
        self.pos_stop_butt.grid(row=0, column=1, sticky='we', pady=2)
        self.pos_stop_butt.config(state='disabled')
        # Close button
        pos_taggerFrInn2 = ttk.Frame(pos_taggerFr, borderwidth=2, height=15,
                                     relief='flat')
        pos_taggerFrInn2.grid(row=3, column=0, sticky='nsew')
        self.pos_butt = ttk.Button(pos_taggerFr, padding=(0, 0), text='Close',
                                   command=self.tagger_win.destroy)
        self.pos_butt.grid(sticky='w')
        self.centrify_widget(self.tagger_win)

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

    def show_message(self, msg, icon, top=True):
        """
        Show a warning window with a given message.

        Args:
            | *msg* (str) -- a message to display
            | *icon* (str) -- icon name
            | *top* (bool) -- make message window on top

        """
        message = tk.Toplevel()
        # set custom window icon
        set_win_icon(message, self.img_path('warning.png'))
        message.title('Warning!')
        if top:
            message.wm_attributes('-topmost', 1)
        message.resizable(0, 0)
        warnFr0 = ttk.Frame(message, borderwidth=2, relief='groove')
        warnFr0.grid(sticky='nsew')
        warnFr1 = ttk.Frame(warnFr0, borderwidth=2, relief='groove')
        warnFr1.grid(sticky='nsew')
        ttk.Label(warnFr1, font='TkDefaultFont 12', text=msg).grid()
        self.err_img = itk.PhotoImage(file=self.img_path(icon))
        ttk.Label(warnFr1, image=self.err_img).grid()
        ttk.Button(warnFr0, padding=(0, 2), text='OK',
                   command=message.destroy, takefocus=True).grid()
        self.centrify_widget(message)

    def save_data(self):
        """
        Save Text widget contents
        """
        types = (("txt file", "*.txt"),
                 ("All files", "*.*"))
        try:
            opened_file = tkf.asksaveasfile(mode='w', filetypes=types)
        except (IOError, OSError):
            msg = 'Can not open the specified file!'
            self.show_message(msg, 'error.png')
            return
        try:
            text = self.Text.get('1.0', tk.END).encode('utf-8')
            opened_file.write(text)
        except AttributeError:
            return
        except (IOError, OSError):
            msg = 'Can not write the specified file!\n' + \
                  'Make sure there is enough free space on disk'
            self.show_message(msg, 'error.png')
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
            self.loaded_text = model.read_input_file(fpath)
            fname = os.path.basename(fpath)
            if len(fname) > 20:
                fname = fname[:17] + '...'
        except TypeError:  # when clicked Load and didn't choose any file
            return
        except (OSError, IOError):
            msg = "Can not open the specified file!"
            self.show_message(msg, 'warning.png')
            return
        # update the file stats
        self.current_fname = os.path.splitext(fname)[0]
        self.set_file_loaded(True)
        self.stats0.config(text="Name: {0}".format(fname))
        self.stats1.config(text="Size: {0}kb".format(round(fsize * 1024, 1)))
        # insert read text into Text widget
        self.insert_text(self.loaded_text)
        # reset text statistics after we loaded a new file
        self.set_stats_ready(False)
        self.set_graphs_ready(False)
        self.Text.edit_modified(False)

    def check_process_thread_save_results(self):
        """
        Check every 10ms if model thread is alive.
        Destroy progress bar when model thread finishes.
        Unlock UI widgets.
        """
        if self.process_thread.is_alive():
            self.after(50, self.check_process_thread_save_results)
        else:
            self.process_thread.join()
            # get the results of model processing
            self.process_results = self.model_queue.get()
            self.fully_tagged_sents = self.process_results[-1]
            self.progress_bar.stop()
            self.prog_win.destroy()
            self.lock_ui(False)

    def run_progressbar(self):
        """
        Run progress bar.
        """
        self.prog_win = tk.Toplevel()
        # set custom window icon
        set_win_icon(self.prog_win, self.img_path('cup.png'))
        self.prog_win.wm_attributes('-topmost', 1)  # keep window topmost
        self.prog_win.title('Processing')
        self.prog_win.resizable(0, 0)
        self.progFr = ttk.Frame(self.prog_win, borderwidth=2, relief='flat')
        self.progFr.grid(sticky='nsew')
        msg = "Exercise some patience..."
        ttk.Label(self.progFr, font=TKFONT, text=msg).grid()
        self.prog_img = itk.PhotoImage(file=self.img_path('cup.png'))
        ttk.Label(self.progFr, image=self.prog_img).grid()
        self.progress_bar = ttk.Progressbar(self.progFr, orient=tk.HORIZONTAL,
                                            length=200,
                                            mode='indeterminate',
                                            takefocus=True)
        self.progress_bar.grid()
        self.centrify_widget(self.prog_win)
        self.progress_bar.start()

    def process_command(self):
        """
        Start the indeterminate progress bar.
        Lock UI widgets.
        Process text loaded into Text widget.
        <Some UI widgets are connected to this function. The purpose of this
        function is to display a progress bar while running model functions in
        a separate thread>.
        """
        # if Text modified, update Name and Size
        if self.Text.edit_modified() or self.is_file_loaded:
            # update the file stats
            loaded_text = self.Text.get("1.0", 'end-1c')
            self.stats0.config(text="Name: {0}".format('Text field'))
            acc_size = round(len(loaded_text) / 1024, 1)
            self.stats1.config(text="Size: {0}kb".format(acc_size))
            # reset Text precaching
        else:
            self.show_message('No data provided!', 'error.png')
            self.set_processed(False)
            return

        self.lock_ui(True)
        self.run_progressbar()
        # now handle the Process button command
        self.process_thread = thr.Thread(target=model.process_text,
                                         args=(self.model_queue, loaded_text))
        self.process_thread.start()
        # check if model_thread finished
        self.after(50, self.check_process_thread_save_results)
        self.set_processed(True)
        self.set_stats_ready(False)
        self.set_graphs_ready(False)
        self.set_search_stats_ready(False)

    def check_stats_thread_save_results(self):
        """
        Check every 10ms if model thread is alive.
        While displaying waiting label in Toplevel.
        Unlock UI widgets.
        """
        self.lock_toplevel(self.stats_win_butt, True)
        self.stats_butt1.config(state='disabled')
        if self.stats_thread.is_alive():
            self.after(50, self.check_stats_thread_save_results)
        else:
            self.stats_thread.join()
            # get the results of model processing
            self.textstats = self.model_queue.get()
            # centering window position
            self.stats_win.title("Statistics")
            self.stats_win.resizable(0, 0)
            # update the information to calculated stats
            stats_text = self.num_rlabl.format(self.textstats.get('tokens'),
                                               self.textstats.get('words'),
                                               self.textstats.get('sents'),
                                               self.textstats.get('diversity'),
                                               self.textstats.get('subj'),
                                               self.textstats.get('polar'),
                                               self.textstats.get('corr'))
            self.update_idletasks()
            self.stats_win.geometry("")
            self.set_stats_ready(True)
            self.lock_toplevel(self.stats_win_butt, False)
            self.stats_butt1.config(state='normal')
            self.rtext.config(text=stats_text)

    def show_stats_win(self):
        """
        Create a new TopLevel window.
        Calculate text stats and insert them as Label widgets.
        Add "Close" button. Check if we already calculated stats, if yes then
        reuse instead of recalculating.

        <Numbers stats calculation is done in a separate Thread in order to
        leave UI responsive. This, however, makes the code that handles
        Numbers pop-up window look ugly and confusing.
        show_stats_win() invokes self.check_stats_thread_save_results() which
        checks whenever Thread is done, updates the Numbers pop-up window>
        """
        if self.processed and not self.stats_ready:
            self.model_queue = Queue.PriorityQueue()
            # now handle the Process button command
            self.stats_thread = thr.Thread(target=model.get_stats,
                                           args=(self.model_queue,
                                                 self.process_results[0]))
            self.stats_thread.start()
            stats = ('tokens', 'words', 'sents', 'diversity', 'subj', 'polar',
                     'corr')
            self.textstats = dict((stat, 'Wait...') for stat in stats)
            # check if model_thread finished
            self.after(50, self.check_stats_thread_save_results)
        elif not self.processed and (self.is_file_loaded or
                                     self.Text.edit_modified()):
            self.show_message('Please click "Process!" button',
                              'warning.png')
            return
        elif not self.processed and not (self.is_file_loaded or
                                         self.Text.edit_modified()):
            self.show_message('No data provided!', 'error.png')
            return
        # update the information to calculated stats
        stats_text = self.num_rlabl.format(self.textstats.get('tokens'),
                                           self.textstats.get('words'),
                                           self.textstats.get('sents'),
                                           self.textstats.get('diversity'),
                                           self.textstats.get('subj'),
                                           self.textstats.get('polar'),
                                           self.textstats.get('corr'))
        # create a pop-up window, use self instances, we need to update them
        self.stats_win = tk.Toplevel()
        # set custom window icon
        set_win_icon(self.stats_win, self.img_path('stats.png'))
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
        num_llabl = 'Tokens count:\nWords count:\nSentences count: \n' +\
                    '-------------------------------\n' +\
                    'Lexical diversity [0,1]:\nSubjectivity [0,1]: \n' +\
                    'Polarity [-1,1]: \nCorrectness [0,1]: \n'
        self.ltext = ttk.Label(self.statsFrInn1, font=TKFONT,
                               text=num_llabl)
        self.ltext.grid()
        self.rtext = ttk.Label(self.statsFrInn2, font='TkDefaultFont 10 bold',
                               text=stats_text)
        self.rtext.grid()
        self.stats_win_butt = ttk.Button(self.statsFr, text='Close',
                                         padding=(0, 0),
                                         command=self.stats_win.destroy)
        self.stats_win_butt.grid(sticky='w')
        self.centrify_widget(self.stats_win)

    def show_tags_help(self):
        """
        Show a pop-up window with Penn Treebank POS-tags description.
        """
        ids, tags, desc = self.penn_treebank
        header = ids[0], tags[0], desc[0]
        penn_win = tk.Toplevel()
        # set custom window icon
        set_win_icon(penn_win, self.img_path('info.png'))
        penn_win.title('Penn Treebank POS-tags')
        penn_win.resizable(0, 0)
        # creating Frames for headers
        pennFr = ttk.Frame(penn_win, borderwidth=2, relief='groove')
        pennFr.grid(sticky='nsew')
        pennFrInnHead0 = ttk.Frame(pennFr, borderwidth=2, relief='flat')
        pennFrInnHead0.grid(row=0, column=0)
        pennFrInnHead1 = ttk.Frame(pennFr, borderwidth=2, relief='flat')
        pennFrInnHead1.grid(row=0, column=1)
        pennFrInnHead2 = ttk.Frame(pennFr, borderwidth=2, relief='flat')
        pennFrInnHead2.grid(row=0, column=2)
        # creating Frames for ids, tags and desc
        pennFrInn0 = ttk.Frame(pennFr, borderwidth=2, relief='groove')
        pennFrInn0.grid(row=1, column=0)
        pennFrInn1 = ttk.Frame(pennFr, borderwidth=2, relief='groove')
        pennFrInn1.grid(row=1, column=1)
        pennFrInn2 = ttk.Frame(pennFr, borderwidth=2, relief='groove')
        pennFrInn2.grid(row=1, column=2)
        # inserting Labels
        ttk.Label(pennFrInnHead0, font='TkDefaultFont 10 bold',
                  text=header[0]).grid()
        ttk.Label(pennFrInnHead1, font='TkDefaultFont 10 bold',
                  text=header[1]).grid()
        ttk.Label(pennFrInnHead2, font='TkDefaultFont 10 bold',
                  text=header[2]).grid()
        ttk.Label(pennFrInn0, font=TKFONT,
                  text='\n'.join(ids[1:])).grid()
        ttk.Label(pennFrInn1, font='TkDefaultFont 10 bold',
                  text='\n'.join(tags[1:])).grid()
        ttk.Label(pennFrInn2, font=TKFONT,
                  text='\n'.join(desc[1:])).grid()
        # create Close button
        penn_butt = ttk.Button(pennFr, padding=(0, 0), text='Close',
                               command=penn_win.destroy)
        penn_butt.grid(column=2)
        self.centrify_widget(penn_win)

    def check_graphs_thread_save_results(self):
        """
        Check every 100ms if model thread is alive.
        While displaying waiting label in Toplevel.
        Unlock UI widgets.
        """
        if self.graphs_thread.is_alive():
            self.after(100, self.check_graphs_thread_save_results)
        else:
            self.graphs_thread.join()
            # get the results of model processing
            self.srt_tags = self.model_queue.get()
            self.ngrams = self.model_queue.get()
            self.set_graphs_ready(True)
            # remove "Wait" message
            self.waitFr.destroy()
            self.stats_butt2.config(state='normal')
            self.finish_graphs_window()

    def finish_graphs_window(self):
        """
        Finish building Graphs window when the results are ready.
        <Plotting, word/ngrams calculation etc. takes time. We first show
        'Wait...' Toplevel window and then fill it with the elements>.
        """
        # create Frames for Toplevel window
        graphFr = ttk.Frame(self.graphs_win, borderwidth=2, relief='groove')
        graphFr.grid(row=0, column=0, sticky='nsew')
        closeFr = ttk.Frame(self.graphs_win, borderwidth=2, relief='groove')
        closeFr.grid(row=1, column=0, sticky='nsew')
        graphFr0 = ttk.Frame(graphFr, borderwidth=2, relief='groove')
        graphFr0.grid(row=0, column=0, sticky='nsew')
        graphFr0Inn = ttk.Frame(graphFr0, borderwidth=2, relief='groove')
        graphFr0Inn.grid(row=1, column=0, sticky='nsew')
        graphFr1 = ttk.Frame(graphFr, borderwidth=2, relief='groove')
        graphFr1.grid(row=0, column=1, sticky='nsew')
        # graphFr2 will contain two inner Frames for pie charts and ngram cnts
        graphFr2 = ttk.Frame(graphFr, borderwidth=2, relief='groove')
        graphFr2.grid(row=0, column=2, sticky='nsew')
        graphFrInn0 = ttk.Frame(graphFr2, borderwidth=2, relief='groove')
        graphFrInn0.grid(row=0, column=0, sticky='nsew')
        graphFrInn1 = ttk.Frame(graphFr2, borderwidth=2, relief='groove')
        graphFrInn1.grid(row=1, column=0, sticky='nsew')
        ngramsFr = ttk.Frame(graphFrInn0, borderwidth=2, relief='groove')
        ngramsFr.grid(row=1, column=0, sticky="nsew")
        # add buttons
        self.pos_img = itk.PhotoImage(file=self.img_path('info.png'))
        tag_help = ttk.Button(graphFr0, padding=(0, 0),
                              text='POS-tags help', image=self.pos_img,
                              compound='left', command=self.show_tags_help)
        tag_help.grid(row=0, sticky='we')
        # add Close button
        close_butt = ttk.Button(closeFr, padding=(0, 0), text='Close',
                                command=self.graphs_win.destroy)
        close_butt.grid(sticky='w')
        # extract POS-tags, occurences, calculate ratio
        self.tgs = '\n'.join([k for k in self.srt_tags])
        self.tgs_cnts = '\n'.join([str(v) for v in self.srt_tags.values()])
        total_cnt = sum([v for v in self.srt_tags.values()])
        self.ratios = '\n'.join([str(round(v/total_cnt*100, 1)) + '%' for v
                                   in self.srt_tags.values()])
        # create two inner Frames, one for POS-tags, another for counts
        graphFr0Inn0 = ttk.Frame(graphFr0Inn, borderwidth=2, relief='groove')
        graphFr0Inn0.grid(row=0, column=0, sticky='nsew')
        graphFr0Inn1 = ttk.Frame(graphFr0Inn, borderwidth=2, relief='groove')
        graphFr0Inn1.grid(row=0, column=1, sticky='nsew')
        graphFr0Inn2 = ttk.Frame(graphFr0Inn, borderwidth=2, relief='groove')
        graphFr0Inn2.grid(row=0, column=2, sticky='nsew')
        # insert POS-tags, counts and ratios
        ttk.Label(graphFr0Inn0, font=TKFONT, text=self.tgs).grid()
        ttk.Label(graphFr0Inn1, font='TkDefaultFont 10 bold',
                  text=self.tgs_cnts).grid()
        ttk.Label(graphFr0Inn2, font=TKFONT,
                  text=self.ratios).grid()
        # insert POS-tags plot
        plot1_path = os.path.join('_graphs', self.current_fname + '.png')
        image = itk.Image.open(plot1_path)
        image = image.resize((550, 500), itk.Image.ANTIALIAS)
        self.plot1 = itk.PhotoImage(image)
        # self.plot1 = itk.PhotoImage(file=plot_path)
        plot1Label = ttk.Label(graphFr1, image=self.plot1)
        plot1Label.grid(row=0, column=0, sticky="nsew")
        # insert functional/content words pie chart
        pie_path = os.path.join('_graphs', self.current_fname + '_pie.png')
        pie_image = itk.Image.open(pie_path)
        pie_image = pie_image.resize((400, 300), itk.Image.ANTIALIAS)
        self.pie_plot = itk.PhotoImage(pie_image)
        pie_header = "Functional vs content words ratio"
        ttk.Label(graphFrInn1, font='TkDefaultFont 10 bold',
                  text=pie_header).grid(row=0)
        plot2Label = ttk.Label(graphFrInn1, image=self.pie_plot)
        plot2Label.grid(row=1, column=0, sticky="nsew")
        # insert ngrams stats
        top5, top5_cnts = zip(*[['"' + r[0] + '"', str(r[1])]
                                for r in self.ngrams[0]])
        top5 = '\n'.join(top5)
        top5_cnts = '\n'.join(top5_cnts)
        ngram2, ngram2_cnts = zip(*[['"' + ' '.join(r[0]) + '"', str(r[1])]
                                    for r in self.ngrams[1]])
        ngram3, ngram3_cnts = zip(*[['"' + ' '.join(r[0]) + '"', str(r[1])]
                                    for r in self.ngrams[2]])
        ngram2 = '\n'.join(ngram2)
        ngram2_cnts = '\n'.join(ngram2_cnts)
        ngram3 = '\n'.join(ngram3)
        ngram3_cnts = '\n'.join(ngram3_cnts)
        # create inner Frames for ngrams header
        headerFr = ttk.Frame(graphFrInn0, borderwidth=0, relief='flat')
        headerFr.grid(row=0, sticky='we')
        head_msg = "Top 10 words, 2-grams, 3-grams and their counts"
        ttk.Label(headerFr, font='TkDefaultFont 10 bold',
                  text=head_msg).grid(row=0, column=1)
        # for top5 ngrams
        ngramFrInn0 = ttk.Frame(ngramsFr, borderwidth=2, relief='groove')
        ngramFrInn0.grid(row=1, column=0, sticky='nsew')
        ngramFrInn1 = ttk.Frame(ngramsFr, borderwidth=2, relief='groove')
        ngramFrInn1.grid(row=1, column=1, sticky='nsew')
        # for ngram2
        ngramFrInn2 = ttk.Frame(ngramsFr, borderwidth=2, relief='groove')
        ngramFrInn2.grid(row=1, column=2, sticky='nsew')
        ngramFrInn3 = ttk.Frame(ngramsFr, borderwidth=2, relief='groove')
        ngramFrInn3.grid(row=1, column=3, sticky='nsew')
        # for ngram3
        ngramFrInn4 = ttk.Frame(ngramsFr, borderwidth=2, relief='groove')
        ngramFrInn4.grid(row=1, column=4, sticky='nsew')
        ngramFrInn5 = ttk.Frame(ngramsFr, borderwidth=2, relief='groove')
        ngramFrInn5.grid(row=1, column=5, sticky='nsew')
        # inserting ngram counts
        ttk.Label(ngramFrInn0, font=TKFONT, text=top5).grid()
        ttk.Label(ngramFrInn1, font='TkDefaultFont 10 bold',
                  text=top5_cnts).grid()
        ttk.Label(ngramFrInn2, font=TKFONT, text=ngram2).grid()
        ttk.Label(ngramFrInn3, font='TkDefaultFont 10 bold',
                  text=ngram2_cnts).grid()
        ttk.Label(ngramFrInn4, font=TKFONT, text=ngram3).grid()
        ttk.Label(ngramFrInn5, font='TkDefaultFont 10 bold',
                  text=ngram3_cnts).grid()
        # update and reset window size, tkinter will adjust
        self.graphs_win.update_idletasks()
        self.graphs_win.geometry('')
        self.graphs_win.minsize(120, 300)  # FIX: limit max size
        self.centrify_widget(self.graphs_win)
        self.graphs_win.update()
        # limit max size using current
        x, y = self.graphs_win.winfo_geometry().split('+')[0].split('x')
        self.graphs_win.maxsize(int(x), int(y))

    def mk_graphs_win(self):
        """
        Check if graphs have already been calculated.
        Create necessary UI elements that will contain the plots and stats.
        Start a separate thread to create plots and calculate word/ngram
        counts.
        """
        # create a Toplevel first, we will update it later
        self.graphs_win = tk.Toplevel()
        # set custom window icon
        set_win_icon(self.graphs_win, self.img_path('stats2.png'))
        self.graphs_win.title('Graphs')
        if self.processed and not self.graphs_ready:
            self.stats_butt2.config(state='disabled')
            self.waitFr = ttk.Frame(self.graphs_win, borderwidth=2,
                                relief='groove')
            self.waitFr.grid(sticky='nsew')
            ttk.Label(self.waitFr,
                      font='TkDefaultFont 12',
                      text='Wait... Creating plots...').grid()
            self.wait_img = itk.PhotoImage(file=self.img_path('cup.png'))
            ttk.Label(self.waitFr, image=self.wait_img).grid()
            self.centrify_widget(self.graphs_win)
            self.model_queue = Queue.PriorityQueue()
            tags_dic = Counter((tup[1] for tup
                                in self.process_results[0].tags))
            # now handle the Process button command
            self.graphs_thread = thr.Thread(target=model.get_graphs_data,
                                            args=(self.model_queue, tags_dic,
                                                  self.current_fname,
                                                  self.process_results))
            self.graphs_thread.start()
            # check if model_thread finished
            self.after(100, self.check_graphs_thread_save_results)
        elif not self.processed and (self.is_file_loaded
                                     or self.Text.edit_modified()):
            self.graphs_win.destroy()
            self.show_message('Please click "Process!" button',
                              'warning.png')
            return
        elif not self.processed and not (self.is_file_loaded
                                         or self.Text.edit_modified()):
            self.graphs_win.destroy()
            self.show_message('No data provided!', 'error.png')
            return
        else:
            # self.graphs_win.resizable(0, 0)
            self.graphs_win.minsize(120, 300)
            self.finish_graphs_window()

    def check_search_stats_thread_save_results(self):
        """
        Check every 10ms if model thread is alive.
        While displaying waiting label in Toplevel.
        Unlock UI widgets.
        """
        self.lock_toplevel(self.sstats_win_butt, True)
        self.stats_butt2.config(state='disabled')
        if self.sstats_thread.is_alive():
            self.after(10, self.check_search_stats_thread_save_results)
        else:
            self.sstats_thread.join()
            # get the results of model processing
            self.sstats = self.model_queue.get()
            # centering window position
            # update the information to calculated stats
            tmatched = self.sstats.get('Tokens matched')
            mlength = self.sstats.get('Matched length')
            mlratio = self.sstats.get('Matched length ratio')
            sstats_text = self.ss_rlabl.format(tmatched, mlength, mlratio)
            self.update_idletasks()
            self.sstats_win.geometry("")
            self.set_search_stats_ready(True)
            self.lock_toplevel(self.sstats_win_butt, False)
            self.stats_butt2.config(state='normal')
            self.ss_rtext.config(text=sstats_text)

    def show_search_stats_win(self):
        """
        Show a window with statistics for a query search.
        Search stats:
            number of matched terms
            length of all matched strings
            % of matched data to all search corpus
        """
        if not self.matches:
            msg = 'Please provide a search query!'
            self.show_message(msg, 'warning.png')
            return
        # handle exceptions
        if self.processed and not self.sstats_ready:
            self.model_queue = Queue.PriorityQueue()
            # now handle the Process button command
            text = self.Text.get('1.0', tk.END)
            self.sstats_thread = thr.Thread(target=model.get_search_stats,
                                            args=(self.model_queue,
                                                  self.matches, text))
            self.sstats_thread.start()
            sstats = ('Tokens matched', 'Matched length',
                      'Matched length ratio')
            self.sstats = dict((stat, 'Wait...') for stat in sstats)
            # check if model_thread finished
            self.after(10, self.check_search_stats_thread_save_results)
        elif not self.processed and (self.Text.edit_modified() or
                                     self.is_file_loaded):
            self.show_message('Please click "Process!" button', 'warning.png')
            return
        elif not self.processed and (not self.Text.edit_modified() and
                                     not self.is_file_loaded):
            self.show_message('No data provided!', 'error.png')
            return
        ss_text = self.ss_rlabl.format(self.sstats.get('Tokens matched'),
                                       self.sstats.get('Matched length'),
                                       self.sstats.get('Matched length ratio'))
        # build a Toplevel window
        self.sstats_win = tk.Toplevel()
        # set custom window icon
        set_win_icon(self.sstats_win, self.img_path('stats3.png'))
        # centering window position
        self.sstats_win.resizable(0, 0)
        self.sstats_win.title("Search statistics")
        self.sstatsFr = ttk.Frame(self.sstats_win, borderwidth=2,
                                  relief='groove')
        self.sstatsFr.grid()
        self.sstatsFrInn1 = ttk.Frame(self.sstatsFr, borderwidth=2,
                                      relief='groove')
        self.sstatsFrInn1.grid(row=0, column=0, sticky='ns')
        self.sstatsFrInn2 = ttk.Frame(self.sstatsFr, borderwidth=2,
                                      relief='groove')
        self.sstatsFrInn2.grid(row=0, column=1, sticky='ns')
        ss_llabl = 'Tokens matched:\nMatched length:\n' +\
                   'Matched length / full text [0,1]:\n'
        self.ss_ltext = ttk.Label(self.sstatsFrInn1, font=TKFONT,
                                  text=ss_llabl)
        self.ss_ltext.grid()
        self.ss_rtext = ttk.Label(self.sstatsFrInn2, font='TkDefaultFont 10 bold',
                                  text=ss_text)
        self.ss_rtext.grid()
        self.sstats_win_butt = ttk.Button(self.sstatsFr, text='Close',
                                          padding=(0, 0),
                                          command=self.sstats_win.destroy)
        self.sstats_win_butt.grid(sticky='w')
        self.centrify_widget(self.sstats_win)

    def insert_matches(self, matched, hl_type):
        """
        Insert and highlight text matches according to selected UI options.

        Args:
            | *matched* -- Orderedict of matched tokens
            | *hl_type* -- type of highlighting, single token or range

        """
        # This is a green tree. The tree is big. The monument is black.
        pos_tags, text_view = self.get_opts()
        # if view is 1, no need to insert text, it has been loaded already
        if text_view == 1:
            self.mark_tokens1(matched, hl_type, pos_tags)
            self.highlight1()
        elif text_view == 2:
            self.mark_tokens2(matched, hl_type, pos_tags)
            self.highlight2()
        elif text_view == 3:
            self.mark_tokens3(matched, hl_type, pos_tags)
            self.highlight3()

    def prepare_view12(self, matched):
        """
        Precache text data for various text views.
        <This is done in order to stop recalculating text each time during
        results insertion.>

        Args:
            | *matched* -- dict of matched tokens

        """
        # There is a big tree. The road is long. The sea is wid. The sky is blue.
        # prepare for view1
        view1_text_pos = ''
        for key, values in self.process_results[1].items():
            text = ['_'.join([value[0], value[1]]) for value in values]
            view1_text_pos = ' '.join([view1_text_pos, ' '.join(text)])
        self.view1_text_pos = view1_text_pos.lstrip(' ')

        # prepare for view2
        # first see which sent has query matches and include only those
        matched_ids =  [sent_id for sent_id in matched
                        for tokens in matched[sent_id] if tokens]
        view2_text = ''
        for sent_id, sent_lst in self.process_results[1].items():
            if sent_id not in matched_ids:
                continue
            sent = ' '.join([token[0] for token in sent_lst])
            text = ': '.join([str(sent_id), sent])
            view2_text = '\n\n'.join([view2_text, text])
        self.view2_text = view2_text.lstrip('\n\n')   # remove first \n\n
        # prepare for view2 with POS-tags
        view2_text = ''
        for sent_id, sent_lst in self.process_results[1].items():
            if sent_id not in matched_ids:
                continue
            sent = ' '.join(['_'.join([token[0], token[1]])
                             for token in sent_lst])
            text = ': '.join([str(sent_id), sent])
            view2_text = '\n\n'.join([view2_text, text])
        self.view2_text_pos = view2_text.lstrip('\n\n')

    def prepare_view3(self, matched):
        """
        Precache text data for various text views.
        <This is done in order to stop recalculating text each time during
        results insertion.>

        Args:
            | *matched* -- Ordereddict of matched tokens

        """
        # prepare text for view3, plain and with pos-tags
        cnt = 0
        view3_plain = []
        view3_pos = []
        for sent_lst in matched.values():
            for tokens in sent_lst:
                cnt += 1
                # plain
                view3_plain.append(': '.join([str(cnt),
                                              ' '.join([token[0]
                                                        for token in tokens])]))
                # pos-tags included
                view3_pos.append(': '.join([str(cnt),
                                            ' '.join(['_'.join([token[0],
                                                                token[1]])
                                                      for token in tokens])]))
                self.view3_text = '\n'.join(view3_plain)
                self.view3_text_pos = '\n'.join(view3_pos)

    def mark_tokens1(self, matched, single, pos):
        """
        Using results of a query match add text tags.
        Highlighting view 1, just plain loaded text.
        <tk.Text.search returns only the beginning of a match, thats why we
        need to '+%dc' to the starting match index.>

        Args:
            | *matched* -- dict of matched results
            | *single* -- True if single match
            | *pos* -- True if add POS-tags

        """
        # This is a green tree. The tree is big. The monument is black.
        self.Text.tag_delete('style')  # reset highighting
        start = '1.0'
        first = True
        end_mark = '1.0'
        # reload text
        self.Text.delete('1.0', 'end')  # remove text
        if pos:
            self.insert_text(self.view1_text_pos)
        else:
            self.insert_text(self.process_results[0])
        # start_mark = '1.0'
        sents_matches = [toks for sent_lst in matched.values() for toks in sent_lst]
        for tokens in sents_matches:
            if not tokens:
                continue
            sent_limit = True
            for token in tokens:
                if not pos:
                    token = ''.join([r'\y', re.escape(token[0]), r'\y'])
                else:
                    token = ''.join([r'\y', re.escape(token[0]), '_',
                                     re.escape(token[1]), r'\y'])
                # get start index, search returns only first match
                temp_mark = self.Text.search(token, start, stopindex=tk.END,
                                             regexp=True)
                if not temp_mark:
                    break
                token_len = len(token) - 4
                end_mark = '%s+%dc' % (temp_mark, token_len)
                # highlight range or single token
                if single:
                    start_mark = temp_mark
                # break highlight between sents
                if sent_limit:
                    start_mark = temp_mark
                    sent_limit = False
                # remember last matched position
                start = end_mark
                # mark first token
                if first:
                    start_mark = temp_mark
                    start = end_mark + '+1c'  # plus one character
                    first = False
                self.Text.tag_add('style', start_mark, end_mark)

    def mark_tokens2(self, matched, single, pos):
        """
        Using results of a query match add text tags.
        Highlighting view 2, formatted text into sentence blocks.
        <tk.Text.search returns only the beginning of a match, thats why we
        need to '+%dc' to the starting match index.>

        Args:
            | *matched* -- dict of matched results
            | *single* -- True if single match
            | *pos* -- True if add POS-tags

        """
        self.Text.tag_delete('style')  # reset highighting
        start = '1.0'
        first = True
        view2_text = ''
        for sent_id, sent_lst in self.process_results[1].items():
            sent = ' '.join([token[0] for token in sent_lst])
            text = ': '.join([str(sent_id), sent])
            view2_text = '\n\n'.join([view2_text, text])
        # reload text
        self.Text.delete('1.0', 'end')  # remove text
        if pos:
            self.Text.insert('1.0', self.view2_text_pos)
        else:
            self.Text.insert('1.0', self.view2_text)
        sents_matches = [toks for sent_lst in matched.values() for toks in sent_lst]
        for tokens in sents_matches:
            if not tokens:
                continue
            sent_limit = True
            for token in tokens:
                if not pos:
                    token = ''.join([r'\y', re.escape(token[0]), r'\y'])
                else:
                    token = ''.join([r'\y', re.escape(token[0]), '_',
                                     re.escape(token[1]), r'\y'])
                # get start index, search returns only first match
                temp_mark = self.Text.search(token, start, stopindex=tk.END,
                                             regexp=True)
                if not temp_mark:
                    break
                token_len = len(token) - 4
                end_mark = '%s+%dc' % (temp_mark, token_len)
                # highlight range or single token
                if single:
                    start_mark = temp_mark
                # break highlight between sents
                if sent_limit:
                    start_mark = temp_mark
                    sent_limit = False
                # remember last matched position
                start = end_mark
                # mark first token
                if first:
                    start_mark = temp_mark
                    start = end_mark + '+ 1c'  # plus one character
                    first = False
                self.Text.tag_add('style', start_mark, end_mark)

    def mark_tokens3(self, matched, single, pos):
        """
        Using results of a query match add text tags.
        Highlighting view 3, display only matched tokens.
        <tk.Text.search returns only the beginning of a match, thats why we
        need to '+%dc' to the starting match index.>

        Args:
            | *matched* -- dict of matched results
            | *single* -- True if single match
            | *pos* -- True if add POS-tags

        """
        self.Text.tag_delete('style')  # reset highighting
        start = '1.0'
        first = True
        # reload text
        self.Text.delete('1.0', 'end')  # remove text
        if pos:
            self.Text.insert('1.0', self.view3_text_pos)
        else:
            self.Text.insert('1.0', self.view3_text)
        sents_matches = [toks for sent_lst in matched.values() for toks in sent_lst]
        for tokens in sents_matches:
            if not tokens:
                continue
            sent_limit = True
            for token in tokens:
                if not pos:
                    token = ''.join([r'\y', re.escape(token[0]), r'\y'])
                else:
                    token = ''.join([r'\y', re.escape(token[0]), '_',
                                     re.escape(token[1]), r'\y'])
                # get start index, search returns only first match
                temp_mark = self.Text.search(token, start, stopindex=tk.END,
                                             regexp=True)
                if not temp_mark:
                    break
                token_len = len(token) - 4
                end_mark = '%s+%dc' % (temp_mark, token_len)
                # highlight range or single token
                if single:
                    start_mark = temp_mark
                # break highlight between sents
                if sent_limit:
                    start_mark = temp_mark
                    sent_limit = False
                # remember last matched position
                start = end_mark
                # mark first token
                if first:
                    start_mark = temp_mark
                    start = end_mark + '+ 1c'  # plus one character
                    first = False
                self.Text.tag_add('style', start_mark, end_mark)

    def highlight1(self):
        """
        Apply highlighting style for view 1
        """
        self.Text.tag_configure('style', foreground='#000000',
                                background='#C0FA82')

    def highlight2(self):
        """
        Apply highlighting style view 2
        """
        self.Text.tag_configure('style', foreground='#000000',
                                background="#BCFC77",
                                font='TkDefaultFont 10 bold')

    def highlight3(self):
        """
        Apply highlighting style view 3
        """
        self.Text.tag_configure('style', font='TkDefaultFont 11 bold')

    def show_about(self):
        """
        Display About window
        """
        about = ['nn-search v.2.0.0',
                 'Built with nltk, TextBlob and matplotlib',
                 'tastyminerals@gmail.com ']
        about_win = tk.Toplevel()
        about_win.title('About')
        # set custom window icon
        set_win_icon(about_win, self.img_path('info.png'))
        about_win.resizable(0, 0)
        # creating Frames for headers
        aboutFr = ttk.Frame(about_win, borderwidth=2, relief='groove')
        aboutFr.grid(sticky='nsew')
        aboutFrInn0 = ttk.Frame(aboutFr, borderwidth=2, relief='groove')
        aboutFrInn0.grid(row=0, column=0)
        # inserting Labels
        ttk.Label(aboutFrInn0, font='TkDefaultFont 10 bold',
                  text=about[0]).grid()
        self.nn_icon = itk.PhotoImage(file=self.img_path('nn-search.png'))
        ttk.Label(aboutFrInn0, image=self.nn_icon).grid()
        ttk.Label(aboutFrInn0, font=TKFONT,
                  text=about[1]).grid(sticky='we')
        email = about[2]
        email_str = tk.StringVar()
        email_str.set(email)
        contact = tk.Entry(aboutFrInn0, state='readonly', relief='flat',
                           fg='#0000FF', width=22, textvariable=email_str)
        contact.grid()
        about_butt = ttk.Button(aboutFr, padding=(0, 0), text='Close',
                                command=about_win.destroy)
        about_butt.grid()
        self.centrify_widget(about_win)

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
        self.load = itk.PhotoImage(file=self.img_path('load.png'))
        self.Menu0.add_command(label="Load", image=self.load, compound='left',
                               command=self.load_data)
        self.save = itk.PhotoImage(file=self.img_path('disk.png'))
        self.Menu0.add_command(label="Save", image=self.save, compound='left',
                               command=self.save_data)
        # self.save2 = itk.PhotoImage(file=self.img_path('disk2.png'))
        # self.Menu0.add_command(label="Save as", image=self.save2,
        #                       compound='left', command=self.save_data)
        self.exit = itk.PhotoImage(file=self.img_path('exit.png'))
        self.Menu0.add_command(label="Exit", image=self.exit, compound='left',
                               command=self.quit)
        put_resizable(self.MenuButton0, 0, 0, 1, 1, 'n')
        # make "Edit" menu
        self.Menu1 = tk.Menu(self.MenuFrm, tearoff=False)
        self.MenuButton1 = ttk.Menubutton(self.MenuFrm, text='Edit',
                                          direction='below',
                                          menu=self.Menu1)
        self.copy = itk.PhotoImage(file=self.img_path('copy.png'))
        self.Menu1.add_command(label="Copy (Ctrl-c)", image=self.copy,
                               compound='left', command=self.ctrl_c)
        self.cut = itk.PhotoImage(file=self.img_path('cut.png'))
        self.Menu1.add_command(label="Cut (Ctrl-x)", image=self.cut,
                               compound='left', command=self.ctrl_x)
        self.paste = itk.PhotoImage(file=self.img_path('paste.png'))
        self.Menu1.add_command(label="Paste (Ctrl-v)", image=self.paste,
                               compound='left', command=self.ctrl_v)
        self.undo = itk.PhotoImage(file=self.img_path('undo.png'))
        self.Menu1.add_command(label="Undo (Ctrl-z)", image=self.undo,
                               compound='left', command=self.ctrl_z)
        self.redo = itk.PhotoImage(file=self.img_path('redo.png'))
        self.Menu1.add_command(label="Redo (Ctrl-u)", image=self.redo,
                               compound='left', command=self.ctrl_u)
        put_resizable(self.MenuButton1, 0, 1, 1, 1, 'n')
        # make "Tools" menu
        self.Menu2 = tk.Menu(self.MenuFrm, tearoff=False)
        self.MenuButton2 = ttk.Menubutton(self.MenuFrm, text='Tools',
                                          direction='below',
                                          menu=self.Menu2)
        self.tagger = itk.PhotoImage(file=self.img_path('wand.png'))
        self.Menu2.add_command(label="POS-tagger", image=self.tagger,
                               compound='left', command=self.pos_tagger_win)
        put_resizable(self.MenuButton2, 0, 2, 1, 1, 'n')
        # make "Help" menu
        self.Menu3 = tk.Menu(self.MenuFrm, tearoff=False)
        self.MenuButton3 = ttk.Menubutton(self.MenuFrm, text='Help',
                                          direction='below',
                                          menu=self.Menu3)
        self.help = itk.PhotoImage(file=self.img_path('help.png'))
        self.Menu3.add_command(label="Help", image=self.help, compound='left',
                               command=None)
        self.about = itk.PhotoImage(file=self.img_path('info.png'))
        self.Menu3.add_command(label="POS-tags", image=self.about,
                               compound='left', command=self.show_tags_help)
        self.Menu3.add_command(label="About", image=self.about,
                               compound='left', command=self.show_about)
        put_resizable(self.MenuButton3, 0, 3, 1, 1, 'n')
        # make a frame for query input widget
        self.EntryFrm = ttk.Frame(self.Main, borderwidth='2', relief='groove')
        put_resizable(self.EntryFrm, 1, 0, 1, 1, 'we')
        # make entry widget inside entry frame
        self.Entry = ttk.Entry(self.EntryFrm, font='TkDefaultFont 12')
        self.Entry.grid(row=1, column=0, columnspan=1, **options)
        self.Entry.bind('<Control-a>', self.ctrl_a)
        self.Entry.bind('<Control-d>', self.ctrl_d)
        self.Entry.bind('<Control-z>', self.ctrl_z)
        self.Entry.bind('<Control-u>', self.ctrl_u)
        self.Entry.bind('<Return>', self.press_return, '+')
        self.Entry.focus()  # <Return> enable when entry widget in focus
        # make search button
        self.search = itk.PhotoImage(file=self.img_path('search.png'))
        self.search_butt= ttk.Button(self.EntryFrm, padding=(-5,0),
                                     text='Search', image=self.search,
                                     compound='left',
                                     command=self.press_return)
        self.search_butt.grid(row=1, column=1, **options)
        # make text frame
        self.TextFrm = ttk.Frame(self.Main, borderwidth=2, relief='groove')
        put_resizable(self.TextFrm, 2, 0, 1, 1, 'nsew')
        # make text widget
        self.Text = tk.Text(self.TextFrm, font=TKTEXT_FONT, height=35,
                            width=100,
                            undo=True,
                            takefocus=0)
        put_resizable(self.Text, 2, 0, 1, 1, 'nsew')
        self.Text.bind('<Control-a>', self.ctrl_a)
        self.Text.bind('<Control-d>', self.ctrl_d)
        self.Text.bind('<Control-s>', self.ctrl_s)
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
                              text='File operations')
        self.flab.grid(row=0)
        # make "Load", "Process" and "Save" buttons for right frame
        self.load_butt = ttk.Button(self.InnerRightFrm0, padding=(0, 0),
                                    text='Load', image=self.load,
                                    compound='left', command=self.load_data)
        self.load_butt.grid(row=1, column=0, sticky='nwe', padx=1, pady=1)
        self.proimg = itk.PhotoImage(file=self.img_path('proc.png'))
        self.proc_butt = ttk.Button(self.InnerRightFrm0, padding=(5, 5),
                                    text='Process!', image=self.proimg,
                                    compound='left',
                                    command=self.process_command)
        self.proc_butt.grid(row=2, column=0, sticky='nwe', pady=1, padx=1)
        self.save_butt = ttk.Button(self.InnerRightFrm0, padding=(0, 0),
                                    text='Save', image=self.save,
                                    compound='left', command=self.save_data)
        self.save_butt.grid(row=3, column=0, sticky='nwe', padx=1, pady=1)
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
        self.view1 = itk.PhotoImage(file=self.img_path('view1.png'))
        self.view1Radio = ttk.Radiobutton(self.InnerRightFrm1,
                                          image=self.view1,
                                          variable=self.view_opts,
                                          value=1)
        self.view1Radio.grid(row=1)
        self.view1Radio.invoke()  # make active by default
        self.view2 = itk.PhotoImage(file=self.img_path('view2.png'))
        self.view2Radio = ttk.Radiobutton(self.InnerRightFrm1,
                                          image=self.view2,
                                          variable=self.view_opts,
                                          value=2)
        self.view2Radio.grid(row=2)
        self.view3 = itk.PhotoImage(file=self.img_path('view3.png'))
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
        self.simg1 = itk.PhotoImage(file=self.img_path('stats.png'))
        self.stats_butt1 = ttk.Button(self.InnerRightFrm2, padding=(0, 0),
                                      text='Numbers', image=self.simg1,
                                      compound='left',
                                      command=self.show_stats_win)
        self.stats_butt1.grid(row=2, column=0, sticky='nwe', pady=1, padx=1)

        self.simg2 = itk.PhotoImage(file=self.img_path('stats2.png'))
        self.stats_butt2 = ttk.Button(self.InnerRightFrm2, padding=(0, 0),
                                      text='Graphs', image=self.simg2,
                                      compound='left',
                                      command=self.mk_graphs_win)
        self.stats_butt2.grid(row=3, column=0, sticky='nwe', pady=1, padx=1)
        self.simg3 = itk.PhotoImage(file=self.img_path('stats3.png'))
        self.stats_butt3 = ttk.Button(self.InnerRightFrm2, padding=(0, 0),
                                      text='Search stats', image=self.simg3,
                                      compound='left',
                                      command=self.show_search_stats_win)
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

        Args:
            *lock* (bool) -- disable widgets if True

        """
        if lock:
            self.MenuButton0.config(state='disabled')
            self.MenuButton1.config(state='disabled')
            self.MenuButton2.config(state='disabled')
            self.MenuButton3.config(state='disabled')
            self.view1Radio.config(state='disabled')
            self.view2Radio.config(state='disabled')
            self.view3Radio.config(state='disabled')
            self.tags_butt.config(state='disabled')
            self.search_butt.config(state='disabled')
            self.load_butt.config(state='disabled')
            self.save_butt.config(state='disabled')
            self.proc_butt.config(state='disabled')
            self.stats_butt1.config(state='disabled')
            self.stats_butt2.config(state='disabled')
            self.stats_butt3.config(state='disabled')
        else:
            self.MenuButton0.config(state='normal')
            self.MenuButton1.config(state='normal')
            self.MenuButton2.config(state='normal')
            self.MenuButton3.config(state='normal')
            self.view1Radio.config(state='normal')
            self.view2Radio.config(state='normal')
            self.view3Radio.config(state='normal')
            self.tags_butt.config(state='normal')
            self.search_butt.config(state='normal')
            self.load_butt.config(state='normal')
            self.save_butt.config(state='normal')
            self.proc_butt.config(state='normal')
            self.stats_butt1.config(state='normal')
            self.stats_butt2.config(state='normal')
            self.stats_butt3.config(state='normal')

    def lock_toplevel(self, toplevel_win_widget, lock):
        """
        Lock Toplevel widgets in order to prevent a user from closing it.

        Args:
            |*toplevel_win_widget* (ttk.Button) -- Toplevel Button widget
            |*lock* (bool) -- disable widgets if True

        """
        if lock:
            toplevel_win_widget.config(state='disabled')
        else:
            toplevel_win_widget.config(state='normal')

    def clean_up(self):
        """
        Remove all plot files in '_graphs' dir upon initialization.
        """
        try:
            shutil.rmtree('_graphs')
        except (OSError, IOError):
            print "WARNING: Cannot remove '_graphs' directory!"
        try:
            shutil.os.mkdir('_graphs')
        except (OSError, IOError):
            print "WARNING: Cannot create '_graphs' directory!"
            sys.exit(1)

    def get_opts(self):
        """
        Return UI selected widget values.
        """
        return self.show_tags.get(), self.view_opts.get()

    def img_path(self, icon_name):
        """
        Return a full path with an icon name.

        Args:
            *icon_name* (str) -- icon name

        """
        return os.path.join('data', 'icons', icon_name)

    def set_stats_ready(self, state):
        """
        Getter/Setter for self.stats_ready var

        Args:
            *state* (bool) -- True, if text statistics was calculated
        """
        self.stats_ready = state

    def set_graphs_ready(self, state):
        """
        Getter/Setter for self.graphs_ready var

        Args:
            *state* (bool) -- True, if graphs were plotted
        """
        self.graphs_ready = state

    def set_search_stats_ready(self, state):
        """
        Getter/Setter for self.graphs_ready var

        Args:
            *state* (bool) -- True, if graphs were plotted
        """
        self.sstats_ready = state

    def set_file_loaded(self, state):
        """
        Getter/Setter for self.is_file_loaded var

        Args:
            *state* (bool) -- True, if file was loaded
        """
        self.is_file_loaded = state

    def set_processed(self, state):
        """
        Getter/Setter for self.processed var

        Args:
            *state* (bool) -- True, if 'Processed!' was clicked
        """
        self.processed = state


def main():
    root = tk.Tk()
    root.title('nn-search2')
    # set a custom window icon
    win_icon_path = os.path.join(os.getcwd(), 'data', 'icons', 'nn-search.ico')
    set_win_icon(root, win_icon_path)
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
