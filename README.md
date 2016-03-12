**nn-search2** is a [part-of-speech](https://en.wikipedia.org/wiki/Part_of_speech) tagging and text search utility based on [NLTK](www.nltk.org), [TextBlob](textblob.readthedocs.org/en/dev/) and [matplotlib](matplotlib.org).
It uses state-of-the-art pos-tagger based on [Averaged Perceptron](http://www.spacy.io/blog/part-of-speech-POS-tagger-in-python) which provides fast and accurate results.
Above that, one of the main **nn-search2** features is full text part-of-speech search extended with word
ranges such that you can find chains of nouns, verbs, adjectives and fixed expressions.

### What does it do?
Here is the main window with loaded text.
<add image>

Imagine you want to find a sequence of ANY determiner (like "a", "an" or "the") and ANY noun in range of max 2 any other [tokens](https://en.wikipedia.org/wiki/Lexical_analysis#Token).
You do the following.
<add image>

In addition to your search results default text *view 1*, there are 2 alternative text *views*.
View 2, shows the search results per sentence number.
<add image>

View 3, shows explicitly only the numbered results of your search query.
<add image>

Also, **nn-search2** provides some text and search results statistics which you can access via right panel buttons.
<add image>

There is also a separate POS-tagger for batch processing one or more text files.
<add image>

Standalone POS-tagger is also available via console.
<add image>

### How it works?

### How to install?
### Linux


### Windows
Here is a [windows instraller]().



python -m nltk.downloader punkt
python -m nltk.downloader stopwords
python -m nltk.downloader averaged_perceptron_tagger
