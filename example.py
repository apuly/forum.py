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
    parser.add_argument("--reply", "-r", help="post a reply to thread", type=int)
    parser.add_argument("--readthread", help="open a tread and print the replies", type=int)

    args = parser.parse_args(args)
    print(args)
    forum = Forums.forum("forum.openredstone.org")

    if args.user and args.password:
        if forum.login(args.user, args.password):
            print("login succesfull")
        else:
            print("login failed")

    if args.shitpost:
        if forum.createThread("this is a bot", "it will murder you if you don't watch out", args.shitpost):
            print("shitpost should have been succesful")

    if args.reply:
        if forum.respond("all bots are evil and must be removed from the internet", args.reply):
            print("reply should have been made succesfully")

    if args.theadlist:
        threads = forum.openPage(f"/forum-{args.theadlist}.html")
        for thread in threads:
            print(thread)

    if args.readthread:
        posts = forum.openPage(f"/thread-{args.readthread}.html")
        for post in posts:
            print("{}: {}".format(post.poster, post.text))


    if args.search:
        results = forum.search(args.search)
        for result in results:
            print(result)


if __name__ == "__main__":
    main(sys.argv[1:])