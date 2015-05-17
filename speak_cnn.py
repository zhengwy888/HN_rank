from story_teller import *
import string
import codecs
import random

# use the same file name as the rcv1 to minimize my modification
datafile =  'rcv1-1m-train.txt.tok'
datalabel = 'rcv1-1m-train.lvl2'
dictfile =  'rcv1-lvl2.catdic'
testfile =  'rcv1-1m-test.txt.tok'
testlabel = 'rcv1-1m-test.lvl2'

def speakFile(datacontainer, dataTarget, labelTarget):
    sequence = range(len(datacontainer['data']))
    random.shuffle(sequence)
    dfile = codecs.open(dataTarget, "w", "utf-8")
    lfile = codecs.open(labelTarget, 'w', 'utf-8')
    for idx in sequence:
        content = removeNewlines(datacontainer['data'][idx])
        label = datacontainer['targets'][idx]
        dfile.write(content+"\n")
        lfile.write(label+"\n")
    dfile.close()
    lfile.close()

remove_punctuation_map = dict((ord(char), None) for char in string.punctuation)
def removeNewlines(content):
# remove new lines, ^M, punctuation, {}, all that jazz
# going to ascii to get more punc removal
    cleaned = content.translate(remove_punctuation_map)
    asci = cleaned.encode("ascii", "ignore")
    altered = " ".join([k.strip() for k in asci.split('\n')]);
    return altered.decode("utf-8")

# start with 100 and 10, we will increase the size at the end
sLabels = ('0To15', '150Plus');
training_data = trainingData(2000, sLabels)
test_data = testingData(200, sLabels)

speakFile(training_data, datafile, datalabel)
speakFile(test_data, testfile, testlabel)

labelFH = codecs.open(dictfile, "w", 'utf-8')
for l in sLabels:
    labelFH.write(l+"\n")
labelFH.close()
