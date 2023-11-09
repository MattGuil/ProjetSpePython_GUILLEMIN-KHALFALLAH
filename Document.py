from datetime import datetime

class Document:
    def __init__(self, titre, auteur, date, origine, url, texte):
        self.titre = titre
        self.auteur = auteur
        self.date = date
        self.origine = origine
        self.url = url
        self.texte = texte

    def __str__(self):
        # return f"{self.titre}\nécrit par {self.auteur}\nparu le {datetime.strptime(self.date, '%Y/%m/%d').strftime('%d/%m/%Y')}\n({self.origine})"
        pass

    def __repr__(self):
        return f"Titre : {self.titre}\tAuteur : {self.auteur}\t Date : {self.date}\tURL : {self.url}\tTexte : {self.texte}\t"