#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
import threading as thr
import ttk
import Tkinter as tk
import Queue

import loop_file


class MyApp(ttk.Frame):
    def __init__(self, master):
        ttk.Frame.__init__(self, master)
        self.grid()
        self.model_queue = Queue.PriorityQueue()
        self.butt = ttk.Button(self, text='Click me!', command=self.proc)
        self.butt.grid()

    def finish_loop_window(self):
        # remove "Wait" message
        self.waitFr.destroy()
        # create Frames for Toplevel window
        graphFr = ttk.Frame(self.loop_win, borderwidth=2, relief='groove')
        graphFr.grid(row=0, column=0, sticky='nsew')

        # update to get the new dimensions
        self.update()
        self.loop_win.geometry("")
        ttk.Label(self.loop_win, text=self.fib_result).grid()

    def check_looping_thread_save_results(self):
        """
        Check every 10ms if model thread is alive.
        Destroy progress bar when model thread finishes.
        Unlock UI widgets.
        """
        if self.loop_thread.is_alive():
            self.after(10, self.check_looping_thread_save_results)
        else:
            self.loop_thread.join()
            # get the results of model processing
            self.fib_result = self.model_queue.get()
            self.finish_loop_window()

    def centrify_widget(self, widget):
        widget.update_idletasks()
        width = widget.winfo_screenwidth()
        height = widget.winfo_screenheight()
        xy = tuple(int(c) for c in widget.geometry().split('+')[0].split('x'))
        xpos = width/2 - xy[0]/2
        ypos = height/2 - xy[1]/2
        widget.geometry("%dx%d+%d+%d" % (xy + (xpos, ypos)))

    def proc(self):
        self.model_queue = Queue.PriorityQueue()
        self.loop_thread = thr.Thread(target=loop_file.do_looping,
                                        args=(self.model_queue, ))
        self.loop_thread.start()
        self.after(10, self.check_looping_thread_save_results)

        self.loop_win = tk.Toplevel()
        self.loop_win.title('Toplevel')
        self.waitFr = ttk.Frame(self.loop_win, borderwidth=2, relief='groove')
        self.waitFr.grid(sticky='nsew')
        ttk.Label(self.waitFr, text='Wait...\nCreating plots...').grid()
        self.centrify_widget(self.loop_win)


root = tk.Tk()
root.title('Test')
root.update()
gui = MyApp(root)
gui.mainloop()
