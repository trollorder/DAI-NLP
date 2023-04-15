from transformers import pipeline,AutoModelForQuestionAnswering, AutoTokenizer
import pandas as pd
import openai
import time
from wiki_product_img_scrape import wikipedia_scrape_and_generate_image
from Sentiment_plotter import get_sentiment_analysis_graph
from Generate_Report import get_report
from Get_Youtube_Comments import get_youtube_comments
from Clean_youtube_comments import clean_youtube_comments
from youtubecommentconsolidator import generate_youtubecomments_df
from get_amazon_reviews import get_product_review_amazon
#turn table of comments to a list
def consolidate_comments(clean_comments):
    processedcomments = []
    for video in clean_comments:
        for comment in video:
            processedcomments.append(comment)
    return processedcomments

#remove empty comments
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
            
#zero shot to get design labels
def labelcomments(commentdf,labels):
    classifier = pipeline("zero-shot-classification")
    predicted_labels = classifier(list(commentdf["Relevant Comments"]),labels)
    for index, eachresult in enumerate(predicted_labels) :  #Extract the highest probability label and insert into results
        eachresult["classified"] = eachresult["labels"][eachresult["scores"].index(max(eachresult["scores"]))]
        eachresult["Components List"] = commentdf["Components List"][index]
        eachresult["label confidence score"] = max(eachresult["scores"])
    #this predicted labels is actually a table
    
    return predicted_labels

#store any input table as csv with the name 
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


#do sentiment analysis with input list of comments and will store the sentiment in addition to the original csv
def getsentimentcsv(inputdf):
    name = inputdf.name
    classifier = pipeline("sentiment-analysis")
    commentlist = list(inputdf["comment"])
    tokenizer_kwargs = {'padding':True,'truncation':True,'max_length':512}
    results = classifier(commentlist,**tokenizer_kwargs) #comment column
    table_of_results  = [[] for columns in results[0]]
    #the below code basically turns the dictionary into a table 
    for eachdict in results:
        for index,eachcolname in enumerate(list(eachdict.keys())):
            table_of_results[index].append(eachdict[eachcolname])
    resultsdf = pd.DataFrame(table_of_results)
    resultsdf = resultsdf.transpose()
    resultsdf.set_axis(["Sentiment" , "Sentiment Confidence Score"] , axis=1 , inplace = True)
    inputdf = pd.concat([inputdf , resultsdf ], axis = 1)
    dfname = "{} Sentiment Analysis.csv".format(name)
    try:
        
        inputdf.to_csv(dfname)
        print(f"Sentiment Analysis csv created with name {dfname}")
    except:
        print(f"Failed To save {dfname} ")

#do zero shot classification for comments with input labels
def getlabelscsv(commentdf , labels):
    results = labelcomments(commentdf,labels) #get labels for these comments
    store_as_csv(results, "Labelled Comments.csv" ) #store labels

#check the processed string
def commandpromptchecker(results,processedstring):
    for i in range(len(results)): #for each result in result
        print(processedstring[i]) #get the relevant text from the source list
        print(results[i]) #print that dictionary of results for that comment
        print(results[i]['label']) # print sentiment

#get the relevant comments labelled as target label
def getrelevantcommentswithdesignspecs(targetlabel):
    df = pd.read_csv("Labelled Comments.csv" ,index_col=0) # get the df object
    labelcolumn = "classified"
    commentcolumn = "sequence"
    newnames = df.loc[df[labelcolumn] == targetlabel] #retrieve the comments with the targetlabel
    return newnames #return a list of comments that suits the relevance
   
#read a list of all components 
def getcomponentlist():
    specs =pd.read_csv("Components.csv",index_col=0) #gotten from chat gpt
    outlist = []
    for items in specs["Components"]:
        outlist.append(items.lower())
    return outlist


def get_comments_with_component(commentsdf, component_list):
    commentdf = commentsdf.copy()
    commentcol = commentdf["comment"]
    finaltable = {} #create a table of comments
    for component in component_list:
        for idx,comment in enumerate(commentcol):
            if component in comment :
                if comment == "":
                    continue
                if comment not in finaltable.keys():
                    finaltable[comment] = [component]
                else:
                    finaltable[comment] += [component]
    table = pd.DataFrame([list(finaltable.keys()) , list(finaltable.values())])
    table.fillna("No Comment")
    table = table.transpose()
    table.columns = ["Relevant Comments" , "Components List"] 
    table.to_csv("relevantcomments.csv")
    return 

