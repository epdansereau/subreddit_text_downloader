import praw
import requests
import json
from datetime import datetime
import time


### Replace values to connect to api (https://praw.readthedocs.io/en/latest/getting_started/authentication.html)
reddit = praw.Reddit(client_id="",
                     client_secret="",
                     user_agent="")
### 


def scrape_posts(subreddit, start_time = None, end_time = None, interval = 3600*6):
    '''With default args, downloads all posts from a subreddit'''
    error_wait_time = 1
    wait_time = 0.5
    retries = 10
    pushshift_max = 100
    all_posts = []
    if start_time is None:
        start_time = int(reddit.subreddit(subreddit).created_utc)
    if end_time is None:
        end_time = int(datetime.now().timestamp())

    with open(f'fetched_r_{subreddit}.json', 'w') as f:
        f.write("[")
        while start_time < end_time:
            end_interval = min(start_time + interval, end_time)
            url = f"https://api.pushshift.io/reddit/search/submission/?after={start_time}&before={end_interval}&subreddit={subreddit}&limit=1000&score=%3E0"
            r = requests.get(url)
            for i in range(retries):
                if r.status_code == 200:
                    break
                else:
                    print("ERROR", str(r.status_code))
                    time.sleep(1*(2**i))
                    r = requests.get(url)
            posts = json.loads(r.text)["data"]
            if len(posts) < pushshift_max:
                start_time += interval
            else:
                start_time = int(posts[-1]["created_utc"])
            for post in posts:
                json.dump(post, f)
                f.write(",\n")
            time.sleep(wait_time)
        # correcting end of file:
        f.seek(f.tell()-2)
        f.truncate()
        f.write("]")