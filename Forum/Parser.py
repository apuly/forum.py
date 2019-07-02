from bs4 import BeautifulSoup
import re
from Forum.Types import Post, ThreadList

PARSER = 'html5lib'

class Parser():
    #Parses the html from the result page; returns named tuple of the results
    @staticmethod
    def parseSearchResults(html):
        results = []
        #tuple = namedtuple('searchResults', ['thread', 'forum', 'author', 'lastreplier', 'lastreplytime'])
        soup = BeautifulSoup(html, features = PARSER)
        rows = soup.findAll('tr', class_ = 'inline_row')
        for row in rows:
            lines = row.findAll('td')

            line = lines[2].find("a")
            title = Parser._parseHref(line)

            line = lines[2].find("div", class_ = "author smalltext").find("a")
            author = Parser._parseHref(line)

            line = lines[3].find('a')
            forum_ = Parser._parseHref(line)

            reply_count = lines[4].getText()
            view_count = lines[5].getText()

            results.append(ThreadList(forum_, title, author, reply_count, view_count, (None), (None)))
        return results

    @staticmethod
    def parseThreadList(html):
        results = []
        #tuple = namedtuple('searchResults', ['thread', 'forum', 'author', 'lastreplier', 'lastreplytime'])
        decoded = html.decode()
        with open("html.txt", 'w' ) as f:
            f.write(decoded)

        soup = BeautifulSoup(decoded, features = PARSER)
        forum_ = soup.find('div', class_ = 'navigation').find('span').getText()
        rows = soup.findAll('tr', class_ = 'inline_row')
        for row in rows:
            lines = row.findAll('td')
            line = lines[2].find("span", class_ = re.compile(r"(\w+ )?subject_\w+"))
           
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
        soup = BeautifulSoup(html, PARSER)
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
            else:
                signature = ""
            results.append(Post(poster, time, text, signature))
        return results
        

    #Parse html, returns tuple containing readable text and the URL
    @staticmethod
    def _parseHref(line):
        return (line.getText(), line.get('href'))