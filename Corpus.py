import os

import praw

import urllib
from urllib.parse import quote
import xmltodict

from datetime import datetime
import pickle

from Document import *
from Author import *


class Corpus:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, nom):
        if not hasattr(self, 'initialized'):
            self.nom = nom
            self.authors = {}
            self.aut2id = {}
            self.id2doc = {}
            self.ndoc = 0
            self.naut = 0
            self.initialized = True

    def __repr__(self):
        docs = list(self.id2doc.values())
        docs = list(sorted(docs, key=lambda x: x.titre.lower()))

        return "\n\n".join(list(map(str, docs)))

    def show(self, n_docs=-1, tri="abc"):
        docs = list(self.id2doc.values())
        if tri == "abc":
            docs = list(sorted(docs, key=lambda x: x.titre.lower()))[:n_docs]
        elif tri == "123":
            docs = list(sorted(docs, key=lambda x: x.date))[:n_docs]

        print("\n\n".join(list(map(str, docs))))

    def add(self, doc):
        if doc.origine == "Reddit":
            if doc.auteur not in self.aut2id:
                self.naut += 1
                self.authors[self.naut] = Author(doc.auteur)
                self.aut2id[doc.auteur] = self.naut
            self.authors[self.aut2id[doc.auteur]].add(doc.texte)
        elif doc.origine == "ArXiv":
            for aut in doc.get_auteurs():
                if aut not in self.aut2id:
                    self.naut += 1
                    self.authors[self.naut] = Author(aut)
                    self.aut2id[aut] = self.naut
                self.authors[self.aut2id[aut]].add(doc.texte)
        
        self.ndoc += 1
        self.id2doc[self.ndoc] = doc

    @staticmethod
    def recherche(subject, nb_articles):
        if os.path.isfile(f"{subject}.pkl"):
            # ==== LECTURE ====

            with open(f"{subject}.pkl", "rb") as f:
                corpus = pickle.load(f)

            corpus.show(tri="123")
            print("\n\n")
            print(f"Nombre de documents : {corpus.ndoc}")
            print(f"Nombre d'auteurs : {corpus.naut}")

        else:

            docs = []           # liste des différents textes des documents
            docs_bruts = []     # liste de toutes les informations nécessaires pour créer une instance d'un object de classe Document

            # ==== REDDIT ====

            # Identification
            reddit = praw.Reddit(
                client_id = '-w5bIuuQGmj47u4g_BWjkg',
                client_secret = 'ac-sSsGg9sTsRM3SqFlZN5EjUH-JOQ',
                user_agent = 'R-WebScraping'
            )

            # Requête
            hottest_post = reddit.subreddit(''.join(subject.split())).hot(limit=nb_articles+1)

            # Récupération du texte
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

            url = f"http://export.arxiv.org/api/query?search_query={query}&max_results={nb_articles}"

            response = urllib.request.urlopen(url).read()
            data = response.decode("utf-8")
            data = xmltodict.parse(data)["feed"]["entry"]

            for entry in data:
                docs.append(entry["summary"].replace("\n", " "))
                docs_bruts.append(("ArXiv", entry))

            # ==== NETTOYAGE ====

            '''
            for doc in docs:
                if len(doc) < 20:
                    docs.remove(doc)
            '''

            # ==== MANIPULATIONS ====

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

            with open(f"{subject}.pkl", "wb") as f:
                pickle.dump(corpus, f)

            # ==== LECTURE ====

            with open(f"{subject}.pkl", "rb") as f:
                corpus = pickle.load(f)

            corpus.show(tri="123")
            print("\n\n")
            print(f"Nombre de documents : {corpus.ndoc}")
            print(f"Nombre d'auteurs : {corpus.naut}")