class Author:
    def __init__(self, name):
        self.name = name
        self.ndoc = 0
        self.production = []

    def __str__(self):
        return f"Auteur : {self.name} ({self.ndoc} production(s))"

    def add(self, production):
        self.ndoc += 1
        self.production.append(production)