#wordmatching 
def wordmatchcomment_list(comments,componentlist):
    comments_with_components = []
    for word in componentlist:
        print(word)
        for comment in comments:
            if word in comment.lower(): #this lower ensures it doesnt miss out the words
                comments_with_components.append(comment)
            else:
                pass     
    return comments_with_components 
    
#ask chatgpt for specifications
def askonequestion(product, components):
    completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": f"Give me the properties of a {product} {components} in a python dictionary. Do not print anything other than the python dictionary"}])
    time.sleep(10)
    print(completion.choices[0].message.content)
    try:
        category_dict = eval(completion.choices[0].message.content)
    except:
        print(f"Cant parse {product} {components}")
        print(f"Will exclude {components} from component list")
        category_dict={}
    return category_dict

#get specslist from component list
def getspecsofcomponents(product,componentlist) :
    categorylist = []
    for index, components in enumerate(componentlist):
        temp_dict = askonequestion(product,components)
        categorylist.append({f"{components}":temp_dict})
    #category list looks like this [{component: {specification1 : dimensions , specification2 : dimensions}}]
    table = [[] for x in range(3)]
    for index,componentdict in enumerate(categorylist):
    #u get a dictionary like this {component:{spec : di , spec : di}}
        for eachspec in componentdict[componentlist[index]].keys(): #get each spec key
            table[0].append(componentlist[index])
            table[1].append(eachspec)
            table[2].append(componentdict[componentlist[index]][eachspec])
    dfspecs = pd.DataFrame(zip(table[0],table[1],table[2]),columns=["component" , "specs","details"])
    dfspecs.to_csv("specslist.csv") #generate the specs list
    print(f"Specslist generated with name specslist.csv")
    return 

#this function, does word matching for each component and its associated category Obsolete
def get_comments_with_speclistdf(commentdf, componentcategorydf): 
    componentcategorytuplelist = [list(row) for idx, row in componentcategorydf[componentcategorydf.columns.tolist()[1:]].iterrows()] #pulls the tuple #pulls the comment 
    localdf = pd.DataFrame(columns=["comments" , "components" , "component" , "specs", "details"]) #local instance for appending
    for index,eachcomment in commentdf[commentdf.columns.tolist()[1:]].iterrows():  #this means each row
        wordincomment = False
        commentcolumn = eachcomment["Relevant Comments"]
        for eachtuple in componentcategorytuplelist:
            if eachtuple[0] in commentcolumn and eachtuple[1] in commentcolumn:
                wordincomment = True
            if wordincomment:
                toappend = list(eachcomment) + eachtuple
                print(toappend)
                localdf.loc[len(localdf)] = toappend #so we add to the last row of the localdf
    return localdf

#chatgpt ask for components 
def getchatgptcomponents(product):
    print("Asking ChatGPT for components")
    completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": f"Retrieve the generic parts of a {product} in a python list. Do not print anything other than the python list."}])
    time.sleep(10)
    try:
        list_of_components = eval(completion.choices[0].message.content)
        print("Sourced Components successfully")
        return list_of_components
    except:
        print(f"Chat GPT Can't parse {product}")
        return ["Unparseable"]
    return 

def zeroshotallcomponents(commentdf,specificationlist):
    #table of results to append on 
    table_of_results  = [[],[],[]]
    table_of_results += [[] for x in commentdf.columns]
    #these indices locate the rows in a series to retrieve
    commentcol = 0
    component_list = 4
    print(commentdf.columns)
    classifier = pipeline("zero-shot-classification")
    for indexrow , eachcomment in commentdf.iterrows():
        #perform zeroshot on the comment by retreiving the all specs to that component from speclistdf object
        component_list = eval(eachcomment["Components List"])
        # iterate incase there is more than
        for comp in component_list:
            comment_to_process = str(eachcomment["comment"])
            if len(comment_to_process) == 0:
                continue
            labels_to_use = list(specificationlist.loc[specificationlist["component"] == comp]["specs"])
            print(comment_to_process)
            print(labels_to_use)
            predicted_labels = classifier(comment_to_process,labels_to_use)

            predicted_labels["Specification"] = predicted_labels["labels"][predicted_labels["scores"].index(max(predicted_labels["scores"]))]
            predicted_labels["Specification Confidence Score"] = max(predicted_labels["scores"])
            predicted_labels["specific component"] = comp
            #cleans unnecessary cols
            del(predicted_labels["scores"])
            del(predicted_labels["labels"])
            del(predicted_labels["sequence"])
        
            #the below code basically turns the dictionary into a table 
            for commentcols, prevkey in enumerate(eachcomment):
                table_of_results[commentcols].append(prevkey)
            existingcol = len(eachcomment)
            for index,key in enumerate(predicted_labels.keys()):
                table_of_results[index+existingcol].append(predicted_labels[key])
            
            

        print(f"Done row {indexrow}")
        
    
    resultsdf = pd.DataFrame(table_of_results)
    resultsdf = resultsdf.transpose()
    resultsdf.set_axis(list(commentdf.columns) + ["Specification" , "Specification Confidence Score" , "Specific Component"] , axis=1 , inplace = True)
    dfname = "Specification labelled relevant comments.csv"
    try:
        
        resultsdf.to_csv(dfname)
        print(f"Specification labelled relevantcomment.csv created")
    except:
        print(f"Failed To save {dfname} ")
    return 
