from datetime import datetime

# Classe Document
# Représente un document générique avec des attributs tels que 'titre', 'auteur', 'date', 'origine', 'url', 'texte'
class Document:
    def __init__(self, titre, date, origine, url, texte, auteur = ""):
        self.titre = titre
        self.auteur = auteur
        self.date = date
        self.origine = origine
        self.url = url
        self.texte = texte

    # Fonction qui retourne le titre du document
    def get_titre(self):
        return self.titre

    # Fonction qui retourne le texte du document
    def get_texte(self):
        return self.texte

    # Fonctions qui fournissent une représentation sous forme de chaîne de caractères de l'objet
    # --
    def __str__(self):
        return f"Titre : {self.titre}\nAuteur : {self.auteur}\nDate : {self.date}\nURL : {self.url}"

    def __repr__(self):
        return f"Titre : {self.titre}\nAuteur : {self.auteur}\nDate : {self.date}\nURL : {self.url}\nTexte : {self.texte}"
    # --


# Classe RedditDocument
# Hérite de la classe Document et ajoute nbcom (nombre de commentaires)
# Spécifique aux documents provenant de Reddit
class RedditDocument(Document):
    def __init__(self, titre, date, origine, url, texte, auteur, nbcom):
        super().__init__(titre, date, origine, url, texte, auteur)
        self.nbcom = nbcom

    # Fonction qui permet de récupérer le nombre de commentaires associés au document
    def get_nbcom(self):
        return self.nbcom
    
    # Fonction qui permet de définir le nombre de commentaires associés au document
    def set_nbcom(self, nbcom):
        self.nbcom = nbcom

    # Fonctions qui fournissent une représentation textuelle spécifique au nombre de commentaires
    # --
    def __str__(self):
        return f"{super().__str__()}\nNombre de commentaires : {self.nbcom}"

    def __repr__(self):
        return f"{super().__repr__()}\nNombre de commentaires : {self.nbcom}"
    # --


# Classe ArxivDocument
# Hérite de la classe Document et traite les auteurs multiples
# Spécifique aux documents provenant de ArXiv
class ArxivDocument(Document):
    def __init__(self, titre, date, origine, url, texte, auteurs):
        super().__init__(titre, date, origine, url, texte)
        self.auteurs = auteurs

    # Fonctions permettant de manipuler la liste des auteurs associés à ce document
    # --
    def get_auteurs(self):
        return self.auteurs.split(", ")
    
    def set_auteurs(self, auteurs):
        self.auteurs = auteurs

    def add_auteur(self, auteur):
        self.auteurs.append(auteur)
    # --

    # Fonctions qui fournissent une représentation textuelle spécifique aux auteurs multiples
    # --
    def __str__(self):
        return f"Titre : {self.titre}\nAuteur(s) : {self.auteurs}\nDate : {self.date}\nURL : {self.url}"
    
    def __repr__(self):
        return f"Titre : {self.titre}\nAuteur(s) : {self.auteurs}\nDate : {self.date}\nURL : {self.url}\nTexte : {self.texte}"
    # --

# Classe DocumentFactory
# Agit comme une fabrique pour créer des instances de RedditDocument ou ArxivDocument
# en fonction de la nature du document
class DocumentFactory:
    # Fonction qui prend en argument la nature et les informations du document
    # puis crée et retourne l'instance appropriée
    @staticmethod
    def create_document(nature, doc_info):
        if nature == "Reddit":
            return RedditDocument(*doc_info)
        elif nature == "ArXiv":
            return ArxivDocument(*doc_info)
        else:
            raise ValueError("Invalid document nature")