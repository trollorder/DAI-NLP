import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
import time

#Function to generate list of product review url from product listing url
def generate_review_url(url):
    # Set up the WebDriver with the appropriate options
    driver = webdriver.Chrome('chromedriver.exe')

    try:
        # Navigate to the product page
        driver.get(url)

        # Extract the page source and parse it with Beautiful Soup
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Find the "See all reviews" hyperlink
        see_all_reviews_link = soup.find('a', {'data-hook': 'see-all-reviews-link-foot'})

        # Print the link URL
        review_url = 'https://www.amazon.com' +  see_all_reviews_link['href']
        return review_url

    finally:
        # Quit the WebDriver
        driver.quit()
    
#Function to retrieve product links from Amazon search url
def generate_urls(soup): 
    url_no = 10 #no of product listing url to scrape
    links = soup.find_all("a", attrs={'class':'a-link-normal s-no-outline'})
    links_list = []
    # Loop for extracting links from Tag Objects
    for link in links[:url_no]: 
        url = "https://www.amazon.com" + link.get('href')
        links_list.append(url)
    return links_list



# Function to extract Product Title
def get_title(soup):
    
    try:
        # Outer Tag Object
        title = soup.find("span", attrs={"id":'productTitle'})
        
        # Inner NavigatableString Object
        title_value = title.text

        # Title as a string value
        title_string = title_value.strip()

    except AttributeError:
        title_string = ""

    return title_string


#Function to scrape reviews, list append in place
def get_reviews(soup,review_list): 
    
    try:
        time.sleep(1)
        reviews = soup.find_all('div', {'data-hook': 'review'})
        for item in reviews:
            review = {
            'title': item.find('a', {'data-hook': 'review-title'}).text.strip(),    
            'rating':  float(item.find('i', {'data-hook': 'review-star-rating'}).text.replace('out of 5 stars', '').strip()),
            'comment': item.find('span', {'data-hook': 'review-body'}).text.strip(),
            'timestamp': item.find('span', {'data-hook': 'review-date'}).text.replace('Reviewed in the United States on','').replace("Reviewed in the United States 🇺🇸 on", '').strip(),
            }
            if (item != None) :
                review_list.append(review)
    except:
        pass


#Function to generate soup object from url    
def get_page_contents(url):
    user_agent = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:106.0) Gecko/20100101 Firefox/106.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Referer": "https://www.amazon.com/",
    "DNT": "1",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1"
}
    page = requests.get(url, headers = user_agent)
    return BeautifulSoup(page.text, 'html.parser')


#Function to generate Amazon reviews from product prompt and returns a list of dictionaries(reviews)
def generate_amazon_reviews(prompt): 
    HEADERS = ({'User-Agent':"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 Edge/16.16299", 'Accept-Language': 'en-US, en;q=0.5'})
    
    # Amazon search page URL
    search_url = "https://www.amazon.com/s?k="+prompt

    # HTTP Request
    webpage = requests.get(search_url, headers=HEADERS)
    
    # Soup object for search window with prompt
    search_soup = BeautifulSoup(webpage.content, "html.parser")
    
    #generate dataset
    reviewList = []

    
    #Iterate through product listings
    prod_url = generate_urls(search_soup)
    for url in prod_url[:4]:
        
        print("Product url:" + url)
        review_url = generate_review_url(url) #retrieve review link from product listing
        print("Review url:" + review_url)
        for x in range(1,25): #iterate through pages of the 
            print(f'Getting page: {x}')
            page_url = review_url+"&pageNumber="+str(x) #changes the individual page of reviews
            print(page_url)
            soup = get_page_contents(page_url)
            get_reviews(soup,reviewList) #scrape review from page
            if not soup.find('li', {'class': 'a-disabled a-last'}):
                pass
            else:
                break
            print(len(reviewList))          
    print("---Scraping Complete---")
    return reviewList
        
def get_product_review_amazon(product):
    all_reviews = generate_amazon_reviews(product) #product prompt
    print('Total review count: ' + str(len(all_reviews)))
    prod_df = pd.DataFrame(all_reviews) #main dataset
    print(prod_df)
    prod_df.to_csv("amazon_reviews.csv") #save to csv file
    print("CSV Saved")
    

    
