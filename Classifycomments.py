from transformers import pipeline
import pandas as pd


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
            
def labelcomments(processedstring,labels):
    classifier = pipeline("zero-shot-classification")
    predicted_labels = classifier(processedstring,labels)
    for eachresult in predicted_labels :  #Extract the highest probability label and insert into results
        eachresult["classified"] = eachresult["labels"][eachresult["scores"].index(max(eachresult["scores"]))]
    return predicted_labels

def store_as_csv(results,csvname):
    filesavedname = csvname #set saved name
    table =[]   #temp table to store 
    tablename = []
    for columns in results[0]: #get number of columns in the table from the length of a dictionary
        table.append([])
        tablename.append(columns)
        
    print(f"Temp {csvname} table created successfully") #check sum 
    
    for index,lineresult in enumerate(results): #only applicable to dictionarys
        for keyindex,key in enumerate(lineresult.keys()): #dynamically retrieve labels and insert into csv columns
            table[keyindex].append(lineresult[key]) # must remember ur column one is the processed string
        if index %100 == 0 and index != 0 : #Check Status
            print("Currently processed {} results".format(index))
            
    localdf = pd.DataFrame()
    header = list(results[0].keys())
    print(f"Headers are {header}")
    
    print("Table is of {} columns ".format(len(table)))
    for index,keycolumn in enumerate(table): 
        print(f"{index} : {keycolumn}")
        df=pd.DataFrame(pd.Series(keycolumn),columns=[header[index]]) #Ensure column formatting does not matter, so if my column is list of list i have no issues creating it
        localdf = pd.concat([localdf,df] , axis = 1) #concat side by side 
    localdf.to_csv(filesavedname)
    
    return "Successfully saved at {}".format(filesavedname)


def getsentimentcsv(processedstring):
    classifier = pipeline("sentiment-analysis")
    results = classifier(processedstring)
    for index,eachcomment in enumerate(processedstring): #insert a comment key value pair into each line 
        results[index]["comment"] = eachcomment
    try:
        store_as_csv(results,"sentiment-analysis.csv")
    except:
        pass
def getlabelscsv(processedstring):
    results = labelcomments(processedstring,labels) #get labels for these comments
    store_as_csv(results, "Labelled Comments.csv" ) #store labels

def commandpromptchecker(results,processedstring):
    
    for i in range(len(results)): #for each result in result
        print(processedstring[i]) #get the relevant text from the source list
        print(results[i]) #print that dictionary of results for that comment
        print(results[i]['label']) # print sentiment
def getrelevantcomments(targetlabel):
    df = pd.read_csv("Labelled Comments.csv" ) # get the df object
    labelcolumn = "classified"
    commentcolumn = "sequence"
    newnames = df.loc[df[labelcolumn] == targetlabel][commentcolumn] #retrieve the comments with the targetlabel
    return [x for x in newnames] #return a list of comments that suits the relevance
    
def getcommonwords(comparetotopwords):
    if comparetotopwords:
        top_words = pd.read_pickle("support/%s/top_words.pkl" % str(search_terms))
        top_words = pd.DataFrame(top_words)
        topwordslist = []
        size = top_words.shape
        for x in range(size[0]): #extract all top words
            for y in range(size[1]):
                topwordslist.append(top_words[y][x])
                
        componentlist  =pd.read_csv("Components.csv") #Get component list <alert>
        commonwords = []
        topwordscleaned = []
        for items in topwordslist:
            topwordscleaned.append(items[0])
        print(topwordscleaned)
        for items in componentlist["Components"]: #find same words
            print(f"Checked : {items}")
            if items.lower() in topwordscleaned:
                commonwords.append(items.lower())
        return commonwords
    else:
        specs =pd.read_csv("Components.csv")
        outlist = []
        for items in specs["Components"]:
            outlist.append(items.lower())
        return outlist

def get_comments_with_speclist(comments, speclist):
    relevantcomments = []
    relevantword = []
    for eachcomment in comments:
        wordincomment=False
        wordlist = []
        for word in speclist:
            
            if word in eachcomment:
                wordlist.append(word)
                wordincomment=True
                
        if wordincomment:
            relevantcomments.append(eachcomment)
            relevantword.append(wordlist)
            
    return relevantcomments,relevantword

search_terms = pd.read_pickle("support/_current_/searchTerms.pkl") #get current terms
clean_comments = pd.read_pickle("support/%s/clean_comments.pkl" % str(search_terms)) # get clean comments
processedstring = consolidate_comments(clean_comments) #list of comment strings for sentiment analysis
processedstring = remove_empty_comments(processedstring) #remove empty comments
commonwords = getcommonwords(False) #get common spec words and top words
print("Spec words are {}".format(commonwords))
processedstring,commentword = get_comments_with_speclist(processedstring,commonwords) #get list of relevant comments and also the associated word
commentdf = pd.DataFrame(zip(processedstring,commentword),columns=["relevantcomments","Common Word"])
commentdf.to_csv("relevantcomments.csv") #save the data.
labels = ["Design Specifications", "Feelings" , "Advertising"] #define ur own labels to classify comments
getlabelscsv(processedstring[0:10]) #store labels as csv for the first 10
processedstring = getrelevantcomments("Design Specifications")
comments_with_components = []
for word in commonwords:
    print(word)
    for comment in processedstring:
        if word in comment:
            comments_with_components.append(comment)
        else:
            pass            
        
print("There are {} comments that match your design specifications.".format(len(comments_with_components)))
getsentimentcsv(comments_with_components) #store sentiment as csv form these comments
df = pd.read_csv("sentiment-analysis.csv")
averagespecsentiment = {}
for eachspec in pd.read_csv("Components.csv")["Components"]: # this creates a new dictionary for each spec
    averagespecsentiment[eachspec] = {"positive" : 0 , "negative" : 0 } 
