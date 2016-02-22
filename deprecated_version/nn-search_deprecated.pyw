#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
# nn-search 0.3 -- is a little application that can search text using part-of-speech tags.

"""
Created on Sat Oct  5 22:59:41 2013

@author: minerals
"""

import ttk, pickle, sys, os, re
sys.path.append('docx_mod')
import docx_mod.get_docx
import nltk.data
from Tkinter import *
from tkFileDialog import *
from nltk.tokenize import WordPunctTokenizer

def initialize_resources():
    '''This function initializes all the necessary resources and functions used in the app.'''
    global Sent_Tokenizer, Word_PunctTokenizer, Backoff_Tagger, CONTRACTIONS, TAGS, HELP_INFO
    Sent_Tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
    Word_PunctTokenizer = WordPunctTokenizer()
    with open('backoff_tagger', 'r') as pickled_tagger:
        Backoff_Tagger = pickle.load(pickled_tagger)
    with open('contractions', 'r') as contr_file:
        contr_file = contr_file.read()
        CONTRACTIONS = {}
        for line in contr_file.split('\n')[0:-1]:
            key, value = line.split(':')
            CONTRACTIONS[key] = value
    with open('tags', 'r') as tags_file:
        TAGS = tags_file.read()

    nn_main.open_button.state(['!disabled'])
    nn_main.init_frame.destroy()

