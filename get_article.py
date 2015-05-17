from firebase import firebase
from time import sleep
import math
import psycopg2
import psycopg2.extras
import threading
import os

MAX_RETRIES = 5

dbConn = psycopg2.connect(os.environ.get('PSQL_CONNECTION'))
dbConn.autocommit = True

hnClient = firebase.FirebaseApplication(
        'https://hacker-news.firebaseio.com',
        authentication=None
        )

def getHNPost(postId):
    result = None
    t = 1
    while(not result and t < MAX_RETRIES):
        try:
            result = hnClient.get('/v0/item/%s' % postId, None)
        except:
            ++t
            sleep(5)
            continue
    return result

def getTopStories(limit=20):
    result = None
    t = 1
    while(not result and t < MAX_RETRIES):
        try:
            result = hnClient.get('/v0/topstories', None)
        except:
            ++t
            sleep(5)
            continue
    return result

def isPostStory(post):
    if ( 'deleted' in post ):
        return False
    if ( post['type'] != "story" ):
        return False
    if ( 'url' not in post or post['url'] == '' ) :
        return False
    return True


def saveHNStories(idchunks):
    print "worker started for range " , idchunks[0], idchunks[len(idchunks)-1]
    for id in idchunks:
        if ( getPost(id) is not None) :
            continue
        post = getHNPost(id)
        if (isPostStory(post) is False):
            continue
        else:
            savePost(post)

def saveHNRanges(lower, higher, chunk_size):
    threads = []
    # I don't care the top range, we can get a couple more
    chunks = [ range(lower+i*chunk_size, lower+chunk_size*(i+1)) for i in xrange(0, (higher-lower+chunk_size-1)/chunk_size)]
    for chunk in chunks:
        t = threading.Thread(
                target = saveHNStories,
                args=(chunk,)
        )
        threads.append(t)
        t.start()

    # bad pattern, it became a long live thread
    #for t in threads:
    #    t.join()
    while threading.active_count() > 0:
        sleep(1)

    print "done!"
    return

'''
CREATE TABLE story (
    id integer NOT NULL PRIMARY KEY,
    title text,
    url text,
    by character varying(64) NOT NULL,
    score integer,
    "time" integer,
    type character varying(16),
    kids text
);
'''
def savePost(post):
    cur = dbConn.cursor()
    print "saving %d:%s" %(post['id'], post['title'])
    usedField = ["id", 'title', 'url', 'by', 'score', 'time', 'type']
    middle = [post[field] for field in usedField]
    cur.execute("INSERT INTO story (" + ','.join(usedField) + ") VALUES (" + ','.join(['%s' for _ in usedField]) + ")",
            (middle))

def getPost(idx):
    cursor = dbConn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute("SELECT * FROM story WHERE id=%s", [idx])
    post = cursor.fetchone()
    return post
# 9492110 : 2015/05/05
# 8489273: Tue, 21 Oct 2014 19:24:20 GMT
# 7489273: Fri, 28 Mar 2014 19:03:37 GMT
#samplePost = getHNPost(9492110)
#saveHNStories([9492110, 8489273])
#saveHNRanges(7489273, 7489373, 10)
#saveHNRanges(7489373, 8489273, 10000)
saveHNRanges(8500000, 9500000, 10000)
#savePost(samplePost)
