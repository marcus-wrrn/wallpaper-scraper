import sys
import requests
# Import required info for access to the reddit api + filepath info specific to the users computer
import clientInfo as ci
import postHandling as phan
from os import listdir
import inquirer
import subprocess


# Global variable for whether to turn on roulleteMode or not
roulleteMode = False

def getAPIHeaderData():
    # url for reddit
    reddit_url = 'https://www.reddit.com/'
    # Required data to access API
    # Note that the user must use their own bot information, details for creating a bot is explained in the reddit api docs
    data = {'grant_type': 'password', 'username': ci.username, 'password': ci.password}
    auth = requests.auth.HTTPBasicAuth(ci.client_id, ci.secret)
    r = requests.post(reddit_url + 'api/v1/access_token',
                  data=data,
                  headers={'user-agent': ci.user_agent},
		          auth=auth).json()
    # Get Access token
    token = 'bearer ' + r['access_token']
    # Return all the header data for the api
    return {'Authorization': token, 'User-Agent': ci.user_agent}

def connectToReddit(base_url, headers):
    try:
        requests.get(base_url + '/api/v1/me', headers=headers)
    except:
        print("unable to connect to the reddit servers")

# Gets the command line arguments of the user
# For now only allows user to specify subreddit, defaults to r/wallpaper
def getUserArgs():
    subreddit = "/r/wallpaper"
    argCount = len(sys.argv)
    if argCount >= 2:
        subreddit = "/r/" + sys.argv[1]
    return subreddit


# Returns true if the post is an image and not tagged NSFW, if roullete mode is turned on NSFW tags are ignored
def validatePost(posts, i):
    if (roulleteMode and posts["image"][i]):
        return True
    if (not roulleteMode and posts["image"][i] and not posts["NSFW"][i]):
        return True
    return False

# Downloads the first valid post and returns its index value
def downloadFirstPost(posts, postCount, filePath):
    for i in range(postCount):
        if(validatePost(posts, i)):
            phan.downloadPicture(posts["url"][i], filePath)
            return i
    return postCount

def selectWallpapaer(firstPostIndex, posts, postCount, filePath1, filePath2,):
    alternate = False
    # Loops through all stored posts
    for i in range(firstPostIndex + 1, postCount):
        # If the post has a picture and is not NSFW (roullete mode ignores NSFW tags) download the picture
        if(validatePost(posts, i)):
            if not alternate:
                phan.downloadPicture(posts["url"][i], filePath2)
                subprocess.run(["./change_wallpaper_path.sh", filePath1])
            else:
                phan.downloadPicture(posts["url"][i], filePath1)
                subprocess.check_call(["./change_wallpaper_path.sh", filePath2])
            
            # Ask the user if they'd like to keep the wallpaper or pick a different one
            if getUserInput("Keep Wallpaper"):
                # If the user wants to keep the wallpaper ask if they'd like to save it permanently
                if getUserInput("Would you like to save the wallpaper permanently"):
                    # Save the wallpaper using the filepath specified in clientInfo.py
                    phan.saveWallpaper()
                # close the loop as a wallpaper has been chosen
                break
            alternate = True if not alternate else False

# Changes the wallpaper on your computer
def changeWallpaper(wallpaperFilepath, posts, postCount):
    filePathTemp1 = "/home/marcus/Projects/InternetAnalysis/wallpaper-scraper/wallpaper-scraper/wallpapers/wallpaper1"
    filePathTemp2 = "/home/marcus/Projects/InternetAnalysis/wallpaper-scraper/wallpaper-scraper/wallpapers/wallpaper2"
    firstPictureNum = downloadFirstPost(posts, postCount, filePathTemp1)

    


# Getting saved wallpaper from file
def changeWallpaperSaved(savedWallpaperFilePath=ci.savedWallpaperFilePath):
    files = listdir(savedWallpaperFilePath)
    # Let the user choose which filepaper to use
    wallChoice = [inquirer.List("Wallpaper", message="Select Wallpaper to use", choices=files)]
    wallpaper = inquirer.prompt(wallChoice)["Wallpaper"]
    phan.moveWallpaper(savedWallpaperFilePath + wallpaper, ci.wallpaperFilepath)


def changeWallpaperFromReddit():
    # base url used for the reddit api
    base_url ='https://oauth.reddit.com'
    # headers needed to request data from api
    print("Getting Header Data...")
    headers = getAPIHeaderData()
    print("Connecting to Reddit...")
    # Connect to reddit api, if not throw an error
    connectToReddit(base_url, headers)
    print("Connected...")
    # subreddit that the wallpapers originate
    subreddit = getUserArgs()
    # parameters for what sort of information the script will be requesting
    # for now only the post limit is used, the default is 200 as that is the maximum number of posts the API can take at once
    # NOTE this limit is not equal to the total number of wallpapers available to the user, posts containing gifs/text or multiple images are ignored
    payload = {'limit': 200}
    # Gets all posts from reddit, posts is a dictionary object containing lists of information for each post, postNum is the number of viable posts found
    posts, postNum = phan.getPostsFromReddit(subreddit, payload, headers, base_url)
    # Changes the wallpaper of the user
    changeWallpaper(ci.wallpaperFilepath, posts, postNum)


# Returns true if the user presses Y or y for an input prompt, False otherwise
def getUserInput(message: str):
    userChoice = input(message + " y/n: ")
    if(userChoice == 'y' or userChoice == 'Y'):
        return True
    return False

def makeWallpaperSelection():
    modeChoice = [inquirer.List("Mode", message="How would you like to change your wallpaper?", choices=["From saved wallpapers", "Get new wallpaper from Reddit"])]
    choice = inquirer.prompt(modeChoice)["Mode"]
    return choice == "From saved wallpapers"


def main():
    # Choose whether or not to get wallpaper from your saved wallpaper folder or from reddit
    # If any extra parameters are used assume that the user wants to get wallpaper from reddit
    # i.e if the user specified a subreddit to use assume that they want to get their wallpaper from that subreddit
    getSavedWallpaper = False if len(sys.argv) >= 2 else makeWallpaperSelection()
    if getSavedWallpaper:
        changeWallpaperSaved()
    else:
        changeWallpaperFromReddit()

if __name__ == "__main__":
    main()
