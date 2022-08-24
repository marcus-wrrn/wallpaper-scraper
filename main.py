from ast import arg
import sys
import requests
# Import required info for access to the reddit api + filepath info specific to the users computer
import clientInfo as ci
import postHandling as phan

roulleteMode = False

def getAPIData():
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
    response = requests.get(base_url + '/api/v1/me', headers=headers)
    return response.status_code == 200

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

# Changes the wallpaper on your computer
def changeWallpaper(wallpaperFilepath, posts, postCount):
    # Loops through all stored posts
    for i in range(postCount):
        # If the post has a picture and is not NSFW (roullete mode ignores NSFW tags) download the picture
        if(validatePost(posts, i)):
            phan.downloadPicture(posts["url"][i], wallpaperFilepath)
            # Ask the user if they'd like to keep the wallpaper or pick a different one
            if phan.getUserInput("Keep Wallpaper"):
                # If the user wants to keep the wallpaper ask if they'd like to save it permanently
                if phan.getUserInput("Would you like to save the wallpaper permanently"):
                    # Save the wallpaper using the filepath specified in clientInfo.py
                    phan.saveWallpaper()
                # close the loop as a wallpaper has been chosen
                break

# Returns true if the user presses Y or y for an input prompt, False otherwise
def getUserInput(message: str):
    userChoice = input(message + " y/n: ")
    if(userChoice == 'y' or userChoice == 'Y'):
        return True
    return False

def main():
    # base url used for the reddit api
    base_url ='https://oauth.reddit.com'
    # headers needed to request data from api
    headers = getAPIData()
    # Connect to reddit api, if not throw an error
    if not connectToReddit(base_url, headers):
        print("Unable to Connect to reddit")
        return
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
    

if __name__ == "__main__":
    main()
