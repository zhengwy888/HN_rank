
Summary
-------------
These codes are an attempt to build a vote score predictor from [Hackers News](https://news.ycombinator.com/) Stories.

The best resulting accuracy was just hitting 70%, which is not good enough to be any practical usage. 

Takeaway lesson: to use neural network effectively, one has to become the **meta neural-network** that learns which model to choose under different circumstance. This requires lots of experience, a bit of intuition, and more trial-and-error. There are very little systematic ways about picking the best model.

Comparison of Classifiers
-----------
Classifier     | Accuracy
-------- | ---
Metamind[^metamind] | 68%
seq2-CNN[^cnnpaper]    | 70%
NearestCentroid[^scikit]     | 63%
Perceptron[^scikit]   | 60%

While there are other classifiers from sci-kit learn, their accuracy weren't much better than a random guess.

Experiment Data
--------
I used the firebase API from Hackers News, grabbed 20000+ webpage content from the links of HN story post. There are a lot more post with 15 or less score so I excluded them after crawling for a while. The content, score and word_count are stored in a postgresql database.
Exclude post with < 100 which usually indicate a crawler problem, or the original page is a video/image.

```
select
      case when s.score >= 0 and s.score <= 15    then '  0 - 15'
           when s.score > 15 and s.score <= 40   then ' 15+ - 40'
           when s.score > 40 and s.score <= 80  then ' 40+ - 80'
           when s.score > 80 and s.score <= 150  then ' 80+ - 150'
           else 'over 150'
      end ScoreRange,
      count(*) as TotalWithinRange
   from
      story_contents sc LEFT JOIN story s ON s.id = sc.id
   where sc.word_count > 100 group by 1;                                                  
```

 scorerange | totalwithinrange 
------------ |------------------
  80+ - 150 |             2532
 over 150   |             2530
  40+ - 80  |             2765
   0 - 15   |            10200
  15+ - 40  |             2359


Package and Reference
------
[^scikit]: [scikit learn](http://scikit-learn.org/stable/index.html): A python package with lots of good stuff. Easy to understand example code, and fast prototyping.

[^metamind]: [Metamind](https://www.metamind.io) has very easy to use API, and easy to understand reporting page for classifier performance. Though out of the box I am guessing the classifier doesn't work that well. 

[^cnnpaper]: Rie Johnson and Tong Zhang. _Effective use of word order for text categorization with convolutional neural networks._ To appear in NAACL-HLT 2015. Also available as arXiv:1412.1058v2. 
To run this, I used a public AMI image that had CUDA 6.5 pre-installed on AWS. [Source](http://riejohnson.com/cnn_download.html)



