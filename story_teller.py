# the general class function for accessing stories, all data munging go here
import psycopg2
import psycopg2.extras
import os

dbConn = psycopg2.connect(os.environ.get('PSQL_CONNECTION'))
# took me 30 min to dig up these 2 lines. python documentation is good?
# http://initd.org/psycopg/docs/usage.html#unicode-handling
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)
psycopg2.extensions.register_type(psycopg2.extensions.UNICODEARRAY)

'''
0 (goblin) -> 0 - 15

1 (orc) -> 16 - 40

2 (troll) -> 41 - 80

3 (nazgul) -> 81 - 150

4 (sauron) -> 150+
'''
labels = ['0To15', '16To40', '41To80', '81To150', '150Plus']
# some really large number to avoid coding complication
labelBins = [(0, 15), (16,40), (41,80), (81,150), (150, 9223372036854775807)]

def getCategories():
    return labels;

# training data are fetched from the head, up to 600
# testing data fetched from the tail, up to 200
# validation data fetched from tail, offseted with 200
# given total sample size of 1000+, we should never have collision
# wordcount > 100 seems to only filter out less than 10% of samples,
# leave it on for now as we might get overfit?
def trainingData(countPerLabel = 100, selectedLabels=None):
    data = {}
    data['data'] = []
    data['targets'] = []
    if ( selectedLabels is None ):
        selectedLabels = getCategories()
    for idx in xrange(len(labels)):
        if ( labels[idx] not in selectedLabels ):
            continue
        scoreRange = labelBins[idx]
        label = labels[idx]
        posts = getPostBetweenScores(scoreRange, countPerLabel, 'asc')
        data['data'] += [post['content'] for post in posts]
        data['targets'] += [label for _ in xrange(len(posts))]
    return data

def testingData(countPerLabel = 30, selectedLabels=None):
    data = {}
    data['data'] = []
    data['targets'] = []
    if ( selectedLabels is None ):
        selectedLabels = getCategories()
    for idx in xrange(len(labels)):
        if ( labels[idx] not in selectedLabels ):
            continue
        scoreRange = labelBins[idx]
        label = labels[idx]
        posts = getPostBetweenScores(scoreRange, countPerLabel, 'DESC')
        data['data'] += [post['content'] for post in posts]
        data['targets'] += [label for _ in xrange(len(posts))]
    return data

def validationData(countPerLabel = 30):
    data = {}
    data['data'] = []
    data['targets'] = []
    for idx in xrange(len(labels)):
        scoreRange = labelBins[idx]
        label = labels[idx]
        posts = getPostBetweenScores(scoreRange, countPerLabel, 'DESC', 200)
        data['data'] += [post['content'] for post in posts]
        data['targets'] += [label for _ in xrange(len(posts))]
    return data

def getPostBetweenScores(scoreRange, limit, order = "DESC", offset = 0):
    cursor = dbConn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute("SELECT * from story_contents sc JOIN story s ON s.id = sc.id WHERE s.score BETWEEN %s and %s AND sc.word_count > 50 " 
            + " ORDER BY s.id %s LIMIT %s OFFSET %s" % (order, limit, offset), (scoreRange[0], scoreRange[1]))
    return cursor.fetchall()

def getRandomPost():
    cursor = dbConn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute("SELECT * from story_contents sc JOIN story s ON s.id = sc.id WHERE sc.word_count > 50 ORDER BY random() LIMIT 1")
    return cursor.fetchone()

def getContentWithLabel(countPerLabel = 10, selectedLabels = None):
    samples = []
    if ( selectedLabels is None ):
        selectedLabels = getCategories()
    for idx in xrange(len(labels)):
        if ( labels[idx] not in selectedLabels ):
            continue
        scoreRange = labelBins[idx]
        label = labels[idx]
        posts = getPostBetweenScores(scoreRange, countPerLabel,'DESC')
        samples += [(post['content'], label) for post in posts]
    return samples
