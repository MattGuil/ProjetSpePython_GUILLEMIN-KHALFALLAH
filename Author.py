# Classe Author
# Représente un auteur avec des attributs tels que 'name', 'ndoc', 'production'
class Author:
    # Tout auteur a, par défaut, un nom et une liste de productions vide
    def __init__(self, name):
        self.name = name
        self.ndoc = 0
        self.production = []

    # Afficher un auteur revient à afficher son nom et son nombre de productions
    def __str__(self):
        return f"Auteur : {self.name} ({self.ndoc} production(s))"

    # Fonction qui permet d'ajouter une production à la liste de productions de l'auteur (self) 
    def add(self, production):
        self.ndoc += 1
        self.production.append(production)