def get_comp_specs_chatgpt(product):
    #Generate List of Components and consequently specifications for each 
    componentlist = getchatgptcomponents(product)
    #save the components
    dfcomponents = pd.DataFrame(componentlist , columns=["Components"])    
    #ask chatgpt for specs for each component and store them thereafter
    getspecsofcomponents(product,componentlist) 
    
    localspecdf=pd.read_csv("specslist.csv",index_col=0)
    dfcomponents["Components"] = dfcomponents.loc[dfcomponents["Components"].isin(localspecdf["component"])]
    dfcomponents.to_csv("Components.csv")

    print("Successfully generate Components.csv and specs.csv")
    return 

def chatgptgetrecommendations(dictionary_of_components):
    recco = {}
    print("Asking ChatGPT for recommendations")

    for compname , compdict in dictionary_of_components.items():
        if len(compdict["Related Comments"]) > 0 :
            recco[compname] = compdict
    for compname , compdict in recco.items():
        questionstring = ""
        for eachline in compdict["response list"]:
            questionstring += eachline + "/n"
        completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": f"{questionstring} . \n With the above text, generate me a recommendation for how to improve a {product} . If you can't answer it, reply with 'No Recommendation Given'"}])
        answer =completion.choices[0].message.content
        compdict["Recommendation"] = answer
        compdict["Component Specification"] = compname
        print(f"Recommendation for {compname} gotten. \n Response is {answer}")
        time.sleep(20)
    #now generate the recommendation
    recco = pd.DataFrame(recco)
    recco = recco.transpose()
    recco.columns = ["Benchmark" , "Related Comments" , "Sentiment Cumulative Score" , "Component", "response list" , "Recommendation","Component Specification"]
    filename = "Recommendation.csv"
    recco.to_csv(filename)
    print(f"{filename} is generated ")


def amazon_comments_SA():
    amazon_reviewsdf = pd.read_csv("amazon_reviews.csv",index_col=0)
    amazon_reviewsdf.name = "amazon_review"
    amazon_reviewsdf['comment'] = amazon_reviewsdf['comment'].fillna("No Comment")
    getsentimentcsv(amazon_reviewsdf) 
    
def youtube_comments_SA():
    youtube_reviewdf=pd.read_csv("youtube comments.csv" ,index_col=0)
    youtube_reviewdf.name="youtube_comments"
    youtube_reviewdf["comment"] = youtube_reviewdf['comment'].fillna("No Comment")
    getsentimentcsv(youtube_reviewdf) 
    
openai.api_key = "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"    
product = "apple watch"
#wikipedia_scrape_and_generate_image(product)
#product  = input("Key in your product for analysis ")
#get_youtube_comments(search_terms=product,max_results=20)
#clean_youtube_comments()
#generate_youtubecomments_df()
#get_product_review_amazon(product)

#plot the graphs from Sentiment Analysis
##amazon_comments_SA()
#youtube_comments_SA()

#get_comp_specs_chatgpt(product)
#get specslist from specslist.csv and component list from component.csv
specslist = pd.read_csv("specslist.csv",index_col=0) 
componentlist = getcomponentlist()
    


#code below to get commentdf
amazoncommentdf = pd.read_csv("amazon_reviews.csv" , index_col=0)
youtubecommentdf = pd.read_csv("youtube comments.csv" , index_col= 0)

print("Word Matching Now")
#code below for word matching for youtube
get_comments_with_component(youtubecommentdf,componentlist)
commentdf =pd.read_csv("relevantcomments.csv",index_col=0)

print("Labelling Comments Now")
labels = ["Design Specifications", "Advertising" , "Software" ] #define ur own labels to classify comments
#getlabelscsv(commentdf,labels) #Generate labelled comments for design specs for design specs and everything else
labelleddf = pd.read_csv("Labelled Comments.csv",index_col=0) #works

