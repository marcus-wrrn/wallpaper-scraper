import json
import requests
import os
import shutil
import clientInfo as ci

# Helper function to get the height and width of a wallpaper
def getResolution(datPost):
    resolution = datPost["preview"]["images"][0]["source"]
    return resolution["width"], resolution["height"]

# assign all post data to the
def assignPostData(post: json, postInfo: dict):
    # get the url to the image/gif
    postInfo["url"].append(post["url_overridden_by_dest"])
    # get post title
    postInfo["title"].append(post["title"])
    # Write flag to show that it is an image or not
    postInfo["image"].append(True if not "gif" in post["url"] else False)
    # Find the width and the height of the image/gif
    width, height = getResolution(post)
    postInfo["height"].append(height)
    postInfo["width"].append(width)
    # Check to see if it's NSFW
    postInfo["NSFW"].append(True if "nsfw" in post["thumbnail"] else False)
    # Get number of upvotes and ratio of upvotes
    postInfo["ups"].append(post["ups"])
    postInfo["upRatio"].append(post["upvote_ratio"])
    

# Gets all posts from a json object including art work, returns a dictionary with all data of each post and the number of posts found
def getPostData(posts):
    # Stores information about the image
    postData = {
        "image":      [],
        "title":      [],
        "height":     [],
        "width":      [],
        "url":        [],
        'ups':        [],
        "upRatio":    [],
        "NSFW":       []
    }
    # Number of posts with art
    postCount = 0
    for i in range(len(posts)):
        post = posts[i]["data"]
        if "url_overridden_by_dest" in post and "preview" in post:
            # Increase the count of the posts
            postCount += 1
            # assign all data to the post
            assignPostData(post, postData)
    return postData, postCount


# Checks to see if the number of posts scraped is correct
def checkPostLength(postData: dict, numOfPosts: int):
    correctLen = True
    if len(postData["image"]) != numOfPosts:
        correctLen = False
    if len(postData["height"]) != numOfPosts:
        correctLen = False
    if len(postData["width"]) != numOfPosts:
        correctLen = False
    if len(postData["url"]) != numOfPosts:
        correctLen = False
    if len(postData["ups"]) != numOfPosts:
        correctLen = False
    if len(postData["upRatio"]) != numOfPosts:
        correctLen = False
    if len(postData["NSFW"]) != numOfPosts:
        correctLen = False
    return correctLen

# takes json post data from a subreddit and returns a dictionary containing a list of post info
def getPostsFromReddit(subreddit, payload, headers, base_url):
    print("Retrieving Posts from subreddit: " + subreddit)
    response = requests.get(base_url + subreddit, params=payload, headers=headers).json()
    print("Posts retrieved...")
    return getPostData(response["data"]["children"])

# downloads an image from the internet writes it to the filepath specified
# NOTE: Will overwrite anything on the filepath, use with caution
def downloadPicture(url: str, filepath: str):
    # Get picture from the internet
    picture = requests.get(url)
    # If a file already exists on the path delete the picture
    if(os.path.exists(filepath)):
        os.remove(filepath)
    # Write the image to the path
    with open(filepath, "wb") as f:
        f.write(picture.content)

def saveWallpaper():
    name = input("Enter wallpaper name: ")
    # This is the filepath for where all wallpapers are stored (in Ubuntu) this has to be changed for anybody using a different os
    mainWallpaperFilePath = ci.savedWallpaperFilePath + str(name)
    shutil.copy(ci.wallpaperFilepath, mainWallpaperFilePath)

def moveWallpaper(oldFilePath, newFilePath):
    if(os.path.exists(newFilePath)):
        os.remove(newFilePath)
    shutil.copy(oldFilePath, newFilePath)