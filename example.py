#! /usr/bin/python3

from Forum import Forums
import argparse
import sys

def main(args):
    parser = argparse.ArgumentParser(description="example tool for showing off forum.py functionality")
    parser.add_argument("--user", "-u", help="username of forum account")
    parser.add_argument("--password", "-p", help="password of the forum account")
    parser.add_argument("--shitpost", help="post a worthless thread into a subforum", type=int)
    parser.add_argument("--search", "-s", help="searches for something on the forum")
    parser.add_argument("--theadlist", "-t", help="list the threads in a subforum", type=int)

    args = parser.parse_args(args)
    print(args)
    forum = Forums.forum("forum.openredstone.org")

    if args.user and args.password:
        if forum.login(args.user, args.password):
            print("login succesfull")
            if args.shitpost:
                if forum.createThread("this is a bot", "it will murder you if you don't watch out", args.shitpost):
                    print("shitpost should have been succesful")
        else:
            print("login failed")

    if args.theadlist:
        posts = forum.openPage(f"/forum-{args.theadlist}.html")
        for post in posts:
            print(post)


    if args.search:
        results = forum.search(args.search)
        for result in results:
            print(result)


if __name__ == "__main__":
    main(sys.argv[1:])