labelledcommentsdf = getrelevantcommentswithdesignspecs("Design Specifications") #Generate relevantcomments that suit the label
labelledcommentsdf.reset_index(drop=True,inplace=True)
labelledcommentsdf.to_csv("labelled relevant comments.csv")

print("Getting Sentiment Now")
#get sentiment for labelled relevant comments
labelledcommentsdf.rename(columns={'sequence': 'comment'}, inplace=True) #rename sequence to comment
labelledcommentsdf.name = "labelled relevant comment"
#getsentimentcsv(labelledcommentsdf) 

print("Splitting to Components now")
#zeroshot component and specification works
labelledrelevantcommentdf = pd.read_csv("labelled relevant comment Sentiment Analysis.csv",index_col=0)
#zeroshotallcomponents(labelledrelevantcommentdf,specslist)

compspecssentdf = pd.read_csv("Specification labelled relevant comments.csv" , index_col=0)

print("Generating Component Specs Dictionaries")
#Getbenchmark from specslist component	specs	details
#so this dictionary below will be {"component spec": { Benchmark : "" , Related Comments : [] , Sentiment Cumulative Score : 0}}
dict_spec_comp = {}
for idx, eachrow in specslist.iterrows():
    componentname,specname,details = eachrow["component"],eachrow["specs"],eachrow["details"]
    dict_spec_comp[f"{componentname} {specname}"] = {}
    dict_spec_comp[f"{componentname} {specname}"]["Benchmark"] = details
    dict_spec_comp[f"{componentname} {specname}"]["Related Comments"] = []
    dict_spec_comp[f"{componentname} {specname}"]["Sentiment Cumulative Score"] = 0
    dict_spec_comp[f"{componentname} {specname}"]["Component"] = eachrow["component"]

# get the Sentiment Cumulative Score for each component specs and gather the comments 
for idx,eachrow in compspecssentdf.iterrows():
    component = eachrow["Specific Component"]
    specs = eachrow["Specification"]
    if eachrow["Sentiment"] == "POSITIVE" and eachrow["Sentiment Confidence Score"] > 0.5 :
        score = 1
    elif eachrow["Sentiment"] == "NEGATIVE" and eachrow["Sentiment Confidence Score"] > 0.5:
        score = -1
    else :
        score = 0
    
    dict_spec_comp[f"{component} {specs}"]["Related Comments"] +=[eachrow["comment"]]
    dict_spec_comp[f"{component} {specs}"]["Sentiment Cumulative Score"] += score
    
#so at this point we have a dictionary of related comments and the score for each the more negative the score the more important it is


        
            
            
    
    
def qnacomments(dict_spec_comp):
    for componentspec , compdict in dict_spec_comp.items():
        if len(compdict["Related Comments"]) > 0 : #if that particular component has a comment
            print(compdict["Related Comments"])
            model_name = "deepset/roberta-base-squad2"
            nlp = pipeline('question-answering', model=model_name, tokenizer=model_name)
            qnaresponselist = [] #results are score , strat, end , answer
            for comment in compdict["Related Comments"]:
                #do QnA on each
                QA_input = {
                'question': f'How to make {componentspec} better?',
                'context': comment
                }
                res = nlp(QA_input)
                qnaresponselist.append(res["answer"])
            print(f"For {componentspec} the responses is a such {qnaresponselist}")
            compdict["response list"] = qnaresponselist
#qnacomments(dict_spec_comp)
print("Getting Reccomendations")
#chatgptgetrecommendations(dict_spec_comp)
#get_sentiment_analysis_graph(product)

accuracydf = pd.read_csv("evaluation scores.csv")

"""
numberofcomments = int
overallsentiment = Positive or Negative
componentliststring = list of strings
promptliststring = Prompts
accuracy = int
"""

commentparsed = len(youtubecommentdf)
overallsentiment = "Positive"
promptlist = ["{questionstring} . \n With the above text, generate me a recommendation for how to improve a {product} . If you can't answer it, reply with 'No Recommendation Given'",
              "Give me the properties of a {product} {components} in a python dictionary. Do not print anything other than the python dictionary"
              , "Retrieve the generic parts of a {product} in a python list. Do not print anything other than the python list."]
class_acc ={"Classification Accuracy" :round(accuracydf["classification accuracy"][0],2)}
sent_acc = {"Sentiment Accuracy" : round(accuracydf["accuracy"][0],2)}
class_acc.update(sent_acc)
accuracy = class_acc


get_report(product, globalvalues={"numberofcomments" : commentparsed , 
                                  "globalsentiment" : overallsentiment,
                                  "componentliststring" : list(componentlist),
                                "promptliststring" : promptlist,
                                "accuracy":str(accuracy)})