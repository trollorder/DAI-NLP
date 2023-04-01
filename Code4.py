import pandas as pd
from textblob import TextBlob
from nltk.corpus import stopwords
import math
import statistics
import pickle
import matplotlib.pyplot as plt
from matplotlib import style
style.use("ggplot")

def code4main():
    '''user inputs'''
    deci = 2            # decimal places


    '''load data'''
    # from Code 1.py
    search_terms = pd.read_pickle("support/_current_/searchTerms.pkl")
    vid_title = pd.read_pickle("support/%s/vid_title.pkl" % search_terms)
    vid_page = pd.read_pickle("support/%s/vid_page.pkl" % search_terms)

    # from Code 2.py
    
    stop = pd.read_pickle("support/%s/stop_words.pkl" % search_terms)

    # from Code 3.py
    top_words = pd.read_pickle("support/%s/top_words.pkl" % search_terms)


    '''initialise'''
    vid_list = list(zip(vid_title, vid_page))
    vid_list = pd.DataFrame(vid_list)
    all_stopwords = stopwords.words('english')
    all_stopwords.extend(stop)

    print("Search terms:", search_terms)
    print(vid_list)
    # Copy & Paste


    # define functions
    def sentiment(text):                            # Lexicon-based vs Supervised Learning
        pol = TextBlob(text).sentiment.polarity
        return pol


    '''Sentiment Analysis'''
    text_pol = []       # to store polarity scores for a comment
    x_index = []        # to store x data point for a comment
    top_plot = []       # to store [x, y] coordinates for a top word
    vid_plot = []       # to store [x, y] coordinates of top words by video
    newclean = []

    #get all comments from top 20 videos list
    for i in range(len(clean_comments)):
        for j in range(len(clean_comments[i])):
            newclean.append(clean_comments[i][j])
    commentscleandf=pd.DataFrame(newclean)

    temp = []
    scorelist = [] #store local value of sentiment


    for i in range(len(top_words)):                         # for each video
        for j in range(len(top_words[i])):                  # for each top word in video
            locallst = []
            for k in range(len(clean_comments[i])):         # for each comment in video
                
                find_this = top_words[i][j][0]              # use 'find_this' on 'check_this' comment
                check_this = " ".join(word for word in clean_comments[i][k].split() if word not in all_stopwords)
                if len(top_words[i][j][0].split()) != 1:                # if top word is a phrase
                    find_this = top_words[i][j][0].replace(" ", "_")    # make it a word (chunk)
                    check_this = check_this.replace(top_words[i][j][0], find_this)
                    print(find_this)
                    print(check_this)
                    # Copy & Paste (optional for situated find_this, check_this)
                
                for word in check_this.split():
                    
                    if find_this == word:  # if find_this found in comment
                        sentimentlocal = sentiment(check_this)
                        text_pol.append(sentimentlocal)  # get sentiment of the comment (y)
                        locallst.append(sentimentlocal)
                        x_index.append(len(text_pol))           # get an index count for above (x)
                        break
                
            locallstmean = sum(locallst)/max(len(locallst),1)
            scorelist.append(locallstmean)
            top_plot.append([x_index.copy(), text_pol.copy()]) # x and y data to plot, for 1 video
            text_pol.clear()
            x_index.clear()
        vid_plot.append(top_plot.copy())                        # x and y data to plot, by video
        top_plot.clear()


    #Sentiment Analysis plot
    for i in range(len(vid_plot)):                              # create subplots for each video i
        for j in range(len(vid_plot[i])):                       # create based on each top word j
            r = math.floor(math.sqrt(int(len(vid_plot[i]))))
            c = math.ceil(int(len(vid_plot[i])) / r)
            plt.subplot(r, c, j + 1, facecolor='skyblue')
            plt.subplots_adjust(wspace=0.5, hspace=1.2)
            plt.scatter(vid_plot[i][j][0], vid_plot[i][j][1], label='skitscat', color='k', s=5, marker="o")
            plt.axhline(0, color='k', linestyle='--', linewidth=1)      # marking a reference line y = 0
            plt.title(top_words[i][j][0], fontsize=10)
            plt.xlim(xmin=0, xmax=len(vid_plot[i][j][0]) + 0.5)         # set x limits
            plt.xticks([1, len(vid_plot[i][j][0])])                     # set x ticks
            plt.ylim(ymin=-1, ymax=1)                                   # set y limits
            plt.yticks([-1, 0.0, 1])                                    # set y ticks
        plt.suptitle('Sentiment analysis (Pol), Video %s' % str(i + 1))
        plt.savefig("support/{}/{}.png".format(search_terms, "video_" + str(i + 1))) #saves the data
        if i == 0:          # plot Video 1, instead of all videos
            plt.show()
        plt.close()         # close for next video, instead of overwriting
    # Copy & Paste


    '''Summary'''
    print("\n---Summary---")
    print(len(vid_plot), "videos analysed.")
    print("Video 1 has", len(vid_plot[0]), "top words.")
    try:
        print("The first top word in Video 1 is <", top_words[0][0][0], "> which appeared", top_words[0][0][1],
            "times in", len(vid_plot[0][0][0]), "comments.")
    except:
        print("Video 1 doesnt have topwords")
    # Copy & Paste (optional)


    print("Creating result summary as csv...")
    res_vid_num = []    # Video ID
    res_vid_titl = []   # video title
    res_vid_page = []   # video page link
    res_vid_comm = []   # number of comments for the video
    res_top_word = []   # the top word for the video
    res_top_freq = []   # number of times the top word was mentioned
    res_top_comm = []   # number of comments with the top word
    res_sen_mean = []   # mean sentiment score for the top word
    res_sen_stdv = []   # standard deviation for the mean score


    for i in range(len(vid_plot)):                              # for each video i
        for j in range(len(vid_plot[i])):                       # based on each top word j
            res_vid_num.append("Video" + str(i + 1))
            res_vid_titl.append(vid_title[i])
            res_vid_page.append(vid_page[i])
            res_vid_comm.append(len(clean_comments[i]))
            res_top_word.append(top_words[i][j][0])
            res_top_freq.append(top_words[i][j][1])
            res_top_comm.append(len(vid_plot[i][j][0]))
            try:
                res_sen_mean.append(round(statistics.mean(vid_plot[i][j][1]), deci))
                res_sen_stdv.append(round(statistics.stdev(vid_plot[i][j][1]), deci))
            except:
                if len(vid_plot[i][j][1]) == 1:     # no stdev for 1 entry
                    res_sen_stdv.append("NA")
                else:                               # no mean and stdev for no entry
                    res_sen_mean.append("NA")
                    res_sen_stdv.append("NA")

    results = list(zip(res_vid_num, res_vid_titl, res_vid_page, res_vid_comm,
                    res_top_word, res_top_freq, res_top_comm,
                    res_sen_mean, res_sen_stdv))

    results = pd.DataFrame(results, columns=["Video ID", "Title", "Link", "No. of comments",
                                            "Top word", "Top Freq", "Top comments",
                                            "TextBlob (mean)", "TextBlob (stdev)"])
    print(results)
    columnmean = results.loc[:,"TextBlob (mean)"]
    annotateframe = pd.concat( [commentscleandf,pd.DataFrame(scorelist)],axis= 1)
    # annotateframe.to_csv("check.csv")
    results.to_csv("support/%s/results.csv" % search_terms)
    pickle.dump(results, open("support/%s/results.pkl" % search_terms, "wb"))
    # Copy & Paste

    # How might Code 1 to 4 be modified to analyse data from other social media?
    # How sensitive are the results with respect to the SA model used?
    # What is the Precision, Recall, F1 score?

    newdata = pd.read_csv("check.csv")
    newdata=newdata[:51] #get first 50 annotated comments
    # comcount = newdata["final cleaned"].value_counts(ascending=True)
    # humancount = newdata["Human Annotation"].value_counts(ascending=True)
    from sklearn.metrics import confusion_matrix
    y_actu = newdata["Human Annotation"]
    y_pred = newdata["final cleaned"]
    cm = confusion_matrix(y_actu, y_pred)



    def getmetrices(cm):
        truepositive,falsepositive,truenegative,falsenegative = cm[2][2],cm[0][2],cm[0][0],cm[2][0]
        precision = truepositive/(truepositive+falsepositive)
        recall=truepositive/(truepositive+falsenegative)
        f1score = 2*(precision*recall)/(precision+recall)
        return precision,recall,f1score
    print(newdata[["Comment","final cleaned","Human Annotation"]].loc[:5])
    print(cm)
    print(getmetrices(cm))