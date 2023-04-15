# Image Scraping from Wikipedia
import requests
from bs4 import BeautifulSoup
import os
       
def wikipedia_scrape_and_generate_image(prompt):
    url = "https://en.wikipedia.org/wiki/"+prompt #requires prompt to have word1_word2:
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    infobox = soup.find("table", {"class": "infobox"})
    image_url = infobox.find_all("img")
    count = 1
    for img in image_url:
        img_url = 'http:' + img["src"]
        if '.jpg' in img_url:  #Stores 
            file = prompt + str(count) + '.jpg'
        if'.png' in img_url:
            file =  prompt + str(count) + '.png'
        if'.jpeg' in img_url:
            file = prompt + str(count) + '.jpeg'
        image_response = requests.get(img_url)
        path = os.path.join("img", file)  # path including the folder name "img"
        with open(path, "wb") as f: #Product Image stored in directory
            f.write(image_response.content)
        count +=1
        print("Image Generated")
        print(img_url)
        print(path)


    





  
    

