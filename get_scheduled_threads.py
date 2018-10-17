import praw
import pdb
import argparse
import requests
import json
import re
import datetime
import time

API_URL = "http://localhost:8081/"

def getThreads(subreddit, fr, to, verbose):

    schedules = getSchedule(subreddit, verbose)

    reddit = praw.Reddit("tinyvices", user_agent="tinyvices.io")
    subreddit = reddit.subreddit(subreddit)

    for i, schedule in enumerate(schedules,1):
        if (verbose): print("Schedule #{}: title=[{}]".format(i, schedule['title']))

        friendlyTitle = re.sub('{.*}', '', schedule['title'])

        if (verbose): print("Searching on: {}".format(friendlyTitle))

        search = "(title:\"{}\" AND author:AutoModerator)".format(friendlyTitle, )

        posts = subreddit.search(search,sort='new', syntax='lucene', time_filter='month', limit=1)

        if (verbose):
            for submission in posts:
                print("-> {}".format(submission.title))
                storeThreadInfo(submission, verbose)

def getSchedule(subreddit, verbose):
    request = requests.get("{}/schedules?subreddit={}".format(API_URL, subreddit))

    schedules = json.loads(request.text)

    return schedules

def storeThreadInfo(submission, verbose):
    #TODO: API call

if __name__ == '__main__':
    ### Commandline argument handling ###
    # Moved this from below imports to MAIN test to allow importation of this module. Otherwise, throws error on null required fields (i.e. USER).
    parser = argparse.ArgumentParser(description="Scrapes comments for a reddit user. Currently limited to most recent 999 comments (limit imposed by reddit).")
    parser.add_argument('-s','--subreddit', type=str, help="Subreddit to get automoderator-schedule from.", required=True)
    parser.add_argument('-f','--fromDate', type=str, help="From date.", required=False)
    parser.add_argument('-t','--toDate', type=str, help="To date.", required=False)
    parser.add_argument('-v','--verbose', help="Enables verbose output.", action="store_true")

    args = parser.parse_args()
    _subreddit = args.subreddit
    _from = args.fromDate
    _to = args.toDate
    _verbose = args.verbose

    getThreads(_subreddit, _from, _to, _verbose)
