import sys
if sys.version_info < (3, 0):
    import cookielib as cookiejar
    import urllib2 as request
    import urllib as parse
else:
    import http.cookiejar as cookiejar
    from urllib import request, parse
from bs4 import BeautifulSoup
import re

#Forum object, created for mybb forum software.
class forum(object):
    def __init__(self, ip, ssl = False, port = None):
        self._ip = ip
        if ssl:                                             #If the server uses SSL, it automatically adjusts the URL to start with https
            self._protocal = "https"                        #If not the url starts with http
        else:
            self._protocal = "http"
        self._port = port
        cj = cookiejar.CookieJar()                     #Cookies. Used for logging into the server.
        self._cproc = request.HTTPCookieProcessor(cj)
        self._opener = request.build_opener(self._cproc)
        self._login = False

    @property                                       #Used to get the forum IP
    def ip(self):
        return self._ip

    #executes an http POST; returns http response
    def _open(self, url, data = {}):
        self.lastRequest = url
        if data == {}:
            p_data = None
        else:
            p_data = parse.urlencode(data).encode()
        return self._opener.open("{}://{}{}".format(self._protocal, self._ip, url), data = p_data)

    def openPage(self, url):                        #Opens a page, parses the content if the page is parsable. Return raw HTML if it's not.
        resp = self._open(url).read()
        if url.startswith("/forumdisplay.php"):     #URL that refers to a subforum
            return Parser.parseThreadList(resp)
        elif url.startswith("/showthread.php"):     #URL that refers to a thread
            return Parser.parseThreadPage(resp)
        else:
            return resp
    
    def respond(self, text, url = None):            #Posts comment on a thread, returns True if succesfull, returns False if it fails
        if not self._login:
            return 0;
        if url is None:
            url = self.lastRequest
        postData = self._getPostData(url)
        if not postData:
            return False
        html = self._open(postData[0])
        soup = BeautifulSoup(html, 'html.parser')
        inputs = soup.find("form", method="post", id="quick_reply_form").findAll("input", type="hidden")      #Gets the needed posting information
        data = {}
        for input in inputs:
            data[input.get("name")] = input.get("value")        #Parses the posting information into a dictionary
        data['message'] = text                                  #Adds the message to the post data
        self._open('/newreply.php', data = data)                #Posts the reply
        return True
    
    def newThread(self, subject, message, fid):
        if not self._login:
            return 0
        url = '/newthread.php?fid='+str(fid)
        postData = self._getPostData(url)
        if not postData:
            return False
        html = self._open(postData[0])
        soup = BeautifulSoup(html, 'html.parser')
        inputs = soup.find("form", method="post", id="quick_reply_form").findAll("input", type="hidden")      #Gets the needed posting information
        data = {}
        for input in inputs:
            data[input.get("name")] = input.get("value")
        data.update({
            "subject":subject,
            "message":message
        })
        self._open(url+'&processed=1', data = data)
        return True

    def moveThread(self, thread_id, target_subforum, method = 'move', redirect_expire=""):
        #if type('target_subforum') != int:
        #    data = {'tid': thread_id, 'my_post_key': self._postkey, 'modtype': 'thread', 'action': 'move'}
        #    resp = self._open('/moderation.php', data)
        postData = self._getPostData(thread_id)
        if not self._login or not postData:
            return 0
       
        data = {'tid': postData[1],
                'my_post_key': self._postkey,
                'moveto': target_subforum,
                'method': method, 'action': 'do_move',
                'submit': 'Move / Copy Thread',
                'redirect_expire': redirect_expire
                }
        resp = self._open('/moderation.php', data = data)
        
    def login(self, username, password, url = '/index.php'):    #Logs into the forum. Sets login and username if succesfull.
                                                                #Returns True if succesfull, returns False if unsuccesfull.

        DATA = {                                                #Sets the required data for logging in.
            "url": "{}://{}{}".format(self._protocal, self._ip, url),
            "action": "do_login",
            "submit": "Login",
            "quick_login": "1",
            "quick_username": username,                         #Sets username
            "quick_password": password                          #Sets password
            }

        resp = self._open('/member.php?action=login', DATA)     #Post data to login page
        txt = resp.read().decode(errors='ignore')
        if "member_login" in txt[-16:]:                         #If the return data refers to the login page, login was unsuccesfull
            return False
        else:                                                   #Otherwise login was successfull
            self._login = True                                  #Sets login state
            self.username = username                            #Sets username
            self._postkey = re.search(r'var my_post_key = "(\w+)";', txt).group(1)
            return True
        

    def search(self, params, searchUrl = "/search.php"):        #Searches the given string on the forums. Requires the search params.
        try:                                                    #sets searchResults if succesfull.
            self.resp = self._open(searchUrl, params)           #Tries to connect to the server. Raises NoPageFound error if failed
        except request.HTTPError:
            raise self.NoPageFound('Bad response status')
        #get URL from redirect
        soup = BeautifulSoup(self.resp.read(), 'html.parser')   #Loads html parser
        url = soup.find('a').get('href')                        #Gets the redirect link from the page. Raises NoRedirect error if not found.
        if url is None:
            raise self.NoRedirect('Redirect link not found.')
        #load search results
        try:
            self.resp = self._open('/{}'.format(url))           #Opens redirect link, raises NoPageFound error if failed.
        except request.HTTPError:
            raise self.NoPageFound('Bad responsen status')
        return Parser.parseSearchResults(self.resp.read())    #Sets searchResults with parsed information


    
    def genSearchParams(self, keywords):    #Generates the default search parameters.
        params = self._defaultParams        #Takes keywords as input, returns dictionary with parameters
        params['keywords'] = keywords
        return params

    def _getPostData(self, s):
        if type(s) is str:
            return (s, re.match("/showthread.php\?tid=(\d+)", s).group())
        elif type(s) is int:
            return ("/showthread.php?tid={}".format(s), s)
        else:
            raise TypeError 
            



    #Default search paramters, without the searchterm. Used in genSearchParams to generate parameters for search function
    _defaultParams = {'submit':      'Search',
                     'sortordr':    'desc',
                     'sortby':      'lastpost',
                     'showresults': 'threads',
                     'postthread':  '1',
                     'postdate':    '0',
                     'pddir':       '1',
                     'keywords': None,
                     'forum[]': '1',
                     'findthreadst': '1',
                     'action': 'do_search' }


    #Exception raised when http response does not have status 200
    class NoPageFound(Exception):
        def __init__(self, value):
            self.value = value
        def __str__(self):
            return repr(self.value)
    

    #Exception raised when there is no URL found on the redirect page. 
    class NoRedirect(Exception):
        def __init__(self, value):
            self.value = value
        def __str__(self):
            return repr(self.value)

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

