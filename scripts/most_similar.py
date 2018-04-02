#!/usr/bin/python3

import gensim

import config

# load model
model = gensim.models.Word2Vec.load(config.model)
wv = model.wv
del model

print(wv.most_similar_cosmul(positive=["lol"]))
