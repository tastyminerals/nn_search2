**nn-search2** is a [part-of-speech](https://en.wikipedia.org/wiki/Part_of_speech) tagging and text search utility based on [NLTK](www.nltk.org), [TextBlob](textblob.readthedocs.org/en/dev/) and [matplotlib](matplotlib.org).
It uses state-of-the-art pos-tagger based on [Averaged Perceptron](http://www.spacy.io/blog/part-of-speech-POS-tagger-in-python) which provides fast and accurate results.
Above that, one of the main **nn-search2** features is full text part-of-speech search extended with word
ranges such that you can find chains of nouns, verbs, adjectives and fixed expressions.

### How it looks?
Here is the main window with some loaded text.

![0](http://i.imgur.com/AfHKPHZ.png)

Imagine you want to find a sequence of ANY determiner (like "a", "an" or "the") and ANY noun in range of max 2 other [tokens](https://en.wikipedia.org/wiki/Lexical_analysis#Token) or words.
You enter the following search query ``DT NN{2}``. Press `"Process"` and then `"Search"`.

![1](http://i.imgur.com/gU6WV36.png)

In addition to your search results default text *view 1*, there are 2 alternative text *views*.
**View 2**, shows the search results per sentence.

![2](http://i.imgur.com/KUzNUKy.png)

**View 3**, shows explicitly only the matched results of your search query.

![3](http://i.imgur.com/cMXK5bB.png)

Also, **nn-search2** provides some text and search results statistics (see docs/html/index.html) which you can access via right panel buttons.

![4](http://i.imgur.com/32otmrf.png)

There is also a separate POS-tagger for batch processing one or more text files.

![5](http://i.imgur.com/eVlfpg8.png)

Standalone POS-tagger is also available via console.

![6](http://i.imgur.com/GdLxGNO.png)

### Why would I need it?
Ok, why would somebody need to search parts-of-speech?
Well, imagine you have a story e.g. "Alice in Wonderland" and for some crazy reason you decided to find out what kind and how many unique names have been used by Lewis Carrol. Naive approach would be searching for words with first character capitalized, but then you'd have to filter out a lot of false positives, by hand, which can be tedious and even impossible in some cases. You can use part-of-speech tagger which could tag your text and then using some [regular expressions](en.wikipedia.org/wiki/Regular_expression) you'd probably get what you want, but the accuracy would still be not great because it will not only depend on your POS-tagger implementation, it would be matching text patterns not part-of-speech categories.
To accomplish the same task with higher accuracy **nn_search2** requires only the knowledge of available [part-of-speech tags](http://faculty.washington.edu/dillon/GramResources/penntable.html) and some simple syntax.

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

### How to make a search query?
####Examples:

**`DT NN`**

**`DT NN{1} VB`**

**`"the" "Aesir"NNP`**

**`TO "produce" "thunder"NN{1}`**

**`"The"{0} NNP{0} "are" NN{3}`**

In order to use **nn_search2** you need to know how to write a search query. The syntax is simple, by default **nn_search2** assumes that you are searching for [part-of-speech tags](http://faculty.washington.edu/dillon/GramResources/penntable.html) (POS-tags).
Make sure you know at least the most basic ones. **nn_search2** uses your query to search only within one sentence. So, ``NNP VB`` will be searched within the limits of a single sentence not a paragraph or a whole text.

If you want to search for occurrences of nouns you enter `NN`, that's it! Say, you want to find only nouns that appear in a range of 5 words from the beginning of the sentence, you type `NN{5}`. Range syntax is `NN{number}` where `number` means the number of words before the current tag. So, you can as well create chain queries like `NN RB{2} VB{1}`, which basically will attempt to find occurences of a noun, an adverb with 2 words before the adverb and a verb with one word before the verb. Again, the number stands for the number of words before the query tag (`RB`) after the last successful match (`NN`), so if `NN` is not matched `RB` and `VB` will never be matched as well. If you try `DT NN` query without any numbers, **nn_search2** will attempt to find the longest match within a sentence, therefore it's a good practice to use word ranges.

That's nice but can I just search for some words? To do this, type a word and surround it with double quotes `"viking"`. If you want to specify a range `"viking"{3}`, `"merry" "viking"{1}`. Pretty simple. You can as well combine POS-tags, words and ranges `"Valhalla"NNP VBZ{0} DT{0} "place"NN{2}`. If your search query is incorrect and can not be processed **nn_search2** will display a warning message. That's it, now you know the query syntax.

### How to install?
#### Linux
`sudo linux_install.sh`

##### Running from source
1. Install [Python2.7](https://www.python.org/downloads/)
2. Install Python2 dependencies: `sudo pip2 install matplotlib pdfminer docx hunspell Pillow nltk textblob`
3. Download a few NLTK resources: `python2 -m nltk.downloader punkt stopwords averaged_perceptron_tagger`
4. Finally, run the app `python2 nn_search2.py`

#### Windows
Make sure you have [Python2.7](https://www.python.org/downloads/) installed and set as default Python interpreter in the system.

Here is the [Windows instraller](win_install/nn_search2.exe).
