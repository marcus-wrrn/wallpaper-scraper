import requests
# Import required info for access to the reddit api
import clientInfo as botInfo
import postAnalysis as panl

def getAPIData():
    # url for reddit
    reddit_url = 'https://www.reddit.com/'
    # Required data to access API
    # Note that the user must use their own bot information, details for creating a bot is explained in the reddit api docs
    data = {'grant_type': 'password', 'username': botInfo.username, 'password': botInfo.password}
    auth = requests.auth.HTTPBasicAuth(botInfo.client_id, botInfo.secret)
    r = requests.post(reddit_url + 'api/v1/access_token',
                  data=data,
                  headers={'user-agent': botInfo.user_agent},
		          auth=auth).json()
    # Get Access token
    token = 'bearer ' + r['access_token']
    # Return all the header data for the api
    return {'Authorization': token, 'User-Agent': botInfo.user_agent}



def connectToReddit(base_url, headers):
    response = requests.get(base_url + '/api/v1/me', headers=headers)
    return response.status_code == 200

def changeWallpaper(wallpaperFilepath, posts, postCount):
    for i in range(postCount):
        if(posts["image"][i] and not posts["NSFW"][i]):
            panl.downloadPicture(posts["url"][i], wallpaperFilepath)
            # if getUserInput():
            #     break
            break


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
    subreddit = '/r/Art'
    # number of posts to be taken from the subreddit
    # the highest possible value is 200
    numOfPosts = 25
    # parameters for what sort of information the script will be requesting
    payload = {'limit': numOfPosts}
    posts, postNum = panl.getPostsFromReddit(subreddit, payload, headers, base_url)
    changeWallpaper("./wallpapers/wallpaper", posts, postNum)
    

if __name__ == "__main__":
    main()
