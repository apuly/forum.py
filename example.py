#! /usr/bin/python3

from Forum import Forums
import argparse
import sys

def main(args):
    parser = argparse.ArgumentParser(description="example tool for showing off forum.py functionality")
    parser.add_argument("--user", "-u", help="username of forum account")
    parser.add_argument("--password", "-p", help="password of the forum account")

    args = parser.parse_args(args)

    forum = Forums.forum("forum.openredstone.org")
    posts = forum.openPage('/forum-7.html')
    for post in posts:
        print(post)
    if args.user and args.password:
        if forum.login(args.username, args.password):
            print("login succesfull")
            #shitpost(forum) #uncomment to shitpost
        else:
            print("login failed")
    results = forum.search("apuly")
    for result in results:
        print(result)

def shitpost(forum):
    if forum.createThread("this is a bot", "this subforum is pretty useless so I'm just abusing the shit out of it", "/forum-92"):
        print("creation should have been succesful")

if __name__ == "__main__":
    main(sys.argv[1:])