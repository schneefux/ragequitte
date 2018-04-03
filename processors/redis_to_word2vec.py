#!/usr/bin/python3

import logging
import time
import sys

import redis
import gensim

import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

r = redis.StrictRedis(**{ **config.redis, "decode_responses": True })

# load or create model
model_updating = True
try:
    model = gensim.models.Word2Vec.load(config.model)
except Exception as e:
    model = gensim.models.Word2Vec(iter=1, min_count=10, size=200, workers=4, sg=1)
    # defaults. iter=1: only iterate once, sg=1: use skip gram (needs more data)
    model_updating = False


def clean_words(words):
    clean_words = []

    if len(words) == 0:
        return []  # return early

    # skip popular bot commands
    bot_prefixes = ["?", "!", ".", "~", "+", ",", "$"]
    if (len(words[0]) > 0 and words[0][0] in bot_prefixes) or \
            (len(words[0]) > 1 and words[0][1] in bot_prefixes):
        return []  # return early

    for word in words:
        if len(word) == 0:
            continue

        # skip discord mentions
        if (word.startswith("<") and word.endswith(">")) or word.startswith("http"):
            continue
        
        # replace markdown
        word = word.replace("**", "").replace("__", "").replace("`", "")
        if len(word) == 0:
            continue

        # turn to lowercase - except if 2/3rds of the text is uppercase
        lowercase_chars = sum(1 for c in word if c.islower())
        uppercase_chars = sum(1 for c in word if c.isupper())
        chars = lowercase_chars + uppercase_chars
        if lowercase_chars * 3 <= uppercase_chars:
            word = word.lower()
        else:
            word = word.upper()

        # remove punctuation - not for emoticons
        punctuation_end = ["?", "!", ",", ".", ";", "(", ")", "\"", "'"]
        if word[-1] in punctuation_end and chars > 2:
            word = word[:-1]

        punctuation_start = ["(", "\"", "'"]
        if word[0] in punctuation_start and chars > 2:
            word = word[1:]

        # done.
        if len(word) > 1:
            clean_words.append(word)

    return clean_words


class RedisIterator(object):
    def __init__(self, match, deleting=False, cleaning=True):
        self.match = match
        self.deleting = deleting
        self.cleaning = cleaning

    def __iter__(self):
        for key in r.scan_iter(match=self.match):
            words = r.get(key).split()

            if self.cleaning:
                words = clean_words(words)
            if len(words) == 0:
                continue

            yield words

            if self.deleting and not config.debug:
                r.delete(key)


def discord_batch_handler(message):
    global model_updating
    print("building vocabulary")
    model.build_vocab(RedisIterator(match="message:*", deleting=False), update=model_updating)
    print("vocabulary size: {}".format(len(model.wv.vocab)))
    print("training")
    model.train(RedisIterator(match="message:*", deleting=True), total_examples=model.corpus_count, epochs=model.epochs)
    print("trained")
    model.save(config.model)
    model_updating = True
    if config.debug:
        sys.exit()


p = r.pubsub(ignore_subscribe_messages=True)
p.subscribe(**{ "discord_to_redis": discord_batch_handler })

discord_batch_handler(None)  # initial start
while True:
    p.get_message()
    time.sleep(0.001)
