from googleapiclient.discovery import build
import pickle
import os
import pandas as pd
from google_key import key                      # google_key.py to hide api_key

def code1main(search_terms = "SUTD" , max_results = 20 ):           # INSERT Search words -> "Brand Product Model"
    '''user inputs'''         
    max_result = 20                                 # No. of results (1-50)
    api_key = key                                   # api_key from key in google_key.py
    # Copy & Paste


    '''initialise'''
    youtube = build('youtube', 'v3', developerKey=api_key)

    vid_id = []             	# video id
    vid_page = []       		# video links (https...)
    vid_title = []              # video title
    num_comments = []           # official number of comments
    load_error = 0              # error counter
    can_load_title = []         # temp. list for storing title w/o loading error
    can_load_page = []          # temp. list for storing links w/o loading error
    num_page = []               # comment_response page number
    page_title = []             # comment_response video title
    comment_resp = []           # comment_response
    comment_list = []           # temp. list for storing comments
    comment_data = []           # comments & replies from comment_response
    all_count = 0               # total number of comments


    '''search for videos'''
    print("Search for videos...")
    request = youtube.search().list(
        q=search_terms,
        maxResults=max_result,
        part="id",
        type="video"
        )
    search_response = request.execute()
    print(search_response)
    # Copy & Paste

    for i in range(max_result):
        videoId = search_response['items'][i]['id']['videoId']
        print(videoId)
        vid_id.append(videoId)
        page = "https://www.youtube.com/watch?v=" + videoId
        print(page)
        vid_page.append(page)

    print("There are", len(vid_page), "videos.")
    # Copy & Paste


    '''get video data'''
    print("Get video data...")
    for i in range(len(vid_id)):
        request = youtube.videos().list(
            part="snippet, statistics",
            id=vid_id[i]
            )
        video_response = request.execute()
        print(video_response)
        # Copy & Paste

        title = video_response['items'][0]['snippet']['title']
        vid_title.append(title)
        try:                        # use try/except as some "comments are turned off"
            comment_count = video_response['items'][0]['statistics']['commentCount']
            print("Video", i + 1, "-", title, "-- Comment count: ", comment_count)
            num_comments.append(comment_count)
        except:
            print("Video", i + 1, "-", title, "-- Comments are turned off")
            num_comments.append(0)
        # Copy & Paste


    '''get comment data'''
    print("Get comment data...")
    for i in range(len(vid_id)):
        try:        # in case loading error
            request = youtube.commentThreads().list(
                part="snippet,replies",
                videoId=vid_id[i]
                )
            comment_response = request.execute()
            print(comment_response)
            # Copy & Paste (with except: print("error"))

            comment_resp.append(comment_response)   # append 1 page of comment_response
            pages = 1
            num_page.append(pages)                  # append page number of comment_response
            page_title.append(vid_title[i])         # append video title along with the comment_response

            can_load_page.append(vid_page[i])       # drop link if it can't load (have at least 1 comment page)
            can_load_title.append(vid_title[i])     # drop title if it can't load (have at least 1 comment page)

            test = comment_response.get('nextPageToken', 'nil')     # check for nextPageToken
            while test != 'nil':                                    # keep running until last comment page
                next_page_ = comment_response.get('nextPageToken')
                request = youtube.commentThreads().list(
                    part="snippet,replies",
                    pageToken=next_page_,
                    videoId=vid_id[i]
                    )
                comment_response = request.execute()
                print(comment_response)

                comment_resp.append(comment_response)   # append next page of comment_response
                pages += 1
                num_page.append(pages)              # append page number of comment_response
                page_title.append(vid_title[i])     # append video title along with the comment_response

                test = comment_response.get('nextPageToken', 'nil')     # check for nextPageToken (while loop)
        except:
            load_error += 1
    # Copy & Paste

    print("Videos that can load...")
    vid_page = can_load_page                    # update vid_page with those with no load error
    vid_title = can_load_title                  # update vid_title with those with no load error
    for i in range(len(vid_title)):
        if vid_title[i] == 'YouTube':           # default error title is 'YouTube'
            vid_title[i] = 'Video_' + str(i+1)  # replace 'YouTube' with Video_1 format
        print(i + 1, vid_title[i])
    # Copy & Paste


    '''sift comments into structure'''
    print("Get individual comment...")
    for k in range(len(comment_resp)):
        count = 0                                                     # comment counter
        comments_found = comment_resp[k]['pageInfo']['totalResults']  # comments on 1 comment_response page
        count = count + comments_found
        for i in range(comments_found):
            try:
                comment_list.append(comment_resp[k]['items'][i]['snippet']['topLevelComment']['snippet']['textDisplay'])
                print(comment_resp[k]['items'][i]['snippet']['topLevelComment']['snippet']['textDisplay'])
                # Copy & Paste (with except: print("missing comment or too many"))

                reply_found = comment_resp[k]['items'][i]['snippet']['totalReplyCount']    # for comment 'i'
                count = count + min(reply_found, 5)     # YT provides max of 5 replies per comment
                for j in range(min(reply_found, 5)):
                    try:
                        comment_list.append(comment_resp[k]['items'][i]['replies']['comments'][j]['snippet']['textDisplay'])
                        print(comment_resp[k]['items'][i]['replies']['comments'][j]['snippet']['textDisplay'])
                        print(j+1, 'out of', reply_found, 'replies captured')
                    except:
                        print("missing reply")
            except:
                print("missing comment")            # or too many comments (e.g. 7.3K comments)
        # Copy & Paste (optional)

        comment_data.append(comment_list.copy())    # all comments on 1 comment_response page, use .copy()
        comment_list.clear()
        all_count += count
    combined_data = list(zip(page_title, num_page, comment_data))
    print(combined_data)        # df format later
    print(combined_data[0])     # print entry 1
    print(combined_data[1])     # print entry 2
    # Copy & Paste


    '''create dir and save files'''
    try:                                            # Create directory named after search terms
        os.makedirs("support/%s" % search_terms)
        print("Directory", search_terms, "created")
    except FileExistsError:
        print("Directory", search_terms, "exists")
    pickle.dump(search_terms, open("support/%s/searchTerms.pkl" % search_terms, "wb"))
    pickle.dump(vid_title, open("support/%s/vid_title.pkl" % search_terms, "wb"))
    pickle.dump(vid_page, open("support/%s/vid_page.pkl" % search_terms, "wb"))
    pickle.dump(combined_data, open("support/%s/combined_data.pkl" % search_terms, "wb"))
    pickle.dump(vid_id, open("support/%s/vid_id.pkl" % search_terms, "wb"))

    try:                                            # Create directory to store current search terms
        os.makedirs("support/_current_")
        print("Directory _current_ created")
    except FileExistsError:
        print("Directory _current_ exists")
    pickle.dump(search_terms, open("support/_current_/searchTerms.pkl", "wb"))
    # Copy & Paste


    '''print summary'''
    combined_data = pd.read_pickle("support/%s/combined_data.pkl" % search_terms)   # open as df
    pd.set_option('colwidth', 30)
    df = pd.DataFrame(combined_data, columns=['Title', 'Page', 'Comments'])
    df.to_csv("Information.csv")
    print("\n<<<Summary>>>")
    print("Search terms:", search_terms)
    print(df)
    print("\nThere are", all_count, "comments captured in total")
    print(load_error, "videos had loading errors")
    # Copy & Paste

    # What was said in the video (caption)?
    # How many views did each video receive?
