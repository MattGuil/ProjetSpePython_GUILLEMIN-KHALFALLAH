# Projet Spécialité Python

# Elyes KHALFALLAH
# Matthieu GUILLEMIN

# v1

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

docs = []
docs_bruts = []

# ==== REDDIT ====

reddit = praw.Reddit(
    client_id = '-w5bIuuQGmj47u4g_BWjkg',
    client_secret = 'ac-sSsGg9sTsRM3SqFlZN5EjUH-JOQ',
    user_agent = 'R-WebScraping'
)

limit = 5
hottest_post = reddit.subreddit(subject).hot(limit=limit+1)

afficher_cles = False
for post in hottest_post:
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

response = urllib.request.urlopen(url).read()
data = response.decode("utf-8")
data = xmltodict.parse(data)["feed"]["entry"]

for entry in data:
    docs.append(entry["summary"].replace("\n", " "))
    docs_bruts.append(("ArXiv", entry))

# Nettoyage

for doc in docs:
    if len(doc) < 20:
        docs.remove(doc)

# Manipulations

collection = []

for nature, doc in docs_bruts:
    if nature == "Reddit":
        doc_info = (
            doc.title.replace("\n", ""),
            datetime.fromtimestamp(doc.created).strftime("%Y/%m/%d"),
            "Reddit",
            "https://www.reddit.com/" + doc.permalink,
            doc.selftext.replace("\n", ""),
            str(doc.author),
            doc.num_comments
        )
    elif nature == "ArXiv":
        try:
            auteurs = ", ".join([a["name"] for a in doc["author"]])
        except:
            auteurs = doc["author"]["name"]
        
        doc_info = (
            doc["title"].replace("\n", ""),
            datetime.strptime(doc["published"], "%Y-%m-%dT%H:%M:%SZ").strftime("%Y/%m/%d"),
            "ArXiv",
            doc["id"],
            doc["summary"].replace("\n", ""),
            auteurs,
        )
    else:
        continue

    doc_instance = DocumentFactory.create_document(nature, doc_info)
    collection.append(doc_instance)


id2doc = {}
for i, doc in enumerate(collection):
    id2doc[i] = doc.titre

authors = {}
aut2id = {}
num_auteurs_vus = 0

for doc in collection:
    if doc.auteur not in aut2id:
        num_auteurs_vus += 1
        authors[num_auteurs_vus] = Author(doc.auteur)
        aut2id[doc.auteur] = num_auteurs_vus

    authors[aut2id[doc.auteur]].add(doc.texte)


corpus = Corpus("Mon corpus")

for doc in collection:
    corpus.add(doc)


# Sauvegarde

with open("pickles/corpus.pkl", "wb") as f:
    pickle.dump(corpus, f)

del corpus

with open("pickles/corpus.pkl", "rb") as f:
    corpus = pickle.load(f)

corpus.show(tri="123")
print("\n\n")
print(f"Nombre de documents : {corpus.ndoc}")
print(f"Nombre d'auteurs : {corpus.naut}")