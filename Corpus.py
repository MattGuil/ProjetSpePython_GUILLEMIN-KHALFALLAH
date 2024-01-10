import os

import praw

import urllib
from urllib.parse import quote
import xmltodict

from datetime import datetime
import pickle
import math
import re
import pandas as pd
from scipy.sparse import csr_matrix
import numpy as np
import json

from Document import *
from Author import *

class Corpus:

    def __init__(self, nom):
        self.nom = nom
        self.authors = {}
        self.aut2id = {}
        self.id2doc = {}
        self.ndoc = 0
        self.naut = 0
        self.docs = []               # liste des différents textes des documents
        self.concatenated_docs = ''  # chaine de caractères qui concatène l'intégralité des textes des documents
        self.vocab = {}
        self.docs_bruts = []         # liste de toutes les informations nécessaires pour créer une instance d'un object de classe Document
        self.collection = []

        self.mat_TF = None
        self.mat_TFxIDF = None

    def __repr__(self):
        self.docs = list(self.id2doc.values())
        self.docs = list(sorted(self.docs, key=lambda x: x.titre.lower()))

        return "\n\n".join(list(map(str, self.docs)))

    def show(self, n_docs=-1, tri="abc"):
        self.docs = list(self.id2doc.values())
        if tri == "abc":
            self.docs = list(sorted(self.docs, key=lambda x: x.titre.lower()))[:n_docs]
        elif tri == "123":
            self.docs = list(sorted(self.docs, key=lambda x: x.date))[:n_docs]

        print("\n\n".join(list(map(str, self.docs))))

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
        
        self.id2doc[self.ndoc] = doc
        self.ndoc += 1

    def fill(self, subject, nb_articles):
        if os.path.isfile(f"pickles/{subject}.pkl"):
            # ==== LECTURE ====

            with open(f"pickles/{subject}.pkl", "rb") as f:
                corpus = pickle.load(f)

            if corpus.ndoc == nb_articles:
                corpus.show(tri="123")
                print("\n\n")
                print(f"Nombre de documents : {corpus.ndoc}")
                print(f"Nombre d'auteurs : {corpus.naut}")
                pass
        
        nb_articles = math.floor(nb_articles / 2)

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

            self.docs.append(post.selftext.replace("\n", " "))
            self.docs_bruts.append(("Reddit", post))

        # ==== ARXIV ====

        query = quote(subject)

        url = f"http://export.arxiv.org/api/query?search_query={query}&max_results={nb_articles}"

        response = urllib.request.urlopen(url).read()
        data = response.decode("utf-8")
        data = xmltodict.parse(data)["feed"]["entry"]

        for entry in data:
            self.docs.append(entry["summary"].replace("\n", " "))
            self.docs_bruts.append(("ArXiv", entry))

        # ==== NETTOYAGE ====

        indices_to_remove = []

        for index, doc in enumerate(self.docs):
            if len(doc) < 20:
                indices_to_remove.append(index)

        for index in sorted(indices_to_remove, reverse=True):
            del self.docs[index]
            del self.docs_bruts[index]

        print(f"Nombre de docs supprimés : {len(indices_to_remove)}")

        # ==== MANIPULATIONS ====

        for nature, doc in self.docs_bruts:
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
            self.collection.append(doc_instance)

        for doc in self.collection:
            self.add(doc)

        self.show(tri="123")
        print("\n\n")
        print(f"Nombre de documents : {self.ndoc}")
        print(f"Nombre d'auteurs : {self.naut}")

        # Sauvegarde dans un fichier .pkl
        with open(f"pickles/{subject}.pkl", "wb") as f:
            pickle.dump(self, f)

    def search(self, keyword, context_size=30):
        for doc in self.docs:
            print(type(doc))
        if self.concatenated_docs == '':
            self.concatenated_docs = self.nettoyer(' ` '.join(self.docs))
        
        pattern = re.compile(fr'\b{re.escape(keyword)}\b', re.IGNORECASE)
        matches = pattern.finditer(self.concatenated_docs)
        
        data = {'contexte gauche': [], 'keyword': [], 'contexte droit': []}

        for match in matches:
            start_index = max(0, match.start() - context_size)
            end_index = min(len(self.concatenated_docs), match.end() + context_size)
            
            context_left = self.concatenated_docs[start_index:match.start()]
            context_right = self.concatenated_docs[match.end():end_index]

            data['contexte gauche'].append(context_left)
            data['keyword'].append(match.group())
            data['contexte droit'].append(context_right)
        
        df = pd.DataFrame(data)
        print(f"Nombre d'occurrences de {keyword} : {len(df)}")
        print(df)
        
        return df
    
    def nettoyer(self, text):
        text = text.lower()
        text = text.replace('\n', ' ')
        text = re.sub(r'[^a-z àáâãäåæçèéêëìíîïðòóôõöøùúûüýÿ`\']', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        return text
    
    def create_vocabulary(self, method=1):
        vocabulary = {}
        documents = self.concatenated_docs.split('`')
        documents = [doc.strip() for doc in documents]
        row_indices = []
        col_indices = []
        data = []

        for doc_index, doc in enumerate(documents):

            for word in sorted(doc.split(' ')):
                if word in self.vocab:
                    self.vocab[word] += 1
                else:
                    self.vocab[word] = 1

                if word not in vocabulary:
                    vocabulary[word] = len(vocabulary)

                word_index = vocabulary[word]
                row_indices.append(doc_index)
                col_indices.append(word_index)
                data.append(doc.split(' ').count(word))

        print('len(documents)')
        print(len(documents))
        self.mat_TF = csr_matrix((data, (row_indices, col_indices)), shape=(len(documents), len(vocabulary)))

        document_frequency = (self.mat_TF > 0).sum(axis=0)
        document_frequency = np.asarray(document_frequency).reshape(-1)
        
        for word, index in vocabulary.items():
            doc_freq = document_frequency[index]

            self.vocab[word] = {
                'id': index + 1,
                'occurencies': self.vocab[word],
                'document frequency': int(doc_freq)
            }

        with open('./vocab.json', 'w') as file:
            json.dump(self.vocab, file, indent=4)

        
        # -- Calcul de la matrice TFxIDF --
        print()
        print("documents")
        print(documents)

        N = len(documents) + 1

        DF = (self.mat_TF > 0).sum(axis=0)
        IDF = np.log(N / DF)

        print()
        print('TF')
        print(self.mat_TF.shape)
        print(self.mat_TF)
        print()
        print('DF')
        print(DF.shape)
        print(DF)
        print()
        print('IDF')
        print(IDF.shape)
        print(IDF)

        IDF_diagonal = np.diag(np.squeeze(np.asarray(IDF)))

        self.mat_TFxIDF = self.mat_TF.dot(IDF_diagonal)

        print()
        print('IDF SQUEEZED')
        print(np.squeeze(np.asarray(IDF)))
        print()
        print('IDF DIAGONAL')
        print(IDF_diagonal.shape)
        print(IDF_diagonal)
        print()
        print('TFxIDF')
        print(self.mat_TFxIDF.shape)
        print(self.mat_TFxIDF)
        print()
        print('VOCAB')
        print(self.vocab)

    def compute_similarity(self, keywords):

        keywords = keywords.split(',')
        keywords = [word.strip() for word in keywords]

        # Récupérer les index des mots correspondant aux mots-clés dans le vocabulaire
        vocab_keys = list(self.vocab.keys())
        keywords_indices = [vocab_keys.index(word) for word in keywords if word in vocab_keys]

        # Récupérer la matrice TFxIDF correspondant aux mots-clés
        keywords_matrix = np.zeros(self.mat_TFxIDF.shape)
        keywords_matrix = np.where(keywords_matrix == 0, 1e-10, keywords_matrix)
        keywords_matrix[:, keywords_indices] = self.mat_TFxIDF[:, keywords_indices]

        # Calculer la norme des vecteurs de la matrice des mots-clés et de chaque document
        norm_keywords = np.linalg.norm(keywords_matrix, axis=1)
        norm_documents = np.linalg.norm(self.mat_TFxIDF, axis=1)

        print()
        print('norm_keywords')
        print(norm_keywords)

        print()
        print('norm_documents')
        print(norm_documents)

        # Calculer le produit scalaire entre la matrice des mots-clés et chaque document
        produit_scalaire = np.dot(self.mat_TFxIDF, keywords_matrix.T)

        print()
        print('PRODUIT SCALAIRE')
        print(produit_scalaire.shape)
        print(produit_scalaire)

        # Calculer la similarité cosine
        similarite = produit_scalaire / (norm_documents[:, np.newaxis] * norm_keywords)

        # Obtenir les indices triés des documents par similarité décroissante
        indices_tries = np.argsort(similarite[:, 0])[::-1]

        print()
        print('SIMILARITE')
        print(similarite)
        print()
        print('INDICES TRIES')
        print(indices_tries)
        
        # Afficher les meilleurs résultats
        for idx in indices_tries:
            print(f"Document '{self.id2doc[idx]}' - Similarité : {similarite[idx, 0]}")