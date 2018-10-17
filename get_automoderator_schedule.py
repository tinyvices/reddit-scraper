import praw
import pdb
import argparse
import yaml
import json
import re
import requests

API_URL = "http://localhost:8081/"

def getSchedule(subreddit, verbose):
    if verbose:
        print("getSchedule: subreddit=[{}]".format(subreddit))

    r = praw.Reddit("tinyvices", user_agent="tinyvices.io")
    fini = praw.models.Subreddit(r,display_name=subreddit)

    page = praw.models.WikiPage(r, fini, "automoderator-schedule")

    if verbose:
        #pdb.set_trace()
        print(page.content_md)

    if page:
        print("getSchedule: success")

    rules = parseYamlToJson(page.content_md,verbose)

    for rule in rules:
        storeRule(subreddit, rule, verbose)

def parseYamlToJson(yaml_text,verbose=False):
    if verbose:
        print("parseYaml: enter \r\n")

    yaml_sections = [section.strip("\r\n")
        for section in re.split("^---", yaml_text, flags=re.MULTILINE)]

    rules = []

    for section_num, section in enumerate(yaml_sections, 1):
        try:
            parsed = yaml.safe_load(section)
        except Exception as e:
            raise ValueError(
                "YAML parsing error in section %s: %s" % (section_num, e))

        # only keep the section if the parsed result is a dict (otherwise
        # it's generally just a comment)
        if isinstance(parsed, dict):
            rules.append(parsed)

    if verbose:
        print("rules ({} items): {}".format(len(rules),rules))

    if rules:
        print("parseYaml: success")

    return rules

def storeRule(subreddit, rule, verbose=False):
    if verbose:
        print("storeRule: enter")

    if verbose:
        print("rule:\n{}".format(rule))
        print("storeRule: attempting API call now")


    headers = {'Content-type': 'application/json'}
    response = requests.post("{}/schedules".format(API_URL), data = json.dumps(rule), headers = headers)

    if response.status_code==200:
        print("storeRule: success")
    else:
        print("storeRule: code:{}".format(response.status_code))

if __name__ == '__main__':
    ### Commandline argument handling ###
    # Moved this from below imports to MAIN test to allow importation of this module. Otherwise, throws error on null required fields (i.e. USER).
    parser = argparse.ArgumentParser(description="Scrapes comments for a reddit user. Currently limited to most recent 999 comments (limit imposed by reddit).")
    parser.add_argument('-s','--subreddit', type=str, help="Subreddit to get automoderator-schedule from.", required=True)
    parser.add_argument('-v','--verbose', help="Enables verbose output.", action="store_true")

    args = parser.parse_args()
    _subreddit = args.subreddit
    _verbose = args.verbose

    if _subreddit:
        getSchedule(_subreddit, _verbose)
