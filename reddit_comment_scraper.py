from urllib2 import Request, urlopen
from time import sleep
import json
import argparse
import praw
import pdb
from datetime import datetime

### Global Variables ###
_headers = {"User-agent" : "reddit_comment_fetcher by /u/shaggorama"} # not sure if I need this
_host = 'http://www.reddit.com'

def get_comments(URL,head,delay=2):
    '''Pretty generic call to urllib2.'''
    sleep(delay) # ensure we don't GET too frequently or the API will block us
    request = Request(URL, headers=head)
    try:
        response = urlopen(request)
        encoding = response.headers.get_content_charset()
        #data = response.read()
        data = json.loads(response.read().decode(encoding))
    except:
        sleep(delay+5)
        response = urlopen(request)
        encoding = response.headers.get_content_charset()
        #data = response.read()
        data = json.loads(response.read().decode(encoding))
    return data

def search_reddit(search, verbose=False, user=None):
    r = praw.Reddit("tinyvices", user_agent="tinyvices.io")
    # params = {"q": search}
    # if after:
        # params["after"] = "t3_" + str(after.id)

    fini = praw.models.Subreddit(r,display_name='financialindependence')
    posts = fini.search(search,limit=None)

    # search = "daily discussion"
    if user!=None:
        for comment in r.redditor(user).comments.new(limit=None):
            pdb.set_trace()
            print(comment.body.split('\n', 1)[0][:79])

    # pdb.set_trace()
    cnt=0

    for submission in posts:
      if verbose:
          print(submission.title)
      cnt+=1

    print(cnt)

def parse_json(json_data):
    '''Simple parser for getting reddit comments from JSON output. Returns tuple of JSON comments and list of IDs'''
    try:
        #pdb.set_trace()
        decoded = json_data #json.JSONDecoder().decode(json_data)
        comments = [x['data'] for x in decoded['data']['children'] ]
        ids = [comments[i]['name'] for i in range(len(comments))]
    except:
        return [], []
    return comments, ids

def threadscrape(post_id, limit=0, pause=2):
    #pdb.set_trace()

    items = []
    pageurl = _host + '/r/financialindependence/comments/' + post_id + '/.json'
    while true:
        try:
            data = get_comments(pageurl, _headers, pause)
            newitems, newids = parse_json(data)
        except:
          print("problem!")
        if newitems == []:
            print("reached limit of available comments")
            break
        try:
            for i, id in enumerate(newids):
                if id in item_ids:
                    print("page is returning comments we've already seen. ending scrape.")
                    break
                else:
                    items.append(newitems[i])
                    item_ids.append(id)
        except:
            items, item_ids = newitems, newids
        print("downloaded %d comments. oldest comment: %d \n" % (len(items), items[-1]['created']))
        if limit > 0 and len(item_ids) >= limit:
            print("exceeded download limit set by paramter 'limit'.")
            items = items[0:limit]
            break
    pdb.set_trace()
    return items


# Probably should store comments as we get them. For now, let's just download them all and dump them into the DB all at once.
def scrape(targetUser, limit=0, pause=2): #, db='redditComments.db', storage='db'):
    items = []
    userpageURL = _host + '/user/' + targetUser + '/comments/.json'
    nPages=0
    stop = False
#    tbl_comments = ConnectToDBCommentsTable(db)
    while not stop: # or len(items)<=50: # Need to figure out how to get past the 999 comments limit.
        if nPages > 0:
            last = items[-1]['name']
            paginationSuffix = '?count='+str(nPages*25)+'&after='+last #+'.json'
            print(userpageURL + paginationSuffix)
        try:
            data = get_comments(userpageURL + paginationSuffix, _headers, pause)
        except:
            data = get_comments(userpageURL, _headers, pause)
        newItems, newIDs = parse_json(data)
        if newItems == []:
            print("Reached limit of available comments")
            stop = True # this is redundant
            break
        try:
            for i, id in enumerate(newIDs):
                if id in item_ids:
                    print("Page is returning comments we've already seen. Ending scrape.")
                    stop = True
                    break
                else:
                    items.append(newItems[i])
                    item_ids.append(id)
        except:
            items, item_ids = newItems, newIDs
        nPages += 1
        print("Downloaded %d pages, %d comments. Oldest comment: %d \n" % (nPages, len(items), items[-1]['created']))
        if limit > 0 and len(item_ids) >= limit:
            print("Exceeded download limit set by paramter 'limit'.")
            items = items[0:limit]
            stop = True #redundant with 'break' command
            break
    #pdb.set_trace()
    return items

def storecomments(comments, session):
  for c in comments:
    session.add(CommentsClass(c))
    if c.replies != None:
      storecomments(c.replies, session)

def getcomments(thread_id = '4q2sol'):
  r = praw.Reddit("dailyfi thread scrape")

  thread = r.get_submission(submission_id=thread_id)

  #pdb.set_trace()
  print("\nThread has " + str(thread.num_comments) + " comments")
  print("Replacing MoreComments...")

  thread.replace_more_comments(limit=None, threshold=0)
  comments = praw.helpers.flatten_tree(thread.comments)

  assert thread.num_comments == len(comments)

if __name__ == '__main__':
    ### Commandline argument handling ###
    # Moved this from below imports to MAIN test to allow importation of this module. Otherwise, throws error on null required fields (i.e. USER).
    parser = argparse.ArgumentParser(description="Scrapes comments for a reddit user. Currently limited to most recent 999 comments (limit imposed by reddit).")
    parser.add_argument('-u','--user', type=str, help="Reddit username to grab comments from.", required=False)
    parser.add_argument('-l','--limit', type=int, help="Maximum number of comments to download.", default=0)
    parser.add_argument('-d','--dbname', type=str, help="Database name for storage.", default='RedditComments.DB')
    parser.add_argument('-w','--wait', type=int,help="Wait time between GET requests. Reddit documentation requests a limit of 1 of every 2 seconds not to exceed 30 per min.", default=2)
    parser.add_argument('-c','--csv', type=str, help="CSV name if you want CSV output instead of database.", default=None)
    parser.add_argument('-s','--search', type=str, help="Search reddit for a string.", required=True)
    parser.add_argument('-t','--thread', help="Store comments from list of threads.", action="store_true")
    parser.add_argument('-p','--pickle', help="Pickle threads from dailythreads table.", action="store_true")
    parser.add_argument('-g','--graph', help="Pickle threads from dailythreads table.", action="store_true")
    parser.add_argument('-v','--verbose', help="Enables verbose output for some commands.", action="store_true")

    args = parser.parse_args()
    _user   = args.user
    _limit  = args.limit
    _dbname = args.dbname
    _wait   = args.wait
    _csv    = args.csv
    _search = args.search
    _thread = args.thread
    _pickle = args.pickle
    _graph = args.graph
    _verbose = args.verbose

    if _search:
      #addthreadbypostid('4q2sol')
      # loadsubmissions()
      # while true:
        # with open("threads/4q2sol.pickle", "rb") as handle:
          # thread = pickle.load(handle)

        # pdb.set_trace()
      search_reddit(_search, _verbose, _user)
    elif _thread:
      getthreadcomments()
    else:
      comments = scrape(_user, _limit, _wait)
      print("Total Comments Downloaded:", len(comments))
      # to pretty print results:
      #for i in comments: print json.dumps(i, indent=2)
