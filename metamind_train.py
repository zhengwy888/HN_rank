from metamind.api import ClassificationData, ClassificationModel, set_api_key
from story_teller import *
import os

set_api_key(os.environ.get('METAMIND_KEY'))

#print getPostBetweenScores((200,300), 1)
#print getContentWithLabel(1)

training_data = ClassificationData(private=True, data_type='text', name='hn_stories_2labels_800_samples')
#training_data = ClassificationData(id=184417)
labels = ('0To15', '150Plus')
samples = getContentWithLabel(400, labels)

training_data.add_samples(samples, input_type='text')
classifier = ClassificationModel(private=True, name='HN score predictor_2labels')
#classifier = ClassificationModel(id=27906)

classifier.fit(training_data)

randomPost = getRandomPost()
prediction = classifier.predict(randomPost['content'], input_type='text')
print randomPost['score']
print prediction[0]['label'], prediction[0]['confidence']
#print 'prediction of score %d is %s with confidence %f' %(randomPost['score'], prediction['label'], prediction['probability'])
