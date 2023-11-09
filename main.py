import praw

import urllib
from urllib.parse import quote
import xmltodict

from datetime import datetime
import pickle

from Document import *
from Author import *
from Corpus import *

subject = "canada"

# ==== REDDIT ====

# Identification
reddit = praw.Reddit(
    client_id = '-w5bIuuQGmj47u4g_BWjkg',
    client_secret = 'ac-sSsGg9sTsRM3SqFlZN5EjUH-JOQ',
    user_agent = 'R-WebScraping'
)

# Requête
limit = 5
dvr_hottest_post = reddit.subreddit(subject).hot(limit=limit)

# Récupération du texte
docs = []
docs_bruts = []
afficher_cles = False
for i, post in enumerate(dvr_hottest_post):
    print("Reddit:", i + 1, "/", limit)
    if afficher_cles:
        for key, value in post.__dict__.items():
            print(key, " : ", value)

    if post.selftext != "":
        pass

    docs.append(post.selftext.replace("\n", " "))
    docs_bruts.append(("Reddit", post))


# ==== ARXIV ====

query = quote(subject)
max_results = 5

url = f"http://export.arxiv.org/api/query?search_query={query}&max_results={max_results}"

response = urllib.request.urlopen(url)
data = response.read().decode()
data = xmltodict.parse(data)

for i, entry in enumerate(data["feed"]["entry"]):
    print("ArXiv:", i + 1, "/", limit)

    docs.append(entry["summary"].replace("\n", " "))
    docs_bruts.append(("ArXiv", entry))


# ==== EXPLOITATION ====

for i, doc in enumerate(docs):
    print(f"Document {i}\t# caractères : {len(doc)}\t# mots : {len(doc.split(' '))}\t# phrases : {len(doc.split('.'))}")
    if len(doc) < 20:
        docs.remove(doc)

print()

longueChaineDeCaracteres = " ".join(docs)


# ==== MANIPULATIONS ====

collection = []

for nature, doc in docs_bruts:
    if nature == "Reddit":

        titre = doc.title.replace("\n", "")
        auteur = str(doc.author)
        date = datetime.fromtimestamp(doc.created).strftime("%Y/%m/%d")
        url = "https://www.reddit.com/" + doc.permalink
        texte = doc.selftext.replace("\n", "")

        doc_classe = Document(titre, auteur, date, "Reddit", url, texte)
        collection.append(doc_classe)

    elif nature == "ArXiv":

        titre = doc["title"].replace("\n", "")
        try:
            authors = ", ".join([a["name"] for a in doc["author"]])
        except:
            authors = doc["author"]["name"]
        summary = doc["summary"].replace("\n", "")
        date = datetime.strptime(doc["published"], "%Y-%m-%dT%H:%M:%SZ").strftime("%Y/%m/%d")
        
        doc_classe = Document(titre, authors, date, "ArXiv", doc["id"], summary)
        collection.append(doc_classe)


# Création de l'index de documents
id2doc = {}
for i, doc in enumerate(collection):
    id2doc[i] = doc.titre


# ==== DICT AUTEURS ====

authors = {}
aut2id = {}
num_auteurs_vus = 0

# Création de la liste + index des auteurs
for doc in collection:
    if doc.auteur not in aut2id:
        num_auteurs_vus += 1
        authors[num_auteurs_vus] = Author(doc.auteur)
        aut2id[doc.auteur] = num_auteurs_vus

    authors[aut2id[doc.auteur]].add(doc.texte)


# ==== CORPUS ====

corpus = Corpus("Mon corpus")

for doc in collection:
    corpus.add(doc)


# ==== SAUVEGARDE ====

with open("corpus.pkl", "wb") as f:
    pickle.dump(corpus, f)

del corpus

with open("corpus.pkl", "rb") as f:
    corpus = pickle.load(f)

corpus.show(tri="123")