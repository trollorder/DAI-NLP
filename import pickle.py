import pickle
import pandas as pd
df = pd.read_pickle(r"C:\Users\Latitude\Desktop\NLP Example\support\children wearable\clean_comments.pkl")
top5 = df[0] #Get first video
print(type(df))
count = 0 
total_count = 0
for x in range(len(df)):
    for items in df[x]:
        total_count += 1
print(f"There are {len(df)} videos.")
print(f"There are {total_count} comments in total")
print("The first 5 comments are:")
for comments in df[0]:
    count += 1
    print(f"comment {count} is : {comments}")
    if count >=5:
        break
    


