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

def code3main():
    '''user inputs'''
    e_grams_max = 5         # Maximum length of every-grams (i.e. 1 = single word)
    e_grams_cut = 30        # Number of top words/every-grams to be analysed (for a video)


    '''load data'''
    # from Code 1.py
    search_terms = pd.read_pickle("support/_current_/searchTerms.pkl")
    vid_title = pd.read_pickle("support/%s/vid_title.pkl" % search_terms)
    vid_page = pd.read_pickle("support/%s/vid_page.pkl" % search_terms)

    # from Code 2.py
    data_clean = pd.read_pickle("support/%s/data_clean.pkl" % search_terms)
    stop = pd.read_pickle("support/%s/stop_words.pkl" % search_terms)


    '''initialise'''
    all_stopwords = stopwords.words('english')
    all_stopwords.extend(stop)
    STOPWORDS.update(all_stopwords)

    data_clean = list(data_clean.Comments)  # make 'Comments' column of data_clean a list
    vid_list = list(zip(vid_title, vid_page))
    vid_list = pd.DataFrame(vid_list)

    print("Search terms:", search_terms)
    print(vid_list)
    # Copy & Paste


    '''Exploratory Data Analysis'''
    '''EDA - metadata'''
    print("Summary of data...")
    vid_index = []      # list of video index (from 1 to last video)
    vid_words = []      # list of number of words in each video

    for i in range(len(data_clean)):
        vid_index.append("Video_" + str(i+1))
        vid_words.append(len(data_clean[i].split()))

    data_words = pd.DataFrame(list(zip(vid_index, vid_words)), columns=['Video Index', 'Total Words'])
    print(data_words)

    print("Plotting graph...")
    fig = plt.figure(figsize=(8, 6))
    plt.bar(vid_index, vid_words, color='r')
    plt.title('Words analysed per video')
    plt.ylabel('Number of words')
    plt.xlabel('Video Index')
    plt.xticks(rotation=70, fontsize=8)
    plt.savefig("support/%s/data_words.png" % search_terms)
    plt.show()
    # Copy & Paste


    '''EDA - WordCloud'''
    print("Creating WordClouds...")
    wc = WordCloud(stopwords=STOPWORDS, background_color="white", colormap="Dark2", collocations=False,
                max_font_size=150, include_numbers=True, random_state=42)  # add "max_words=10" to limit number of words
    fig2 = plt.figure(figsize=(8, 5))

    for i in range(len(data_clean)):
        if len(data_clean[i]) != 0:     # WordCloud needs at least one word
            wc.generate(data_clean[i])  # a WordCloud for each video
        else:
            wc.generate("empty")

        r = math.floor(math.sqrt(len(data_clean)))
        c = math.ceil(len(data_clean)/r)
        plt.subplot(r, c, i + 1)        # plt.subplot(rows, cols, index), remove to plot individual video

        plt.imshow(wc, interpolation="bilinear")
        plt.axis("off")
        plt.title(vid_index[i], fontsize=10)
    plt.savefig("support/%s/WordCloud.png" % search_terms)
    plt.show()
    # Copy & Paste


    '''EDA - top word'''
    print("Finding top words...")
    top_words = []      # list of top words by video
    top = []            # list of top words in each video

    for i in range(len(data_clean)):
        data_clean[i] = " ".join(word for word in data_clean[i].split() if word not in all_stopwords)
        e_grams_counts = Counter(everygrams(data_clean[i].split(), max_len=e_grams_max))
        e_grams_most = e_grams_counts.most_common(e_grams_cut)
        print("Video ", str(i+1))
        print(e_grams_most)
        # Copy & Paste

        for j in range(len(e_grams_most)):
            top.append([" ".join(e_grams_most[j][0]), e_grams_most[j][1]])
        top_words.append(top.copy())
        top.clear()

    pickle.dump(top_words, open("support/%s/top_words.pkl" % search_terms, "wb"))
    print(top_words)
    # Copy & Paste

    # How might we introduce a minimum threshold frequency for top words?
    # How might we examine linked words (i.e. words frequently mentioned with top words)?
