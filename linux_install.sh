#!/bin/bash
NN_DIR=$HOME/.nn_search2
NN_SLINK=/usr/local/bin/nn_search2

#copy files
if [ -d "$NN_DIR" ]; then
    rm -r $NN_DIR
fi
mkdir $HOME/.nn_search2
cp -r nn_search2 $HOME/.nn_search2

# create a symlink
if [ -L "$NN_SLINK" ]; then
    sudo rm /usr/local/bin/nn_search2
fi
sudo ln -s $HOME/.nn_search2/nn_search2/nn_search2.py /usr/local/bin/nn_search2

# install python2 dependencies
sudo pip install nltk
sudo pip install textblob
sudo pip install numpy
sudo pip install matplotlib
sudo pip install Pillow
sudo pip install docx
sudo pip install pdfminer
sudo pip install hunspell
    
python -m nltk.downloader punkt stopwords averaged_perceptron_tagger
