import requests
from bs4 import BeautifulSoup
import pandas as pd
from googleapiclient.discovery import build
import pickle
import os
from google_key import key    
import pickle
import pandas as pd
import re
import nltk
nltk.download('stopwords')
nltk.download('wordnet')
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import CountVectorizer
import pandas as pd
from nltk.corpus import stopwords
from wordcloud import WordCloud, STOPWORDS
from collections import Counter
from nltk.util import everygrams
import math
import pickle
import matplotlib.pyplot as plt
from matplotlib import style
style.use("ggplot")
import pandas as pd
from textblob import TextBlob
from nltk.corpus import stopwords
import math
import statistics
import pickle
import matplotlib.pyplot as plt
from Code1 import code1main
from Code2 import code2main
from Code3 import code3main

#run dependencies once only 
# code1main(search_terms="Applewatch" , max_results=20) #Get comments using API
# code2main()   #Clean Comments 
# code3main() #Analytics Wordcloud and Number of Comments
search_terms = pd.read_pickle("support/_current_/searchTerms.pkl")
clean_comments = pd.read_pickle("support/%s/clean_comments.pkl" % str(search_terms))

def code5main(clean_comments):
    search_terms = pd.read_pickle("support/_current_/searchTerms.pkl")
    vid_title = pd.read_pickle("support/%s/vid_title.pkl" % search_terms)
    vid_page = pd.read_pickle("support/%s/vid_page.pkl" % search_terms)
    raw_comments = pd.read_pickle("support/%s/combined_data.pkl" % str(search_terms))
    top_words = pd.read_pickle("support/%s/top_words.pkl" % str(search_terms))
    top_words = pd.DataFrame(top_words)
    topwordslist = []
    size = top_words.shape
    for x in range(size[0]): #extract all top words
        for y in range(size[1]):
            topwordslist.append(top_words[y][x])
            
    componentlist  =pd.read_excel("Components.xlsx",dtype=str) #Get component list
    print(componentlist)
    commonwords = []
    topwordscleaned = []
    for items in topwordslist:
        topwordscleaned.append(items[0])
    print(topwordscleaned)
    for items in componentlist["Components"]: #find same words
        print(f"Checked : {items}")
        if items.lower() in topwordscleaned:
            commonwords.append(items.lower())
    print(commonwords)
    print("There is {} comments in total".format(len(raw_comments)))
    print("There is {} number of components in the top words".format(len(commonwords)))
    print("The words are {}".format(commonwords))
    
    def sentiment(text):                            # Lexicon-based vs Supervised Learning
            pol = TextBlob(text).sentiment.polarity
            return pol
    
        
        
    sentimentcombine = ""
    wordsentimentlist = [ [0,0] for x in commonwords] #(total sentiment score, number of comments) for each comment
    for video in clean_comments: #for all videos
        for comment in video: #for each comment
            combinesentiment = 0  #combine sentiment value for a comment    
            checkthis = False
            for x in commonwords:
                if x in comment:
                    checkthis = True
            if checkthis:
                for words in comment:
                    combinesentiment=sentiment(comment)
            
            for index,x in enumerate(commonwords):
                if x in comment:
                    wordsentimentlist[index][0] += combinesentiment
                    wordsentimentlist[index][1] += 1
                else:
                    pass
    def processtupleinlist(listoftuples,commonwords):
        locallist = []
        for index,x in enumerate(listoftuples):
            if x[1] != 0:
                locallist.append((commonwords[index],x[0]/x[1]))
        return locallist #returns a new list of processed

    wordsentimentlist = processtupleinlist(wordsentimentlist,commonwords)

    print("The sentiment for each word is {}".format(wordsentimentlist))
    return wordsentimentlist
code5main()
