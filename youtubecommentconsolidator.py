import pickle 
import pandas as pd

def generate_youtubecomments_df():
    def consolidate_comments(clean_comments):
        processedcomments = []
        for video in clean_comments:
            for comment in video:
                processedcomments.append(comment)
        return processedcomments

    def remove_empty_comments(comments):
        stored = []
        emptycomment = []
        for index,comment in enumerate(comments):
            if comment == "":
                emptycomment.append(index)
                comment = "emptycomment"
            else:
                stored.append(comment)
        print("Empty comments at " , emptycomment)
        return stored

    search_terms = pd.read_pickle("support/_current_/searchTerms.pkl") #get current terms
    clean_comments = pd.read_pickle("support/%s/clean_comments.pkl" % str(search_terms)) # get clean comments
    processedstring = consolidate_comments(clean_comments) #generate list of comment strings from table of comments from clean comments
    processedstring = remove_empty_comments(processedstring)
    clean_comments = pd.DataFrame(processedstring,columns=["comment"])
    clean_comments.to_csv("youtube comments.csv")