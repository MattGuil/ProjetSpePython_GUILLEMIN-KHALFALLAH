from datetime import datetime

class Document:
    def __init__(self, titre, date, origine, url, texte, auteur = ""):
        self.titre = titre
        self.auteur = auteur
        self.date = date
        self.origine = origine
        self.url = url
        self.texte = texte

    def get_texte(self):
        return self.texte

    def __str__(self):
        return f"Titre : {self.titre}\nAuteur : {self.auteur}\nDate : {self.date}\nURL : {self.url}"

    def __repr__(self):
        return f"Titre : {self.titre}\nAuteur : {self.auteur}\nDate : {self.date}\nURL : {self.url}\nTexte : {self.texte}"


class RedditDocument(Document):
    def __init__(self, titre, date, origine, url, texte, auteur, nbcom):
        super().__init__(titre, date, origine, url, texte, auteur)
        self.nbcom = nbcom

    def get_nbcom(self):
        return self.nbcom
    
    def set_nbcom(self, nbcom):
        self.nbcom = nbcom

    def __str__(self):
        return f"{super().__str__()}\nNombre de commentaires : {self.nbcom}"

    def __repr__(self):
        return f"{super().__repr__()}\nNombre de commentaires : {self.nbcom}"


class ArxivDocument(Document):
    def __init__(self, titre, date, origine, url, texte, auteurs):
        super().__init__(titre, date, origine, url, texte)
        self.auteurs = auteurs

    def get_auteurs(self):
        return self.auteurs.split(", ")
    
    def set_auteurs(self, auteurs):
        self.auteurs = auteurs

    def add_auteur(self, auteur):
        self.auteurs.append(auteur)

    def __str__(self):
        return f"Titre : {self.titre}\nAuteur(s) : {self.auteurs}\nDate : {self.date}\nURL : {self.url}"
    
    def __repr__(self):
        return f"Titre : {self.titre}\nAuteur(s) : {self.auteurs}\nDate : {self.date}\nURL : {self.url}\nTexte : {self.texte}"


class DocumentFactory:
    @staticmethod
    def create_document(nature, doc_info):
        if nature == "Reddit":
            return RedditDocument(*doc_info)
        elif nature == "ArXiv":
            return ArxivDocument(*doc_info)
        else:
            raise ValueError("Invalid document nature")