import praw
import pdb
import argparse
import yaml
import json
import re

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

    rule_defs_json = parseYamlToJson(page.content_md,verbose)
    storeRules(subreddit, rule_defs_json, verbose)

def parseYamlToJson(yaml_text,verbose=False):
    if verbose:
        print("parseYaml: enter \r\n")

    yaml_sections = [section.strip("\r\n")
        for section in re.split("^---", yaml_text, flags=re.MULTILINE)]

    rule_defs_json = []

    for section_num, section in enumerate(yaml_sections, 1):
        try:
            parsed = yaml.safe_load(section)
        except Exception as e:
            raise ValueError(
                "YAML parsing error in section %s: %s" % (section_num, e))

        # only keep the section if the parsed result is a dict (otherwise
        # it's generally just a comment)
        if isinstance(parsed, dict):
            rule_defs_json.append(json.dumps(parsed))

    if verbose:
        print("rule_defs_json ({} items): {}".format(len(rule_defs_json),rule_defs_json))

    if rule_defs_json:
        print("parseYaml: success")

    return rule_defs_json

def storeRules(subreddit, rule_defs_json, verbose=False):
    if verbose:
        print("storeRules: enter")

    success = False

    if verbose:
        for i, rule in enumerate(rule_defs_json,1):
            print("rule #{}:\n{}\n".format(i,rule))
        print("storeRules: attempting API call now")
        
    if success:
        print("storeRules: success")

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
