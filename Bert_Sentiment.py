from transformers import pipeline

text = ["SUTD is the best University!!",
        "I love DAI :)",
        "AI Applications in Design is the most interesting course I have ever taken... ever!"]

classifier = pipeline("sentiment-analysis")

results = classifier(text)

for i in range(len(results)):
    print(text[i])
    print(results[i])
    print(results[i]['label'])
    print("\n")
