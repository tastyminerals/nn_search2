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
sudo pip2 install nltk
sudo pip2 install textblob
sudo pip2 install numpy
sudo pip2 install matplotlib
sudo pip2 install Pillow
sudo pip2 install docx
sudo pip2 install pdfminer
sudo pip2 install hunspell
    
python2 -m nltk.downloader punkt stopwords averaged_perceptron_tagger
