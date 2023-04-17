import openai
import pandas as pd
import time
openai.api_key = "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"

def getchatgptranking(report_path):
    reccopath = f"{report_path}/Recommendation.csv"

    reccodf = pd.read_csv(reccopath)
    reccolist = list(reccodf.loc[reccodf["Recommendation"] != "No Recommendation Given."]["Recommendation"])
    #limit the length
    #clean list of "No Recommendation Given."
    print(reccolist)
    
    formatstring = "\n"
    for eachrecco in reccolist:
        formatstring += "'"+str(eachrecco) + "'\n"
    promptstart = "Select 3 recommendations that have the potential to make the product more sustainable and change the 3 recommendations to make it more sustainable."
    prompt = formatstring + promptstart
    print(prompt)
    answer = askchatgpt(prompt,"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")
    
    # save to sustainable.df
    localdf = pd.DataFrame([answer],columns = ["Sustainability ranking"])
    localdf.to_csv("sustainability.csv")
    
    return answer
def askchatgpt(prompt,apikey) :
    openai.api_key = apikey
    prompt = prompt
    completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": prompt}])
    #time.sleep(20)
    print(completion.choices[0].message.content)
    return str(completion.choices[0].message.content)
    
