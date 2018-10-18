import praw
import pdb
import argparse
import requests

API_URL = "http://localhost:8081/"

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
