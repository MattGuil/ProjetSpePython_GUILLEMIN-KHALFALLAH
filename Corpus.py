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

# Classe Corpus
# Dédiée à la gestion de la thématique de recherche,
# càd au stockage et au traitement de toutes les données liés aux documents renvoyés par la requête de l'utilisateur
# Cela inclut les auteurs des documents en question
# Cette classe contient également toutes les fonctions utiles à la recherche par mots clés
class Corpus:

    def __init__(self, nom):
        self.nom = nom
        self.authors = {}                   # Dictionnaire regroupant tous les auteurs (Author) du corpus
        self.aut2id = {}                    # Dictionnaire associant chaque auteur à son identifiant unique
        self.id2doc = {}                    # Dictionnaire regroupant tous les documents (Documents) du corpus
        self.ndoc = 0                       # Nombre de documents dans le corpus
        self.naut = 0                       # Nombre d'auteurs dans le corpus
        self.docs = []                      # Liste contenant les titres de tous les documents
        self.concatenated_titles = ''       # String concatènant l'intégralité des titres des documents, espacés par '`'
        self.vocab = {}                     # Vocabulaire du corpus, càd une liste exhaustive des mots que comportent les titres de tous les documents (sans doublons)
        self.docs_bruts = []                # Liste contenant toutes les informations nécessaires pour créer une instance de classe Document
        self.collection = []                # Liste contenant toutes les instances de RedditDocument et ArxivDocument

        self.mat_TF = None                  # TF pour Term Frequency.
                                            # Matrice représentant le nombre d'occurences de chacun des mots du vocabulaire dans le corpus
        self.mat_TFxIDF = None              # TFxIDF pour Term Frequency x Inverse Document Frequency.
                                            # Matrice alternative à TF : En plus de représenter le nombre d'occurences de chacun des mots,
                                            # elle permet d'évaluer l'importance d'un mot au sein d'un document donné
                                            # Indispensable à la pertinence de notre moteur de recherche.

    
    # Fonctions qui fournissent une représentation textuelle du corpus (liste de tous les documents)
    # --
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
    # --

    # Fonction qui permet d'ajouter un document au corpus
    # L'opération est effectuée dépendamment de l'origine du document
    # et engendre automatiquement la mise à jour de la liste des auteurs du corpus
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

    # Fonction principale de la classe Corpus
    # Entrée    : Demande de l'utilisateur (sujet, nombre d'articles souhaité)
    # Opération : Requêtes vers les API de Reddit et ArXiv
    # Sortie    : Remplissage et enregistrement du corpus dans un fichier .pkl
    def fill(self, subject, nb_articles):
        
        if os.path.isfile(f"pickles/{subject}.pkl"):
            
            with open(f"pickles/{subject}.pkl", "rb") as f:
                corpus = pickle.load(f)

            # Si la recherche de l'utilisateur a déjà été effectuée précedemment, on charge la sauvegarde
            # Pas besoin de faire appel aux APIs
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

        # Remplissage des listes docs et docs_bruts avec les résultats de la requête
        afficher_cles = False
        for post in hottest_post:
            if afficher_cles:
                for key, value in post.__dict__.items():
                    print(key, " : ", value)

            if post.selftext != "":
                pass

            self.docs.append(post.title.replace("\n", " "))
            self.docs_bruts.append(("Reddit", post))

        # ==== ARXIV ====

        # Préparation et réalisation de la requête
        query = quote(subject)

        url = f"http://export.arxiv.org/api/query?search_query={query}&max_results={nb_articles}"

        response = urllib.request.urlopen(url).read()
        data = response.decode("utf-8")
        data = xmltodict.parse(data)["feed"]["entry"]

        # Remplissage des listes docs et docs_bruts avec les résultats de la requête
        for entry in data:
            self.docs.append(entry["title"].replace("\n", " "))
            self.docs_bruts.append(("ArXiv", entry))

        # Nettoyage
        # On retire du corpus les documents dont le titre fait moins de 20 caractères
        # --
        indices_to_remove = []

        for index, doc in enumerate(self.docs):
            if len(doc) < 20:
                indices_to_remove.append(index)

        for index in sorted(indices_to_remove, reverse=True):
            del self.docs[index]
            del self.docs_bruts[index]

        print(f"Nombre de docs supprimés : {len(indices_to_remove)}")
        # --

        # Manipulations
        for nature, doc in self.docs_bruts:
            if nature == "Reddit":      # Si le document est de type Reddit
                doc_info = (            # Son doc_info sera : 
                    doc.title.replace("\n", ""),                                # Son Titre
                    datetime.fromtimestamp(doc.created).strftime("%Y/%m/%d"),   # Sa date de publication
                    "Reddit",                                                   # Son origine
                    "https://www.reddit.com/" + doc.permalink,                  # Son url
                    doc.selftext.replace("\n", ""),                             # Son contenu
                    str(doc.author),                                            # Son unique auteur
                    doc.num_comments                                            # Le nombre de commentaires
                )

            elif nature == "ArXiv":     # Si le document est de type Arxiv
                try:
                    auteurs = ", ".join([a["name"] for a in doc["author"]])     # Joindre les noms de tous les auteurs, s'il y en a plusieurs
                except:
                    auteurs = doc["author"]["name"]                             # Prendre le nom de l'auteur s'il n'y en a qu'un
                
                doc_info = (                                                    # Et continuer similairement à Reddit
                    doc["title"].replace("\n", ""),         
                    datetime.strptime(doc["published"], "%Y-%m-%dT%H:%M:%SZ").strftime("%Y/%m/%d"),
                    "ArXiv",
                    doc["id"],
                    doc["summary"].replace("\n", ""),
                    auteurs,
                )

            else:   # En cas de type manquant (bug), ignorer le doc
                continue

            doc_instance = DocumentFactory.create_document(nature, doc_info)    # Creer concretement le doc grace a doc_info
            self.collection.append(doc_instance)                                # Append ce doc à collection

        for doc in self.collection:
            self.add(doc)           # Add au corpus tous les documents reunis de collection 

        self.show(tri="123")
        print("\n\n")
        print(f"Nombre de documents : {self.ndoc}")
        print(f"Nombre d'auteurs : {self.naut}")

        if not os.path.exists('pickles'):
            os.makedirs('pickles')

        # Sauvegarde dans un fichier .pkl
        with open(f"pickles/{subject}.pkl", "wb") as f:
            pickle.dump(self, f)


    # Creation de la fonction search, qui effectue un nettoyage sur tous les contenus de document
    # en utilisant du RegExp, et cree ensuite le concordancier
    def search(self, keyword, context_size=30):  

        if self.concatenated_titles == '':      # Si l'operation n'a pas deja été faite
            if type(self.docs[0]) == str:       # (pour eviter un bug, on prend en compte le cas où nous avons un string en entree et non un doc)
                self.concatenated_titles = self.nettoyer(' ` '.join(self.docs))
            else:
                for doc in self.docs:
                    self.concatenated_titles += f"{doc.get_titre()} ` "     # Pour chaque doc, concatener son titre à la recherche
                self.nettoyer(self.concatenated_titles)                     # Et les nettoyer
        
        # Cree le pattern RegExp en compilant la demande donnée, en ignorant la casse
        pattern = re.compile(fr'\b{re.escape(keyword)}\b', re.IGNORECASE)   # (GENERE PAR ChatGPT)
        matches = pattern.finditer(self.concatenated_titles)    # Cherche les occurences pertinentes dans pattern, et les stocke dans matches
        
        data = {'contexte gauche': [], 'keyword': [], 'contexte droit': []}


        for match in matches:
            start_index = max(0, match.start() - context_size)
            end_index = min(len(self.concatenated_titles), match.end() + context_size)
            
            context_left = self.concatenated_titles[start_index:match.start()]
            context_right = self.concatenated_titles[match.end():end_index]

            data['contexte gauche'].append(context_left)
            data['keyword'].append(match.group())
            data['contexte droit'].append(context_right)
        
        df = pd.DataFrame(data)
        print(f"Nombre d'occurrences de {keyword} : {len(df)}")
        print(df)
        
        return df
    
    # Effectue un nettoyage sur le string d'entree text
    def nettoyer(self, text):
        text = text.lower()                 # Met tout en minuscule
        text = text.replace('\n', ' ')      # Remplace les retours a la ligne par des espaces
        text = re.sub(r'[^a-z àáâãäåæçèéêëìíîïðòóôõöøùúûüýÿ`\']', ' ', text)    # Remplace tous les caracteres, sauf ceux entre crochets, par un espace
        text = re.sub(r'\s+', ' ', text)    # Remplace tous les espaces supplémentaires/inutiles par un unique espace au lieu
        return text
    
    def create_vocabulary(self):
        vocabulary = {}     # Dico contenant les mots et leur donnees
        documents = self.concatenated_titles.split('`')     # Cree un tableau en separant les titres par leur separateur `
        documents = [doc.strip() for doc in documents]      # Enleve les espaces inutiles avant et apres les titres
        row_indices = []
        col_indices = []
        data = []

        for doc_index, doc in enumerate(documents):     # Pour chaque doc

            for word in sorted(doc.split(' ')): # Pour chaque mot
                if word in self.vocab:
                    self.vocab[word] += 1   # Si le mot est dans le vocab, +1
                else:
                    self.vocab[word] = 1    # Si le mot n'est pas dans le vocab, cree sa cle, et sa valeur de base

                if word not in vocabulary:  # Si le mot n'est pas dans le vocabulaire general, l'ajouter pour avoir son indice 
                    vocabulary[word] = len(vocabulary)

                word_index = vocabulary[word] 
                row_indices.append(doc_index)
                col_indices.append(word_index)
                data.append(doc.split(' ').count(word))

        print(f"\nLength de \'documents\' : {len(documents)}")

        # Creation de la matrice TF grace à la librairie scipy
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

        # Creation du json contenant le vocabulaire 
        with open('./vocab.json', 'w') as file:
            json.dump(self.vocab, file, indent=4)

        
        # -- Calcul de la matrice TFxIDF --
        print("\n\nDocuments")
        print(documents)

        N = len(documents) + 1

        DF = (self.mat_TF > 0).sum(axis=0)
        IDF = np.log(N / DF)

        print(f"\n\nTF : Shape = {self.mat_TF.shape}")
        print(self.mat_TF)

        print(f"\n\nDF: Shape = {DF.shape}")
        print(DF)

        print(f"\n\nIDF: Shape = {IDF.shape}")
        print(IDF)

        IDF_diagonal = np.diag(np.squeeze(np.asarray(IDF)))
        self.mat_TFxIDF = self.mat_TF.dot(IDF_diagonal)

        print('\n\nIDF SQUEEZED')
        print(np.squeeze(np.asarray(IDF)))

        print(f"\n\nIDF DIAGONAL : Shape = {IDF_diagonal.shape}")
        print(IDF_diagonal)

        print(f"\n\nTFxIDF : Shape = {self.mat_TFxIDF.shape}")
        print(self.mat_TFxIDF)

        print(f"\n\nVOCAB")
        print(self.vocab)

    # Fonction qui classe les documents du corpus en fonction des mots clés saisis par l'utilisateur
    # (Plus le titre d'un document contient de mots clés, plus le document qui lui est associé remonte dans le classement)
            # Cette fonction à été majoritairement générée par ChatGPT. Après s'etre bloqué dessus pendant quelques heures, nous avons
            # décidé de lui ceder cette tache.
    def compute_similarity(self, keywords):

        # Création de la liste des mots clés entrés par l'utilisateur
        keywords = keywords.split(',')
        keywords = [word.strip() for word in keywords]

        # Récupération des index des mots correspondants aux mots-clés dans le vocabulaire du corpus
        vocab_keys = list(self.vocab.keys())
        keywords_indices = [vocab_keys.index(word) for word in keywords if word in vocab_keys]

        # Récupération de la matrice TFxIDF correspondant aux mots-clés
        keywords_matrix = np.zeros(self.mat_TFxIDF.shape)
        keywords_matrix = np.where(keywords_matrix == 0, 1e-10, keywords_matrix)
        keywords_matrix[:, keywords_indices] = self.mat_TFxIDF[:, keywords_indices]

        # Calcul de la norme des vecteurs de la matrice des mots-clés et de chaque document
        norm_keywords = np.linalg.norm(keywords_matrix, axis=1)
        norm_documents = np.linalg.norm(self.mat_TFxIDF, axis=1)

        print('\n\nnorm_keywords')
        print(norm_keywords)

        print('\n\nnorm_documents')
        print(norm_documents)

        # Calcul du produit scalaire entre la matrice des mots-clés et chaque document
        produit_scalaire = np.dot(self.mat_TFxIDF, keywords_matrix.T)

        print(f"\n\nPRODUIT SCALAIRE : Shape = {produit_scalaire.shape}")
        print(produit_scalaire)

        # Calcul de la similarité cosine
        similarite = produit_scalaire / (norm_documents[:, np.newaxis] * norm_keywords)

        sorted_results = []
        indices_tries = np.argsort(similarite[:, 0])[::-1]

        # Création de la liste des documents triés suivant leur pertinence par rapport à la requête de l'utilisateur
        for idx in indices_tries:
            document_info = self.id2doc[idx]
            similarity = similarite[idx, 0]

            sorted_results.append((document_info, similarity))
        
        return sorted_results