class Parser():
        #Parses the html from the result page; returns named tuple of the results
    @staticmethod
    def parseSearchResults(html):
        results = []
        #tuple = namedtuple('searchResults', ['thread', 'forum', 'author', 'lastreplier', 'lastreplytime'])
        soup = BeautifulSoup(html, 'html.parser')
        rows = soup.findAll('tr', class_ = 'inline_row')
        for row in rows:
            lines = row.findAll('td')

            line = lines[2].find(class_ = ' subject_old')
            if line is None: line = lines[2].find('span', class_ = " subject_editable subject_old")
            title = Parser._parseHref(line)

            line = lines[2].find(class_ = 'author smalltext').find('a')
            author = Parser._parseHref(line)

            line = lines[3].find('a')
            forum_ = Parser._parseHref(line)

            line = lines[6].findAll('a')[-1]
            lastreplier = Parser._parseHref(line)

            lastreplytime = lines[6].find('span').getText().split()[:2]

            view_count = lines[5].getText()

            reply_count = lines[4].getText()

            results.append(ThreadList(forum_, title, author, reply_count, view_count, lastreplier, lastreplytime))
        return results
    
    @staticmethod
    def parseThreadList(html):
        results = []
        #tuple = namedtuple('searchResults', ['thread', 'forum', 'author', 'lastreplier', 'lastreplytime'])
        soup = BeautifulSoup(html, 'html.parser')
        forum_ = soup.find('div', class_ = 'navigation').find('span').getText()
        rows = soup.findAll('tr', class_ = 'inline_row')
        for row in rows:
            lines = row.findAll('td')
            
            line = lines[2].find('span', class_ = " subject_new")
            if line is None: line = lines[2].find('span', class_ = " subject_old")
            if line is None: line = lines[2].find('span', class_ = "subject_editable subject_new")
            if line is None: line = lines[2].find('span', class_ = "subject_editable subject_old")
            
            line = line.find('a')
            title = Parser._parseHref(line)

            line = lines[2].find(class_ = 'author smalltext').find('a')
            author = Parser._parseHref(line)

            line = lines[5].findAll('a')[-1]
            lastreplier = Parser._parseHref(line)

            lastreplytime = lines[5].find('span').getText().split()[:2]

            view_count = lines[4].getText()

            reply_count = lines[3].getText()

            results.append(ThreadList((forum_), title, author, reply_count, view_count, lastreplier, lastreplytime))
        return results

    @staticmethod
    def parseThreadPage(html):
        results = []
        soup = BeautifulSoup(html, 'html.parser')
        posts = soup.findAll('div', class_ = 'post ')
        for post in posts:

            line = post.find('div', class_ = 'author_information')
            poster = [line.findChild().getText()]
            poster.append(line.find('a').get('href'))

            time = post.find('span', class_ = 'post_date').getText().split('(')[0].strip()

            text = post.find('div', class_ = 'post_body scaleimages').getText().strip()

            signature = post.find('div', class_ = 'signature scaleimages')
            if signature:
                signature = signature.getText().strip()
            results.append(Post(poster, time, text, signature))
        return results
        

    #Parse html, returns tuple containing readable text and the URL
    @staticmethod
    def _parseHref(line):
        return (line.getText(), line.get('href'))
