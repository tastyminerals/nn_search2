#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
Created on Fri Nov 06 20:00:00 2015
@author: tastyminerals@gmail.com
"""

from __future__ import division
import os
import re
import sys
import ttk
import Tkinter as tk
from textblob import Blobber
from textblob_aptagger import PerceptronTagger
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
        self.build_gui()

    def build_gui(self):
        """
        Create user interface including all necessary components like Frames,
        Buttons, Labels etc.
        """
        pass


def main():
    # blob = Blobber(pos_tagger=PerceptronTagger())
    # tagged_sent = blob("This is an empty space of darkness.")
    # print tagged_sent.tags
    root = tk.Tk()
    root.title('nn-search 2.0')
    root.geometry("1100x630")  # gui size at startup
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    root.resizable(True, True)
    root.update()
    ttk_theme = ttk.Style()
    # you can use ttk themes here ('clam', 'alt', 'classic', 'default')
    ttk_theme.theme_use('default')
    gui = NNSearch(root)
    gui.mainloop()

if __name__ == '__main__':
    main()
