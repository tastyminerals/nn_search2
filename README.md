*nn-search* is a simple search tool, yet there are couple of things you need to know before making a query. 

One of the main features is POS-tag usage. *nn-search* implements a list of Penn Treebank part-of-speech tags. So if you want to find all nouns in the text you can simply enter "NN" or "JJ" if you need adjectives.
Let's take a closer look at the search algorithm: "One red sails ship appeared on the blue horizon." 
Simply searching for "red horizon" shall return you this sentence because *nn-search* assumes you're searching for a sequence of words of any length within the boundaries of one sentence. If you need to find "blue horizon" explicitly you must specify the range "blue horizon{1}".
"red NN" in turn shall match "red ship" not "red horizon" because only the first "NN" occurrence will be matched. By default *the first longest possible match* is searched. If there will be more than one possible sequence of "red NN" in the text all of them shall be matched.
Now take a look at *one very important thing*. If you search for "JJ horizon", which means search for an adjective and "horizon" somewhere in the sentence, what will be matched? First longest possible match is "red horizon", but how do we match "blue horizon" instead ? You may think that "JJ horizon{1}" is what we need, but it's not. 
The answer is you can't use the word "horizon" at all. Such logic, while limiting our searching potential, helps us to save a lot of processing time. To match "blue horizon" sequence you must use "JJ NN{1}" query.

== Making a search query ==

Here is a quick explanation of everything you need to know about matching sentences with nn-search.
  One red sails ship appeared on the blue horizon.

 * red horizon -- simple search query that matches the first longest possible sequence within a sentence.

 * blue horizon{1} -- shall match only the word "blue" *followed* by "horizon". 

 * red horizon{7} -- the number in curly brackets specifies the range, so the number of words allowed between "red" and "horizon" is 6 because the 7th is "horizon" itself. This query is the same as typing "red horizon".

 * JJ NN -- the query shall match any occurrence of an adjective and a noun. For our test sentence it shall match "red sails ship" and "blue horizon".

 * JJ NN{1} -- this query shall match ONLY "blue horizon", because it states that a noun should follow an adjective.

 * JJ NN{2} -- this query shall match "red sails ship" AND "blue horizon".

 * CD sails{NNS}{2} -- this query shall match "One red sails".

 * One !red ship -- this query shall not match the test sentence, it matches any occurrence of "One" and "ship" ONLY if there is no "red" between them.

 * NN !IN{1} horizon -- this query shall match the "ship appeared on the blue horizon" sequence, because "IN" is not expected only right after "NN". 

 * red{JJ}{2} sails{NNS}{1} ship{NN}{1} on{IN} the{DT}{1} !green horizon{NN}{2} -- this query shall match "red sails ship appeared on the blue horizon" sequence. 

 Science "NN" is "VBZ" magic "NN" "that" works.

 * "VBZ" magic "that" -- Use double quotes to match POS-tags if they appear in text. You can't use punctuation in your query except " to match double quoted strings in text.

If you still did not grasp the idea, go run the application and try your own queries on some test files.

== Interface ==
The interface is pretty self-explanatory. There are three types of view modes: range highlighting, items highlighting and "matched items only.
There are load and save buttons. The result can be saved only in txt format with each matched sentence separated by a new line. But you can save the results by directly copy pasting them from the application as well. The input file format can be plain text (txt) or Microsoft Office Word 2007/2010 (docx).