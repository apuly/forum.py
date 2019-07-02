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

from Forum.Parser import PARSER, Parser

#Forum object, created for mybb forum software.
class forum(object):
    def __init__(self, ip, ssl = True, port = None):
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
    def _open(self, url, data = None):
        if data is not None:
            data = parse.urlencode(data).encode()
        try:
            return self._opener.open("{}://{}{}".format(self._protocal, self._ip, url), data = data)
        except:
            pass
            #print(E.fp.read())
    
    def openPage(self, url):                        #Opens a page, parses the content if the page is parsable. Return raw HTML if it's not.
        """
        opens a forum page and parses the returning html
        url is the url to a forum page
        """
        resp = self._open(url).read()
        if re.match(r"\/forum-\d+.html", url):          #URL that refers to a subforum
            return Parser.parseThreadList(resp)
        elif re.match(r"\/thread-\d+.html", url):       #URL that refers to a thread
            return Parser.parseThreadList(resp)
        elif url.startswith("search.php") and "action=results" in url:
            Parser.parseSearchResults(resp)
        else:
            return resp
    
    def respond(self, text, url = None):            #Posts comment on a thread, returns True if succesfull, returns False if it fails
        """
        replies to an existing thread
        text will be the content of the message
        url is the url or id of the thread that is being replied to
        """
        if not self._login:
            raise self.NoLogin
        postData = self._getPostData(url)
        html = self._open(postData[0])
        soup = BeautifulSoup(html, features = PARSER)
        inputs = soup.find("form", method="post", id="quick_reply_form").findAll("input", type="hidden")      #Gets the needed posting information
        data = {}
        for input in inputs:
            data[input.get("name")] = input.get("value")        #Parses the posting information into a dictionary
        data['message'] = text                                  #Adds the message to the post data
        self._open('/newreply.php', data = data)                #Posts the reply
        return True

    def moveThread(self, thread_id, target_subforum, method = 'move', redirect_expire=""):
        """
        method for moving threads
        thread_id is the id of the thread
        target_subforum is the subforum that the thread must be moved to
        method is what moderation method will be executed, move by default. Other methods might require move data that can't be passed to the function
        redirect_expire is the time that a redirect will fuction (don't know what its for, but needs to be empty to properly move threads)
        """
        if not self._login:
            raise self.NoLogin
        else:
            postData = self._getPostData(thread_id)
        
            data = {'tid': postData[1], #build dict with data needed to move thread
                    'my_post_key': self._postkey,
                    'moveto': target_subforum,
                    'method': method, 'action': 'do_move',
                    'submit': 'Move / Copy Thread',
                    'redirect_expire': redirect_expire
                    }
            self._open('/moderation.php', data = data)
        
    def createThread(self, subject, text, url, **argv):
        """
        function for creating new thread
        subject is string that becomes thread subject
        text is string that becomes the message of the first post
        url is either url or id of subforum that will be posted to
        argv contains any settings for the post that you want to override
        (argv could possibly also be used to add attachements, though this is untested)
        """
        if not self._login:
            raise self.NoLogin
        forumData = self._getForumData(url)
        create_url = "/newthread.php?fid={}".format(forumData[1]) #build url that is posted
        
        # collect information for succesfully posting thread
        html = self._open(create_url)
        soup = BeautifulSoup(html, PARSER)
        inputs = soup.findAll("form", method="post")[1].findAll("input", type="hidden")
        
        # parse posting information into a dictionary
        data = {
            "subject": subject,
            "message": text
        }        
        for input in inputs:
            data[input.get("name")] = input.get("value")
        merge_two_dicts(data, argv)

        self._open("{}&processed=1".format(create_url), data = data)
        return True
    

    
    def login(self, username, password, url = '/index.php'):    #Logs into the forum. Sets login and username if succesfull.
        """
        logs user into a forum account
        lets login and username if succesful
        Returns True if succesfull, returns False if unsuccesfull.
        """
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
        

    def search(self, params, searchUrl = "/search.php"): 
        """
        Searches the given string on the forums. Requires the search params
        Returns search result as array of ThreadList if succesful
        """
        if isinstance(params, str): #allow simple searching of stuff
            params = self.genSearchParams(params)

        try:                                                    
            self.resp = self._open(searchUrl, params)           #Tries to connect to the server. Raises NoPageFound error if failed
        except request.HTTPError:
            raise self.NoPageFound('Bad response status')
        #get URL from redirect
        soup = BeautifulSoup(self.resp.read(), PARSER)   #Loads html parser
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
        #Default search paramters, without the searchterm. Used in genSearchParams to generate parameters for search function
        params = {
            'submit':      'Search',
            'sortordr':    'desc',
            'sortby':      'lastpost',
            'showresults': 'threads',
            'postthread':  '1',
            'postdate':    '0',
            'pddir':       '1',
            'keywords': None,
            'forum[]': '1',
            'findthreadst': '1',
            'action': 'do_search'
        }
        
        params['keywords'] = keywords
        return params

    def _getPostData(self, s):
        """
        creates common interface for forum links based on either a url or thread data
        s is either url to a thread or the id of a thread
        """
        if isinstance(s, str):
            return (s, re.match(r"\/thread-(\d+)(\D.+)?", s).group(1))
        elif isinstance(s, int):
            return ("/thread-{}".format(s), s)
        else:
            raise TypeError 

    def _getForumData(self, s):
        """
        creates common interface for forum links based on either a url or thread data
        s is either url to a subforum or the id of a subforum
        """
        if type(s) is str:
            return (s, re.match(r"\/forum-(\d+)(\D.+)?", s).group(1))
        elif type(s) is int:
            return ("/forum-{}".format(s))
        else:
            raise TypeError


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

    #Exception raised when certain method requires login and bot is not succesfully logged in
    class NoLogin(Exception):
        pass

def merge_two_dicts(x, y):
    """
    method for merging two dictionaries
    used for compatiblity with python 2.7, because that's still a thing apparently
    """
    z = x.copy()   # start with x's keys and values
    z.update(y)    # modifies z with y's keys and values & returns None
    return z