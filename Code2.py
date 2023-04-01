import pickle
import pandas as pd
import re
import nltk
nltk.download('stopwords')
nltk.download('wordnet')
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import CountVectorizer

def code2main():
    '''user inputs'''
    stop = ["wa", "doe", "ha", "video", "one",
            "subscribe", "channel", "watch",
            "watching", "thanks", "thank"]      # Add stopwords (lower case)


    '''initialise'''
    all_stopwords = stopwords.words('english')  # set english
    all_stopwords.extend(stop)                  # and extend with 'stop' above

    page_raw_comments = []      # list of raw comments by df page
    page_comments = []          # list of comments by df page
    page_combined = []          # list of corpus by page
    vid_combined = []           # list of corpus by video
    raw_comments = []           # list of raw comments by video
    clean_comments = []         # list of comments by video


    '''load data'''
    search_terms = pd.read_pickle("support/_current_/searchTerms.pkl")
    vid_title = pd.read_pickle("support/%s/vid_title.pkl" % search_terms)
    data = pd.read_pickle("support/%s/combined_data.pkl" % search_terms)    # 'combined_data' => 'data'
    pd.set_option('colwidth', 30)
    df = pd.DataFrame(data, columns=['Title', 'Page', 'Comments'])          # df is for visual only
    print("Search terms:", search_terms)
    print("There are", len(vid_title), "videos analysed")
    print(df)
    # Copy & Paste


    # define functions
    def combine_text(list_of_text):                     # define combine_text to take (list_of_text)
        combined_text = ' '.join(list_of_text)          # do this
        return combined_text                            # and give combined_text back


    def clean_text(text):                               # user defined function for cleaning text
        text = text.lower()                             # all lower case
        text = re.sub(r'\[.*?\]', ' ', text)            # remove text within [ ] (' ' instead of '')
        text = re.sub(r'\<.*?\>', ' ', text)            # remove text within < > (' ' instead of '')
        text = re.sub(r'http\S+', ' ', text)            # remove website ref http
        text = re.sub(r'www\S+', ' ', text)             # remove website ref www

        text = text.replace('€', 'euros')               # replace special character with words
        text = text.replace('£', 'gbp')                 # replace special character with words
        text = text.replace('$', 'dollar')              # replace special character with words
        text = text.replace('%', 'percent')             # replace special character with words
        text = text.replace('\n', ' ')                  # remove \n in text that has it

        text = text.replace('\'', '’')                  # standardise apostrophe
        text = text.replace('&#39;', '’')               # standardise apostrophe

        text = text.replace('’d', ' would')             # remove ’ (for would, should? could? had + PP?)
        text = text.replace('’s', ' is')                # remove ’ (for is, John's + N?)
        text = text.replace('’re', ' are')              # remove ’ (for are)
        text = text.replace('’ll', ' will')             # remove ’ (for will)
        text = text.replace('’ve', ' have')             # remove ’ (for have)
        text = text.replace('’m', ' am')                # remove ’ (for am)
        text = text.replace('can’t', 'can not')         # remove ’ (for can't)
        text = text.replace('won’t', 'will not')        # remove ’ (for won't)
        text = text.replace('n’t', ' not')              # remove ’ (for don't, doesn't)

        text = text.replace('’', ' ')                   # remove apostrophe (in general)
        text = text.replace('&quot;', ' ')              # remove quotation sign (in general)

        text = text.replace('cant', 'can not')          # typo 'can't' (note that cant is a proper word)
        text = text.replace('dont', 'do not')           # typo 'don't'

        text = re.sub(r'[^a-zA-Z0-9]', r' ', text)      # only alphanumeric left
        text = text.replace("   ", ' ')                 # remove triple empty space
        text = text.replace("  ", ' ')                  # remove double empty space
        return text


    '''combine text by video'''
    for i in range(len(data)):                                           # 'i' is a page (a row in df)
        for j in range(len(data[i][2])):                                 # 'j' is a comment on the page
            page_raw_comments.append(data[i][2][j])                      # keep a copy of raw comments
            print(data[i][2][j])

            data[i][2][j] = (clean_text(data[i][2][j]))                  # overwrite with clean_text function
            print(data[i][2][j])

            tokens = nltk.tokenize.TreebankWordTokenizer().tokenize(data[i][2][j])  # each word as a token
            for k in range(len(tokens)):
                tokens[k] = nltk.stem.WordNetLemmatizer().lemmatize(tokens[k])      # stem each token
            data[i][2][j] = " ".join(tokens)                                        # join stemmed tokens back
            print(data[i][2][j])

            page_comments.append(data[i][2][j])                                     # append the cleaned comment
        page_combined.append(combine_text(data[i][2]))                              # combine all comments on page
        print("Page", str(i + 1), "out of", str(len(data)), "done")
        # Copy & Paste

        if i + 1 < len(data):                                            # if not last row of df
            if data[i+1][1] == 1:                                        # if next page is Page 1 of a new video:
                vid_combined.append(combine_text(page_combined))         # combine all comments for a video
                page_combined.clear()
                clean_comments.append(page_comments.copy())              # store clean comments by video
                page_comments.clear()
                raw_comments.append(page_raw_comments.copy())            # store raw comments by video
                page_raw_comments.clear()
        else:                                                            # reached last row of df
            vid_combined.append(combine_text(page_combined))
            clean_comments.append(page_comments.copy())
            raw_comments.append(page_raw_comments.copy())

    data_clean = list(zip(vid_title, vid_combined))
    data_clean = pd.DataFrame(data_clean, columns=['Title', 'Comments'])
    print(data_clean)
    print(len(vid_title), "videos processed")
    print(len(vid_combined), "corpora created")
    # Copy & Paste (optional)


    '''create dtm'''
    cv = CountVectorizer(stop_words=all_stopwords)                       # initialise cv w/o stopwords
    data_cv = cv.fit_transform(data_clean.Comments)                      # apply cv
    dtm = pd.DataFrame(data_cv.toarray(), columns=cv.get_feature_names_out(), index=pd.Series(vid_title))
    print(dtm)


    '''save files'''
    dtm.to_csv("support/%s/dtm.csv" % search_terms)     # save as csv

    dtm.to_pickle("support/%s/dtm.pkl" % search_terms)  # pickle for pd
    data_clean.to_pickle("support/%s/data_clean.pkl" % search_terms)

    pickle.dump(clean_comments, open("support/%s/clean_comments.pkl" % search_terms, "wb"))
    pickle.dump(raw_comments, open("support/%s/raw_comments.pkl" % search_terms, "wb"))
    pickle.dump(all_stopwords, open("support/%s/all_stopwords.pkl" % search_terms, "wb"))
    pickle.dump(stop, open("support/%s/stop_words.pkl" % search_terms, "wb"))
    # Copy & Paste

    # What is the average number of words in a comment?
    # What is the average number of words removed in pre-processing?

