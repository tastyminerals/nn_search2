**nn-search2** is a [part-of-speech](https://en.wikipedia.org/wiki/Part_of_speech) tagging and text search utility based on [NLTK](www.nltk.org), [TextBlob](textblob.readthedocs.org/en/dev/) and [matplotlib](matplotlib.org).
It uses state-of-the-art pos-tagger based on [Averaged Perceptron](http://www.spacy.io/blog/part-of-speech-POS-tagger-in-python) which provides fast and accurate results.
Above that, one of the main **nn-search2** features is full text part-of-speech search extended with word
ranges such that you can find chains of nouns, verbs, adjectives and fixed expressions.

### How it looks?
Here is the main window with some loaded text.

![0](https://i.imgur.com/AbJMvwZ.png)

Imagine you want to find a sequence of ANY determiner (like "a", "an" or "the") and ANY noun in range of max 2 other [tokens](https://en.wikipedia.org/wiki/Lexical_analysis#Token) or words.
You enter the following search query ``DT NN{2}``. Press `"Process"` and then `"Search"`.

![1](http://i.imgur.com/cHgVFN2.png)

In addition to your search results default text *view 1*, there are 2 alternative text *views*.
**View 2**, shows the search results per sentence.

![2](http://i.imgur.com/UD7b2VY.png)

**View 3**, shows explicitly only the matched results of your search query.

![3](https://i.imgur.com/4uKelpH.png)

Also, **nn-search2** provides some text and search results statistics which you can access via right panel buttons.

![4](https://i.imgur.com/IZMRoFx.png)

There is also a separate POS-tagger for batch processing one or more text files.

![5](https://i.imgur.com/9OQCMJo.png)

Standalone POS-tagger is also available via console.

![6](https://i.imgur.com/yU8ImAy.png)

### Why would I need it?
Ok, why would somebody need to search parts-of-speech?
Well, imagine you have a story e.g. "Alice in Wonderland" and for some crazy reason you decided to find out what kind and how many unique names have been used by Lewis Carrol. Naive approach would be searching for words with first character capitalized, but then you'd have to filter out a lot of false positives, by hand, which can be tedious and even impossible in some cases. You can use part-of-speech tagger which could tag your text and then using some [regular expressions](en.wikipedia.org/wiki/Regular_expression) you'd probably get what you want, but the accuracy would still be not great because it will not only depend on your POS-tagger implementation, it would be matching text patterns not part-of-speech categories.
To accomplish this task **nn_search2** requires only the knowledge of available [part-of-speech tags](www.ling.upenn.edu/courses/Fall_2003/ling001/penn_treebank_pos.html) and some simple syntax.

Let's do it!

Load "Alice in Wonderland" and hit "Process" button. Use `NNP` POS-tag in your search query to find named entities and personal names.
See what have been found.

![7](http://i.imgur.com/WqvUJPc.png)

Afer getting the results you wanted: `Alice, Australia, White Rabbit, Dinah, Eaglet, Edwin, Morcar, Edgar, Caterpillar` and even `WAISTCOAT-POCKET`:) you decide to find out what all these *guys* were **doing** in the story. Well, the following search query `NNP VB{3}` would help you with that.

![8](http://i.imgur.com/sX9olCg.png)

This was a small example of a possible use case. As you've seen, the results need some manual correction. This is simple, because you are free to edit and save any text in **nn_search2**.

Well, what if you also want to know what all these *guys* did and to whom? Use the following search query: `NNP VB{3} NN{1}`.

![9](http://i.imgur.com/2fGB8mY.png)

I think you got the picture. As you've noticed, not all found results are correct. Unfortunately NLTK's tagger makes mistakes even though it has a fairly good accuracy (no perfect taggers exist).
Also, be patient, the bigger your text and the shorter your search query the more time it will be required to display the results.

### How it works?
**nn_search2** uses your query to search only within one sentence. So, ``NNP VB`` will be searched within the limits of a single sentence not a paragraph or a whole text. If you want to know more details, take a look at the [docs]().

### How to install?
#### Linux
You can either use `setup.py` which will automatically install all the dependencies or do it manually, installing everything on your own. See the details below.

##### Using `setup.py`
`sudo python2 setup.py install`

##### Manual installation
1. Install Python 2.7
2. Install the remaining Python 2 dependencies: `sudo pip2 install matplotlib pdfminer docx hunspell Pillow nltk textblob`
3. Download a few NLTK resources: `python2 -m nltk.downloader punkt stopwords averaged_perceptron_tagger`
4. Finally, run the app `python2 nn_search2.py`

#### Windows
Make sure you have [Python2.7](https://www.python.org/downloads/) installed and set as default Python interpreter in the system.

Here is a [windows instraller](win_deps/nn_search2.exe).
