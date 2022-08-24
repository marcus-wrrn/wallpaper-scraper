from ast import arg
import sys
import requests
# Import required info for access to the reddit api
import clientInfo as ci
import postHandling as phan

roulleteMode = False

def getUserArgs():
    subreddit = "/r/wallpaper"
    postCount = 25
    # Check command line
    argCount = len(sys.argv)
    if argCount >= 2:
        subreddit = "/r/" + sys.argv[1]
    return subreddit




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

def validatePost(posts, i):
    if (roulleteMode and posts["image"][i]):
        return True
    if (not roulleteMode and posts["image"][i] and not posts["NSFW"][i]):
        return True
    return False

def changeWallpaper(wallpaperFilepath, posts, postCount):
    for i in range(postCount):
        if(validatePost(posts, i)):
            phan.downloadPicture(posts["url"][i], wallpaperFilepath)
            if phan.getUserInput("Keep Wallpaper"):
                if phan.getUserInput("Would you like to save the wallpaper permanently"):
                    phan.saveWallpaper()
                break

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
    payload = {'limit': 200}
    posts, postNum = phan.getPostsFromReddit(subreddit, payload, headers, base_url)
    changeWallpaper(ci.wallpaperFilepath, posts, postNum)
    

if __name__ == "__main__":
    main()
