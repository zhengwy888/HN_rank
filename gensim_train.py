import gensim, logging
from gensim.models import Word2Vec
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

# does not load
model = Word2Vec.load_word2vec_format('GoogleNews-vectors-negative300.bin', binary=True) 
print model.most_similar(positive=['woman', 'king'], negative=['man'])
print model['computer']
#XXX out of memory
