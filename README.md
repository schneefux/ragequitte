# ragequitte

Tech to evaluate:
  * UI
    * https://tabler.github.io/
  * NLP
    * https://github.com/orsinium/textdistance
    * http://www.nltk.org/
    * https://textblob.readthedocs.io/en/dev/index.html
    * https://spacy.io/
  * other
    * https://prodi.gy/

SETUP
---

  * Create a virtual Python environment `virtualenv venv -p python3`
  * Enter it `source venv/bin/activate`
  * Install dependencies `pip install -r requirements.txt`
  * Set up a Redis server
  * Copy and modify `config_example.py`

USAGE
---

  * Enter the virtual environment
  * Start the Discord log collector (optional): `PYTHONPATH="." python grabbers/discord_to_redis.py`
  * Train a word2vec model: `PYTHONPATH="." python processors/redis_to_word2vec.py`
  * Try the model, run an interactive Python shell with `python`:
    * `>>> import gensim`
    * `>>> import config`
    * `>>> model = gensim.models.Word2Vec.load(config.model)`
    * `>>> model.wv.most_similar_cosmul("what", topn=4)`
    * `[('where', 0.8449756503105164), ('how', 0.8136355876922607), ('whatever', 0.8117746114730835), ('why', 0.8039281368255615)]`
    * `>>> model.wv.similarity("league", "dota")`
    * `0.6141897432617985`
  * more examples here: https://radimrehurek.com/gensim/models/keyedvectors.html
