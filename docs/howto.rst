Search query
============

How to make a search query?
***************************

Examples::

  DT NN
  DT NN{1} VB
  "the" "Aesir"NNP
  TO "produce" "thunder"NN{1}
  "The"{0} NNP{0} "are" NN{3}

In order to use **nn_search2** you need to know how to write a search query. The syntax is simple, by default **nn_search2** assumes that you are searching for part-of-speech tags (POS-tags).
Make sure you know at least the most basic ones. **nn_search2** uses your query to search only within one sentence. So, ``NNP VB`` will be searched within the limits of a single sentence not a paragraph or a whole text.

If you want to search for occurrences of nouns you enter ``NN``, that's it! Say, you want to find only nouns that appear in a range of 5 words from the beginning of the sentence, you type ``NN{5}``. Range syntax is ``NN{number}`` where ``number`` means the number of words before the current tag. So, you can as well create chain queries like ``NN RB{2} VB{1}``, which basically will attempt to find occurences of a noun, an adverb with 2 words before the adverb and a verb with one word before the verb. Again, the number stands for the number of words before the query tag (``RB``) after the last successful match (``NN``), so if ``NN`` is not matched ``RB`` and ``VB`` will never be matched as well. If you try ``DT NN`` query without any numbers, **nn_search2** will attempt to find the longest match within a sentence, therefore it's a good practice to use word ranges.

That's nice but can I just search for some words? To do this, type a word and surround it with double quotes ``"viking"``. If you want to specify a range ``"viking"{3}``, ``"merry" "viking"{1}``. Pretty simple. You can as well combine POS-tags, words and ranges ``"Valhalla"NNP VBZ{0} DT{0} "place"NN{2}``. If your search query is incorrect and can not be processed **nn_search2** will display a warning message. That's it, now you know the query syntax.
.
