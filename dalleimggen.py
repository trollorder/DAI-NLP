import openai
import requests
from transformers import pipeline
import pandas as pd
import time
def get_img_prompt(report_path,product,recommendations):
    openai.api_key = "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"  
    model_name = "deepset/roberta-base-squad2"
    nlp = pipeline('question-answering', model=model_name, tokenizer=model_name)

    promptlist = []
    for recco in recommendations:
        if recco !="No Recommendation Given.":
            QA_input = {
                    'question': f'What should apple change about the apple watch?',
                    'context': recco
                    }
            res = nlp(QA_input)
            prompt_to_ask = res["answer"]
            promptlist.append(prompt_to_ask)
    promptasked = []
    namegen = []
    for index,eachprompt in enumerate(promptlist):
        name,prompt =getimage(report_path,product,eachprompt,index)
        promptasked.append(prompt)
        namegen.append(name)
        pass
    promptaskeddf =pd.DataFrame(zip(promptasked,namegen),columns=["Prompts used for dall e","imgname"])
    promptaskeddf.to_csv(f"{report_path}/{product} dalle prompts used.csv")

def getimage(report_path,product,prompt_to_ask,index):
    completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": f"Generate a image prompt for dall e in less than 60 words enclosed in “” based on {prompt_to_ask} for {product}"}])
    answer = completion.choices[0].message.content
    print(answer)
    time.sleep(20)
    prompt_to_ask = answer + " Hyper Realistic"
    prompt = prompt_to_ask
    
    response = openai.Image.create(
        prompt=prompt ,
        n=1,
        size="1024x1024"
    )

    if "data" in response:
        image_url = response["data"][0]["url"]
        filename = f"{report_path}/img/Dall E Image {index}.png"
        with open(filename, "wb") as f:
            f.write(requests.get(image_url).content)
            print(f"Image saved as {filename}")
    else:
        print("Error generating image.")
    return f"Dall E Image {index}.png",prompt
