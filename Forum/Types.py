
class Post(object):                 #Post object. Contains post data
    def __init__(self, poster, time, text, signature):
        self._poster = poster           #Name of the poster
        self._time = time               #The time of the post
        self._text = text               #The text in the post
        self._signature = signature     #The posters signature.
    @property
    def poster(self):
        return self._poster
    @property
    def signature(self):
        return self._signature
    @property
    def text(self):
        return self._text
    @property
    def time(self):
        return self._time 

class ThreadList(object):       #Threadlist object. Contains thread list information found in subforums
    def __init__(self, forum, title, author, reply_count, view_count, last_poster, last_post_time):
        self._title = title                 #The title of the thread
        self._author = author               #The maker of the thread
        self._forum = forum                 #The forum in which the thread was posted
        self._replc = reply_count           #The reply count
        self._viewc = view_count            #The view count
        self._lastpr = last_poster          #The name of the person that posted last
        self._lastpt = last_post_time       #The time at which the last reply was made
    @property
    def forum(self):
        return self._forum
    @property
    def title(self):
        return self._title
    @property
    def author(self):
        return self._author
    @property
    def reply_count(self):
        return self._replc
    @property
    def view_count(self):
        return self._viewc
    @property
    def last_replier(self):
        return self._lastpr
    @property
    def last_reply_time(self):
        return self._lastpt

    def __str__(self):
        return f"title: {self._title}, author: {self._author}"
