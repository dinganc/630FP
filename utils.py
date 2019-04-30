import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import re
from nltk.tokenize import wordpunct_tokenize
from nltk.corpus import stopwords
from nltk.tokenize import MWETokenizer
import gensim.downloader as api
import sqlite3
import numpy as np
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences


import datetime
def clean_text(text):
    text=re.sub(r'[^a-zA-Z ]+', '', text.lower().replace('\n'," "))
    return text

def remove_stopwords(text_list):
    sw=set(stopwords.words('english'))
    text_list=[i for i in text_list if i not in sw]
    return text_list

def tokenize_word(text):
    text= wordpunct_tokenize(text)
    text=remove_stopwords(text)
    return text

def tokenize_phrase(text):
    text= wordpunct_tokenize(text)
    text=remove_stopwords(text)
    return text

def doc2vec(text_list):
    pass

def w2v_average_wiki(text_list,wlname='glove-wiki-gigaword-200'):
    info = api.info()  # show info about available models/datasets
    model = api.load(wlname)
    rtr=[]
    for each_text in text_list:
        each_text = filter(lambda x: x in model.vocab, each_text)
        sub=[]
        for each_token in each_text:
            sub.append(model[each_token])
        sub=np.array(sub)
        rtr.append(np.average(sub, axis=0))
    return rtr

def get_embedding_dict(text_list,wlname='glove-wiki-gigaword-200'):
    info = api.info()  # show info about available models/datasets
    model = api.load(wlname)
    embeddings_index = {}
    new_text_list=[]
    for each_text in text_list:
        new_text=[]
        each_text = filter(lambda x: x in model.vocab, each_text)
        for each_token in each_text:
            embeddings_index[each_token]=model.wv[each_token]
            new_text.append(each_token)
        new_text_list.append(new_text)
    return embeddings_index,new_text_list

def update_nltk_sentiment():
    print('updating nltk sentiment')
    sid = SentimentIntensityAnalyzer()
    conn=sqlite3.connect('SONGS.db')
    cur=conn.cursor()
    for i in cur.execute("select PK,Lyrics from song where pos is null").fetchall():
        try:
            pk,text=i
            scores = sid.polarity_scores(text)
            cur.execute("UPDATE SONG SET pos=?,neg=?,neu=?,comp=? WHERE PK =?",(scores['pos'],scores['neg'],scores['neu'],scores['compound'],pk))
            conn.commit()
        except:
            pass

if 1>2:
    conn=sqlite3.connect('songs.db')
    cur=conn.cursor()
    example_text=cur.execute("select Lyrics from song where Lyrics is not null").fetchall()
    labels=[i[0] for i in cur.execute("select Economic from song where Lyrics is not null").fetchall()]
    songs=[]
    for i in example_text:
        songs.append(tokenize_word(clean_text(i[0])))
    songs=get_embedding_dict(songs)
