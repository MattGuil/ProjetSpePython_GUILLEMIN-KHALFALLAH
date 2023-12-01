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
    def reset(self):
        Corpus._instance = None