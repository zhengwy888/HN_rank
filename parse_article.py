import psycopg2
import codecs
import psycopg2.extras
import time
import urllib2
from urllib2 import urlopen
from urlparse import urlparse
from bs4 import BeautifulSoup
import threading
import os
from readability.readability import Document

#rdClient = ParserClient('4de0345b55435bfc5642ebf6b518422383c127bb')
dbConn = psycopg2.connect(os.environ.get('PSQL_CONNECTION'))
dbConn.autocommit = True

opener = urllib2.build_opener()
opener.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11')]
urllib2.install_opener(opener)
'''
CREATE TABLE story_contents (
    id int REFERENCES story (id),
    author varchar(256),
    excerpt text,
    word_count int,
    content text
);
'''

def getPost(idx):
    cursor = dbConn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    #cursor = dbConn.cursor()
    cursor.execute("SELECT * FROM story WHERE id=%s", [idx])
    post = cursor.fetchone()
    return post

def parseURL_py(url):
    html = urlopen(url).read()    
    soup = BeautifulSoup(html)
# kill all script and style elements
    for script in soup(["script", "style"]):
        script.extract()    # rip it out
    text = soup.get_text()  
# break into lines and remove leading and trailing space on each
    lines = (line.strip() for line in text.splitlines())
# break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
# drop blank lines
    raw = u'\n'.join(chunk for chunk in chunks if chunk)
    return raw

# readability python
def parseURL_pr(url):
    parsed = urlparse(url)
    if ( "youtube" in parsed.hostname ):
        print url, 'has youtube and we dont parse that'
        return None
    try:
        response = urlopen(url)
    except IOError:
        return None

    if ( response.getcode() > 400 ):
        print url , ' is not accessible any more', response.getcode()
        return None
    html = response.read()
    doc = Document(html)
    content = {}
    #content['content'] = doc.summary()
    html = doc.summary(True)
    soup = BeautifulSoup(html)
    content['content'] = soup.get_text()
    content['title'] = doc.title()
    content['word_count'] = len(content['content'])
    return content


# readability
'''
def parseURL_RD(url):
    parsed = urlparse(url)
    if ( "youtube" in parsed.hostname ):
        return None
    parser_response = rdClient.get_article_content(url)
    if ( 'content' not in parser_response.content ) :
        print parser_response
        print url, " has some trouble being parsed"
        return None
    soup = BeautifulSoup(parser_response.content['content'])
    parser_response.content['content'] = soup.get_text()
    return parser_response.content
'''

def saveContent(id, data):
    #usedField = ['id', 'author', 'excerpt', 'content', 'word_count']
    usedField = ['id', 'content', 'word_count']
    cur = dbConn.cursor()
    data['id'] = id
    cur.execute("INSERT INTO story_contents (" + ','.join(usedField) + ") VALUES (%(id)s, %(content)s, %(word_count)s)", data)

def getContent(id):
    cur = dbConn.cursor()
    cur.execute("SELECT * FROM story_contents WHERE id=%s", (id,))
    return cur.fetchone()

def parseContentChunk(idchunk):
    print "worker started for range " , idchunk[0], idchunk[len(idchunk)-1]
    for idx in idchunk:
        if ( getContent(idx) is not None ):
            continue
        post = getPost(idx)
        if ( post is None):
            continue
        if ( post['score'] <= 100 ):
            continue
        print 'parsing %d: %s (%d)' %(post['id'], post['title'], post['score'])
        data = parseURL_pr(post['url'])
        if ( data is None ):
            continue
        saveContent(idx, data)

def parseContentThreaded(lower, higher, chunk_size):
    threads = []
    # I don't care the top range, we can get a couple more
    chunks = [ range(lower+i*chunk_size, lower+chunk_size*(i+1)) for i in xrange(0, (higher-lower+chunk_size-1)/chunk_size)]
    for chunk in chunks:
        t = threading.Thread(
                target = parseContentChunk,
                args=(chunk,)
        )
        threads.append(t)
        t.start()

    while threading.active_count() > 0:
        time.sleep(1)

    print "done!"
    return


#post = getPost(9492110)
##post = getPost(7489328)
#content = parseURL_pr(post['url'])
#content = parseURL_pr('http://www.coindesk.com/kim-dotcom-launches-political-party-proposes-national-cryptocurrency/')
##content = parseURL_pr('http://www.google.com')
#print content
#saveContent(9492110, content)
#parseContentThreaded(7489373, 7489473, 10)
# 2015/05/09
#parseContentThreaded(7489373, 7499473, 1000)
# 2015/05/10
#parseContentThreaded(7500000, 8000000, 10000)
# more than 15 is what I need
#parseContentThreaded(8000000, 8400000, 10000)
#parseContentThreaded(8400000, 8500000, 10000)
#parseContentThreaded(8500000, 8700000, 10000)
parseContentThreaded(8700000, 9000000, 10000)