class nn_search(Frame):
    def __init__(self, master):
        Frame.__init__(self, master)
        self.grid()
        self.interface_filler()
        self.Matched_Tokens = []
        self.All_Matched_Tokens = []

    def more_info(self):
        '''This function shows additional information when <More> button is clicked.'''
        # additional info
        self.button_more.state(['disabled'])
        self.help_window.minsize(600, 232)
        self.help_window.maxsize(783, 729)

        more_info_tags = ['','Less common tags:','PRP','NNP','NNPS','PRP$','JJR','JJS','TO','VBD','VBG','VBN','VBP','VBZ',\
        'RBR','RBS','WP','WP$','WDT','WRB','POS','RP','UH','EX','']
        more_info_desc = ['','Personal pronoun', 'Proper noun, singular','Proper noun, plural','Possessive pronoun','Adjective, comparative',\
        'Adjective, superlative','to','Verb, past tense','Verb, gerund or present participle','Verb, past participle',\
        'Verb, non-rd person singular present','Verb, rd person singular present','Adverb, comparative','Adverb, superlative',\
        'Wh-pronoun','Possessive wh-pronoun','Wh-determiner','Wh-adverb','Possessive ending','Particle',\
        'Interjection','Existential there','']
        rare_info_tags = ['Uncommon or unused tags:','PDT','SYM','LS','FW']
        rare_info_desc = ['','Predeterminer','Symbol','List item marker','Foreign word']

        help_examples = ['DT tree','measures{VB}','measures{NN} CC{1} weights{NN}{1}','Science VBZ magic{5} that works{VB}', 'Elephants do !not fly', 'We !can{2} forsee{5} future{1}']
        examples_desc = ['"DT" is a part-of-speech TAG','"measures" MUST have "VB" TAG (be a verb).','CC must follow "measures", "weights" must follow "CC"','"magic" should follow VBZ in a range of 5 words(inclusive)',\
        '"not" should not be between "do" and "fly"','"can" should not follow "We" in a range of 2 words(inclusive)', '', 'Trying to search "NN" (nouns only) may take tons of time\n with text files bigger than 500kb!\n Try to avoid using single tag queries on big files in general.']

        i = self.N
        for more_tag in more_info_tags:
            ttk.Label(self.left_frame, font='TkDefaultFont 9 bold', text=more_tag).grid(row=i, column=0, sticky='w')
            i += 1
        i = self.N + 1
        for more_desc in more_info_desc:
            ttk.Label(self.left_frame, font='TkDefaultFont 9', text=more_desc).grid(row=i, column = 1, sticky='e')
            i += 1
        i = 0
        for rare_tag in rare_info_tags:
            ttk.Label(self.right_frame, font='TkDefaultFont 9 bold', text=rare_tag).grid(row=i, column = 0, sticky='w')
            i += 1
        i = 0
        for rare_desc in rare_info_desc:
            ttk.Label(self.right_frame, font='TkDefaultFont 9', text=rare_desc).grid(row=i, column = 1, sticky='e')
            i += 1

        ttk.Label(self.right_frame_ex, font = 'TkDefaultFont 9 bold', text='Example queries:').grid(row=0, column=1, sticky='w')
        n = 1
        for example in help_examples:
            ttk.Label(self.right_frame_ex, font = 'TkDefaultFont 9 bold', text=example).grid(row=n, column=1, sticky='w')
            n += 3
        n = 2
        for e_desc in examples_desc:
            ttk.Label(self.right_frame_ex, font = 'TkDefaultFont 9 italic', text=e_desc).grid(row=n, column=1, sticky='w')
            n += 3
        n = 3
        for i in range(5):
            ttk.Label(self.right_frame_ex, font = 'TkDefaultFont 9', text='').grid(row=n, column=1, sticky='w')
            n += 3

    def Help_Window(self):
        '''This function creates a window with information on how to create a search query.'''
        try:
            self.help_window.destroy()
        except:
            pass
        self.N = 0
        self.help_window = Toplevel()
        self.help_window.columnconfigure(0, weight=1)
        self.help_window.rowconfigure(0, weight=1)
        self.help_window.minsize(410, 230)
        self.help_window.title('Search instructions')

        self.button_more_ico = PhotoImage(file=os.path.join('icons', 'more.gif'))
        self.button_more = ttk.Button(self.help_window, text='More', padding=(0,0), compound='left', image=self.button_more_ico, command=self.more_info); self.button_more.grid(row=1, column=0, sticky='w')
        #self.button_close_ico = PhotoImage(file=os.path.join('icons', 'close.gif'))
        self.button_close = ttk.Button(self.help_window, text='OK', padding=(0,0), compound='left', command=self.help_window.destroy); self.button_close.grid(row=1, column=1, sticky='e')
        self.left_frame = ttk.Frame(self.help_window, padding = (5, 0), borderwidth = 3, relief = 'groove'); self.left_frame.grid(row=0, column=0, sticky='e')
        self.right_frame = ttk.Frame(self.help_window, padding = (5, 5), borderwidth = 3, relief = 'groove'); self.right_frame.grid(row=0, column=1, sticky='wn')
        self.right_frame_ex = ttk.Frame(self.help_window, padding = (5, 5), borderwidth = 3, relief = 'groove'); self.right_frame_ex.grid(row=0, column=1, sticky='ws')

        info_tags = ['Common TAGS:', 'DT','CD','NN','NNS','JJ','RB','MD','VB','CC','IN']
        info_desc = ['Determiner', 'Cardinal number', 'Noun, singular or mass', 'Noun, plural', 'Adjective', \
        'Adverb', 'Modal', 'Verb, base form', 'Coordinating conjunction', 'Preposition or subordinating conjunction']

        for tag in info_tags:
            ttk.Label(self.left_frame, font='TkDefaultFont 9 bold', text=tag).grid(row=self.N, column=0, sticky='w')
            self.N += 1
        self.N = 1
        for desc in info_desc:
            ttk.Label(self.left_frame, font='TkDefaultFont 9', text=desc).grid(row=self.N, column = 1, sticky='e')
            self.N += 1

    def About_Window(self):
        '''This function shows "About" window'''
        try:
            self.about_window.destroy()
        except:
            pass
        self.about_window = Toplevel()
        self.about_window.columnconfigure(0, weight=1)
        self.about_window.rowconfigure(0, weight=1)
        self.about_window.minsize(230, 145)
        self.about_window.maxsize(230, 145)
        self.about_window.title('About nn-search')

        self.about_frame = ttk.Frame(self.about_window, height = 150, width = 150, borderwidth=2, relief = 'groove'); self.about_frame.grid()
        ttk.Label(self.about_frame, font='TkDefaultFont 10 bold', text='nn-search v.0.3').grid()
        self.app_icon = PhotoImage(file=os.path.join('icons', 'app_icon.gif'))
        ttk.Label(self.about_frame, image=self.app_icon).grid()
        ttk.Label(self.about_frame, font='TkDefaultFont 10', text='email: tastyminerals@gmail.com').grid()
        ttk.Frame(self.about_frame, height=10).grid()
        ttk.Button(self.about_frame, text='OK', command=self.about_window.destroy).grid(sticky='s')

    def raise_NOQUERY(self):
        '''This function shows a warning message if <search> is pressed and no query provided.'''
        self.frame_noquery = ttk.Frame(self, height=366, width=843, padding = (1, 1), borderwidth = 1, relief = "flat")
        self.frame_noquery.grid(row=0, column=0)
        self.noquery = ttk.Label(self.frame_noquery, font='TkDefaultFont 10', text='Please enter your search query')
        self.noquery.grid()

    def save_RESULTS(self):
        '''This function allows results saving.'''
        fname = asksaveasfilename(filetypes=(("txt file", "*.txt"), ("docx file", "*.docx"), ("Custom file", "*.*")))
        fname = open(fname, 'w')
        full_text = ''

        if self.options[1] == 0:
            for line in self.sents_RESULTS:
                full_text += line + '\n'
        else:
            for l in self.tagged_SENTS:
                for t in l:
                    full_text += re.sub(' ', '_', ' '.join(t)) + ' '
                full_text += '\n'

        fname.write(full_text)
        fname.close()

    def pressedReturn(self, *args):
        '''This function invokes the search process when <Enter> or <Search> button is pressed.'''
        self.QUERY = self.entry.get()
        if not self.QUERY:
            self.raise_NOQUERY()
        else:
            try:
                self.noquery.destroy()
                self.frame_noquery.destroy()
            except:
                pass
            self.query_preprocess(self.QUERY)

    def ctrl_a(self, callback):
        '''Select all text in the text widget.
        <Overwriting tkinter default ctrl+/, (only for text widget)>'''
        self.text.tag_add('sel', '1.0', 'end')
        return 'break'

    def ctrl_z(self, callback):
        '''Undo the last modification in the text widget'''
        self.text.edit_undo()
        return 'break'

    def apply_style_1(self):
    # style for 1 view mode
            self.text.tag_configure('style', background='#C0FA82')

    def apply_style_2(self):
    # style for 2 view mode
            self.text.tag_configure('style', background="#BCFC77", font='TkDefaultFont 11 bold')

    def apply_style_3(self):
    # style for 3 view mode
            self.text.tag_configure('style', font='TkDefaultFont 12 bold')

    def addtags(self):
        '''This function adds tags to the output.'''
        sent_str = ''
        for sent in self.tagged_SENTS[self.i]:
            sent_str += sent[0] + '_' + sent[1] + ' '
        self.i += 1
        return sent_str

    def create_results(self):
        '''This function fills the text widget with results, creates working scrollbar and invokes highlighting functions.'''
        self.text = Text(self.text_frame, height=20, width=93, undo=True, takefocus=0, font = 'TkDefaultFont 11')
        self.text.grid(row=1,column=0)
        self.i = 0 # this var is used in self.addtags function to keep count on self.tagged_SENTS
        if self.getVars()[0] == 0: # view mode: show all text
            for sent in self.sents_RESULTS[:]:
                if self.getVars()[1] == 1: sent = self.addtags()
                self.text.insert('1.0', sent + ' ') # TEXT is inserted into the text widget here
                self.text.grid()
                self.pos_lighter_1() # search for area to highlight and do the highlighting
                self.apply_style_1()
        elif self.getVars()[0] == 1: # view mod: show numbered sentences
            i = len(self.sents_RESULTS) # sentence numbers
            for sent in self.sents_RESULTS[:]:
                if self.getVars()[1] == 1: sent = self.addtags()
                self.text.insert('1.0', str(i) + ': ' + sent + '\n\n')
                i -= 1
                self.text.grid()
                self.pos_lighter_2()
                self.apply_style_2()
        elif self.getVars()[0] == 2: # view mod: show only matched
            i = len(filter(None, self.tokens_RESULTS)) + 1
            start = '1.0'

            for token_pack in self.tokens_RESULTS[:]:
                if token_pack == None: self.tokens_RESULTS.remove(token_pack); continue
                full_token = ''
                for token in token_pack:
                    token_mod = ((token.split()[0] + ' '), (re.sub('\s', '_', ' '.join(token.split()[0:2])) + ' '))
                    full_token += token_mod[self.options[1]]
                i -= 1;
                self.text.insert(start, str(i) + ': ' + full_token+'\n')

                last_pos = self.text.search(full_token, start, stopindex=END)
                full_token_len = len(full_token)
                end_pos = '%s+%dc' % (last_pos, full_token_len)
                self.text.tag_add('style', last_pos, end_pos)
                self.text.grid()
                self.apply_style_3()

        self.scroll = ttk.Scrollbar(self.text_frame, command=self.text.yview)
        self.text.config(yscrollcommand=self.scroll.set)
        self.scroll.grid(row=1,column=1, sticky='ens')
        self.save_button.state(['!disabled'])
        self.text.bind('<Control-a>', self.ctrl_a)
        self.text.bind('<Control-z>', self.ctrl_z)

    def pos_lighter_2(self):
        '''This function detects positions of all items in user query, these positions are then used to highlight matched areas in view mode 2.'''
        start='1.0'
        for token_pack in self.tokens_RESULTS[:]:
            if token_pack == None: self.tokens_RESULTS.remove(token_pack); break
            for token in token_pack:
                token_mod_output1 = (('\y'+token.split()[0]+'\y'), ('\y'+token.split()[0]))
                token_mod_output2 = (('\Y'+token.split()[0]+'\Y'), ('\Y'+token.split()[0]))
                if token.split()[0][0] != '"': # for "<TAG>" functionality
                    token_mod = token_mod_output1[self.options[1]]
                else:
                    token_mod = token_mod_output2[self.options[1]]
                last_pos = self.text.search(token_mod, start, stopindex=END, regexp=True)
                if not last_pos: break
                token_len = len(token.split()[0])
                start = last_pos + '+ 1c'
                end_pos = '%s+%dc' % (last_pos, token_len)
                self.text.tag_add('style', last_pos, end_pos)
            self.tokens_RESULTS.remove(token_pack)


    def pos_lighter_1(self):
        '''This function detects positions of all items in user query, these positions are then used to highlight matched areas in view mode 1.'''
        start='1.0'
        for token_pack in self.tokens_RESULTS[:]: # we are iterating through every token pack
            if token_pack == None: self.tokens_RESULTS.remove(token_pack); break
            first = True
            for token in token_pack:
                token_mod_output1 = (('\y'+token.split()[0]+'\y'), ('\y'+token.split()[0]))
                token_mod_output2 = (('\Y'+token.split()[0]+'\Y'), ('\Y'+token.split()[0]))
                if token.split()[0][0] != '"': # for "<TAG>" functionality
                    token_mod = token_mod_output1[self.options[1]] #used to implement POS-tags for a sentence
                else:
                    token_mod = token_mod_output2[self.options[1]] #used to implement POS-tags for a sentence
                temp_token_pos = self.text.search(token_mod, start, stopindex=END, regexp=True) # we need to know the index of the first token in a token pack for highlighting
                last_token_len = len(token.split()[0])
                end_pos = '%s+%dc' % (temp_token_pos, last_token_len)
                if first:
                    first_token_pos = temp_token_pos
                    start = end_pos + '+ 1c'
                    first = False
            self.text.tag_add('style', first_token_pos, end_pos)
            self.tokens_RESULTS.remove(token_pack)


    def enum_tagged_sent(self, tagged_sent):
        '''USAGE: enum_tagged_sent: tagged_sent
        This function converts tagged sentence tuples into one per word and adds a sequence number for each word.
        The function strips all words from ounctuation marks except '"' assigned for TAGs.
        <I decided to use its output in frankenstein_func to directly match rule_part and each word tuple>'''
        sent_list = []
        punct = '!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~'
        n = 0
        for item in tagged_sent:
            item_mod = item[0].strip(punct) # excluding punctuation from index
            sent_list.append(('{0} {1} {2} '.format(item_mod,item[1],n)))
            n += 1
        return sent_list

    def query_preprocess(self, query):
        '''This function does some necessary modifications to the query.'''
        self.QUERY = []
        for qnode in [i for i in query.strip().split()]:
            self.QUERY += re.sub('}{|}|{', ' ', qnode.strip()).strip().split('  ')

        self.query_test()

    def query_test(self):
        '''This function tags a sentence and sends it together with the search query
        to souls_collector. After that it splits the results into two lists for further processing.
        TYPE: str -> list, list'''
        self.Final_Token_Cache = []
        self.sents_RESULTS = []
        self.tokens_RESULTS = []
        self.tagged_SENTS = []
        RESULTS = []


        for sent in self.TokenizedSents:
            tagged_sent = (Backoff_Tagger.tag(Word_PunctTokenizer.tokenize(sent)))
            results = self.souls_collector(tagged_sent, self.QUERY, sent)
            if results:
                self.tagged_SENTS.append(tagged_sent)
                results.append(None)
                RESULTS.append(results) # appending to final RESULTS list, because 'results' shall be overwritten in next iteration

        if RESULTS:
            for item in RESULTS[0]:
                if isinstance(item, str):
                    self.sents_RESULTS.append(item)

            for item in RESULTS[0]:
                if not isinstance(item, str):
                    self.tokens_RESULTS.append(item)

        #print self.sents_RESULTS, self.tokens_RESULTS
        self.create_results()


    def exception_test(self, sent_list, qnode, qnode_bk, last_match, position):
        '''This function checks for exception in the search query and returns True or False if exception is found.
        TYPE: list, str, str, int, int -> boolean'''
        exception_last_match = int(last_match) + 1
        reg_qnode = re.compile(qnode + '[^\w]')

        for token in sent_list[:]:
            if reg_qnode.search(token):
                if position:

                    qnode_pos_max = int(qnode_bk.split()[-1]) + int(last_match)
                    if int(token.split()[-1]) <= qnode_pos_max:
                        return True, exception_last_match
                    else:
                        return False, last_match
                return True, last_match
            exception_last_match += 1
        return False, exception_last_match


    def souls_collector(self, tagged_sent, query, sent):
        '''This function implements processing of a search query. It analyzes the query and
        attempts to find appropriate matches in the sentence.
        TYPE: list of tuples, list, str -> list of tuples and strings'''

        sent_list = self.enum_tagged_sent(tagged_sent)
        last_match = 0
        position = False
        this_sent = []
        while sent_list:
            temp_token_cache = []
            query_len = len(query)
            for qnode in query: #taking a node 'number NN' from 'NN', 'that 3', 'IN' query
                qnode_bk = qnode
                if len(qnode.split()) > 1:
                    if qnode.split()[-1].isdigit():
                        qnode = qnode.strip(' 0123456789')
                        position = True
                if qnode[0] == '!':
                    qnode = qnode.strip('!')
                    is_exception, last_match = self.exception_test(sent_list, qnode, qnode_bk, last_match, position)
                    position = False
                    if is_exception:
                        query_len += 1
                        continue
                    else:
                        query_len -= 1
                        continue
                for token in sent_list[:]: # taking 'number NN 2' from sent_list
                    if qnode not in TAGS:
                        qnode_mod = qnode.strip('"') # matching "<TAG>" sequences
                        reg_qnode = re.compile('^' + qnode_mod + '[^\w]') # for word query
                    else:
                        reg_qnode = re.compile('\w ' + qnode + ' ') # for TAG query
                    if reg_qnode.search(token):
                        if position:
                            qnode_pos_max = int(qnode_bk.split()[-1]) + int(last_match) # getting the range value from query node
                            if int(token.split()[-1]) <= qnode_pos_max:
                                last_match = token.split()[-1]
                                query_len -= 1
                                temp_token_cache.append(token)
                                position = False
                                sent_list.remove(token)
                                if query_len == 0: # if all tokens matched
                                    self.Final_Token_Cache.append(tuple(temp_token_cache))
                                    this_sent.append(sent)
                                    query_len = len(query)
                                break
                            else:
                                position = False
                                query_len += 1
                                sent_list.remove(token)
                                break
                        else:
                            last_match = token.split()[-1]
                            query_len -= 1
                            temp_token_cache.append(token)
                            sent_list.remove(token)
                            if query_len == 0: # if all tokens matched
                                self.Final_Token_Cache.append(tuple(temp_token_cache))
                                this_sent.append(sent)
                                query_len = len(query)
                            break

                    else:
                        sent_list.remove(token)
                        continue
        if this_sent:
            self.Final_Token_Cache.append(sent)
            return self.Final_Token_Cache

    def load_data(self):
        '''This function loads a file and gets its stats. It supports txt and docx formats.'''
        fname = askopenfilename(filetypes=(("txt file", "*.txt"), ("Microsoft Word 2007/2010 XML file", "*.docx"), ("All files", "*.*")))

        if fname[-2:] == "oc" or fname[-2:] == "cx":
            docx_file = get_docx.opendocx(fname)
            text_list= get_docx.getdocumenttext(docx_file)
            self.TEXT = ''.join(map(str, text_list)) # conversting list to strings
        else:
            with open(fname, 'r') as data_file:
                self.TEXT = data_file.read()

        self.stats1.destroy()
        self.stats2.destroy()

        sents_cnt, word_cnt = self.detect_sentences()
        self.s_button.state(['!disabled'])
        self.stats1 = ttk.Label(self.actions_frame, text='Sentences: ' + str(sents_cnt))
        self.stats2 = ttk.Label(self.actions_frame, text='Words: ' + str(word_cnt))
        self.stats1.grid(row=3, column=1)
        self.stats2.grid(row=4, column=1)


    def fix_sent_border(self, tokenized_sents): #{1: 'apple!Yeah.', 2: 'Come here\nthere is a cup.', 3: 'Of coffeee'}
        '''USAGE: detect_sent_border(sent_dic)
        This function provides additional sentence detection capabilities.'''
        sents_list = Sent_Tokenizer.tokenize(self.TEXT)
        sents_str = ''
        for sent in sents_list:
            r0 = re.compile("\n")
            r1 = re.compile("\.([A-Z])") #WARNING REGEXP is used for sentence detection!!!
            r2 = re.compile("!([A-Z])")

            sent1 = r1.sub(". \\1", sent)
            sent2 = r2.sub("! \\1", sent1)
            sent3 = r0.sub(". ", sent2)

            sents_str += ' ' + sent3
        return sents_str

    def detect_sentences(self):
        '''This function implements basic sentence detection, word tokenization and contraction resolution.
        TYPE: -> int, int'''
        for contraction in CONTRACTIONS:
            contraction_reg = re.compile(contraction)
            self.TEXT = contraction_reg.sub(CONTRACTIONS[contraction], self.TEXT)
        self.TokenizedSents = Sent_Tokenizer.tokenize(self.fix_sent_border(self.TEXT))
        sent_cnt = len(self.TokenizedSents)
        word_cnt = len(Word_PunctTokenizer.tokenize(self.TEXT))
        return sent_cnt, word_cnt

    def getVars(self):
        self.options = self.options_var.get(), self.check_tags.get()
        return self.options #is a tuple (0, 0)

    def interface_filler(self):
        '''This function fills the main interface with buttons and frames.'''
        # main frame
        self.results_frame = ttk.Frame(self, relief = "flat")
        self.results_frame.grid(row=0, column=0)

        #actions frame
        self.actions_frame = ttk.Frame(self, padding = (1, 1), height=230, width=10, borderwidth = 2, relief = "flat")
        self.actions_frame.grid(row=0, column=2)

        # search entry frame
        self.entry_frame = ttk.Frame(self.results_frame, padding = (1, 1), borderwidth = 1, relief = "flat")
        self.entry_frame.grid(row=0, column=0)

        # spacer on the right of the search entry
        self.entry_frame_right_spacer = ttk.Frame(self.entry_frame, height=20, width=100, relief = "flat")
        self.entry_frame_right_spacer.grid(row=0, column=3)

        # actions frame spacer, below the buttons
        self.actions_frame_spacer = ttk.Frame(self.actions_frame, height=SIZE[os.name]['A_HEIGHT'], width=55, relief = "flat")
        self.actions_frame_spacer.grid(row=2, column=1)

        # little space between entry and search button
        self.entry_frame_right_innerspacer = ttk.Frame(self.entry_frame_right_spacer, width=16, relief = "flat")
        self.entry_frame_right_innerspacer.grid(row=0, column=0)

        # little space between info button and entry widget
        self.entry_left_space = ttk.Frame(self.entry_frame, width=12, relief = "flat")
        self.entry_left_space.grid(row=0, column=1)

        # text frame
        self.text_frame = ttk.Frame(self.results_frame, height=SIZE[os.name]['T_HEIGHT'], width=SIZE[os.name]['T_WIDTH'], padding = (1, 1), borderwidth = 1, relief = "groove")
        self.text_frame.grid(row=1, column=0)

        # space between text frame and actions panel
        self.text_frame_rightspacer = ttk.Frame(self, width=SIZE[os.name]['B_FRAME'], relief = "flat")
        self.text_frame_rightspacer.grid(row=0, column=1)

        # entry widget
        self.entry = ttk.Entry(self.entry_frame, font='TkDefaultFont 11', width = SIZE[os.name]['E_WIDTH'])
        self.entry.grid(row=0, column=2)
        self.entry.bind('<Return>', self.pressedReturn, '+')
        self.entry.focus() # <Return> works only when entry is focused

        # load file button
        self.open_button_image = PhotoImage(file=os.path.join('icons', 'open.gif'))
        self.open_button = ttk.Button(self.actions_frame, text='Load file', padding = (1, 1), image=self.open_button_image, compound='left', command=self.load_data)
        self.open_button.state(['disabled'])
        self.open_button.grid(row=0, column=1)

        # save results button
        self.save_button_image = PhotoImage(file=os.path.join('icons', 'save.gif'))
        self.save_button = ttk.Button(self.actions_frame, text='Save', padding = (1, 1), image=self.save_button_image, compound='left', command=self.save_RESULTS)
        self.save_button.state(['disabled'])
        self.save_button.grid(row=1, column=1)

        # search button
        self.s_button_image = PhotoImage(file=os.path.join('icons', 'find.gif'))
        self.s_button = ttk.Button(self.entry_frame_right_spacer, text='Search!', padding=(1,1), image=self.s_button_image, compound='left', command=self.pressedReturn)
        self.s_button.state(['disabled'])
        self.s_button.grid(row=4, column=1)

        # info frame and button
        self.info_frame = ttk.Frame(self.entry_frame, width = 30, padding = (3,0), relief = "flat")
        self.info_frame.grid(row=0, column=1)

        self.info_button_image = PhotoImage(file=os.path.join('icons', 'book.gif'))
        self.info_button = ttk.Button(self.info_frame, image=self.info_button_image, command=self.Help_Window)
        self.info_button.grid()

        # about frame and button
        self.info_frame2 = ttk.Frame(self.entry_frame, relief = "flat")
        self.info_frame2.grid(row=0, column=0, sticky = 'w')

        self.about_button_image = PhotoImage(file=os.path.join('icons', 'info.gif'))
        self.about_button = ttk.Button(self.info_frame2, image=self.about_button_image, command=self.About_Window)
        self.about_button.grid()

        # search options
        self.radio_frame = ttk.Frame(self.actions_frame, padding = (5, 5), borderwidth=2, relief = "groove")
        self.radio_frame.grid(row=2, column=1)

        self.radio_label = ttk.Label(self.radio_frame, font='TkDefaultFont 9', text='View mode')
        self.radio_label.grid(row=0)

        self.options_var = IntVar()
        self.option_original_ico = PhotoImage(file=os.path.join('icons', 'original.gif'))
        self.option_original = ttk.Radiobutton(self.radio_frame, image=self.option_original_ico, variable=self.options_var, value=0)

        self.option_one_ico = PhotoImage(file=os.path.join('icons', 'one.gif'))
        self.option_one = ttk.Radiobutton(self.radio_frame, image=self.option_one_ico, variable=self.options_var, value=1)

        self.option_matched_ico = PhotoImage(file=os.path.join('icons', 'matched.gif'))
        self.option_matched = ttk.Radiobutton(self.radio_frame, image=self.option_matched_ico, variable=self.options_var, value=2)

        self.option_original.grid(row=1)
        self.option_one.grid(row=2)
        self.option_matched.grid(row=3)

        # TAGS check button
        self.check_tags = IntVar()
        self.check = ttk.Checkbutton(self.radio_frame, text='POS-tags', padding=(0,5), onvalue=1, offvalue = 0, variable=self.check_tags)
        self.check.grid(row=4)

        # frame to initialize resources
        self.init_frame = ttk.Frame(self.results_frame)
        self.init_frame.grid(row=1, column=0)

        # initalize resources message
        self.init_message = ttk.Label(self.init_frame, font='TkDefaultFont 10', text='Wait a moment please...')
        self.init_message.grid()

        # filling space with empty labels for better positioning
        self.stats1 = ttk.Label(self.actions_frame)
        self.stats2 = ttk.Label(self.actions_frame)
        self.stats1.grid(row=3, column=1)
        self.stats2.grid(row=4, column=1)

# init gui
global SIZE
SIZE = {'posix':{'WIDTH':1150, 'HEIGHT':410, 'A_HEIGHT':312, 'T_HEIGHT':370, 'T_WIDTH':862, 'B_FRAME':10, 'E_WIDTH':75}, \
'nt':{'WIDTH':890, 'HEIGHT':390, 'A_HEIGHT':287, 'T_HEIGHT':348, 'T_WIDTH':770, 'B_FRAME':3, 'E_WIDTH':74}} #UI dimentions for win and linux

root = Tk()
root.title('nn-search 0.3')
root.minsize(SIZE[os.name]['WIDTH'],SIZE[os.name]['HEIGHT'])
root.maxsize(SIZE[os.name]['WIDTH'],SIZE[os.name]['HEIGHT'])
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)
root.update()

nn_main = nn_search(root)
#root.bind('<Return>', nn_main.pressReturn)
nn_main.after(300, initialize_resources)
nn_main.mainloop()
