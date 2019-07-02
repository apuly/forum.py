#! /usr/bin/python3

from Forum import Forums
from settings import username, password

def main():
    forum = Forums.forum("forum.openredstone.org")
    posts = forum.openPage('/forum-7.html')
    for post in posts:
        print(post)
    if forum.login(username, password):
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
    main()