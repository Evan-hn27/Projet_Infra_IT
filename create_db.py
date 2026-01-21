import sqlite3

connection = sqlite3.connect('database.db')

with open('schema.sql') as f:
    connection.executescript(f.read()) #com

cur = connection.cursor()

cur.execute('''
CREATE TABLE IF NOT EXISTS livres (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titre TEXT NOT NULL,
    auteur TEXT NOT NULL,
    disponible INTEGER DEFAULT 1
)
''')

cur.execute("INSERT INTO livres (titre, auteur, disponible) VALUES (?, ?, ?)", ("Le Petit Prince", "Antoine de Saint-Exupéry", 1))
cur.execute("INSERT INTO livres (titre, auteur, disponible) VALUES (?, ?, ?)", ("1984", "George Orwell", 1))
cur.execute("INSERT INTO livres (titre, auteur, disponible) VALUES (?, ?, ?)", ("Le Seigneur des Anneaux", "J.R.R. Tolkien", 1))
cur.execute("INSERT INTO livres (titre, auteur, disponible) VALUES (?, ?, ?)", ("L'Étranger", "Albert Camus", 0)) # Livre déjà emprunté

cur.execute("INSERT INTO clients (nom, prenom, adresse) VALUES (?, ?, ?)",('DUPONT', 'Emilie', '123, Rue des Lilas, 75001 Paris'))
cur.execute("INSERT INTO clients (nom, prenom, adresse) VALUES (?, ?, ?)",('LEROUX', 'Lucas', '456, Avenue du Soleil, 31000 Toulouse'))
cur.execute("INSERT INTO clients (nom, prenom, adresse) VALUES (?, ?, ?)",('MARTIN', 'Amandine', '789, Rue des Érables, 69002 Lyon'))
cur.execute("INSERT INTO clients (nom, prenom, adresse) VALUES (?, ?, ?)",('TREMBLAY', 'Antoine', '1010, Boulevard de la Mer, 13008 Marseille'))
cur.execute("INSERT INTO clients (nom, prenom, adresse) VALUES (?, ?, ?)",('LAMBERT', 'Sarah', '222, Avenue de la Liberté, 59000 Lille'))
cur.execute("INSERT INTO clients (nom, prenom, adresse) VALUES (?, ?, ?)",('GAGNON', 'Nicolas', '456, Boulevard des Cerisiers, 69003 Lyon'))
cur.execute("INSERT INTO clients (nom, prenom, adresse) VALUES (?, ?, ?)",('DUBOIS', 'Charlotte', '789, Rue des Roses, 13005 Marseille'))
cur.execute("INSERT INTO clients (nom, prenom, adresse) VALUES (?, ?, ?)",('LEFEVRE', 'Thomas', '333, Rue de la Paix, 75002 Paris'))

connection.commit()
connection.close()
print("Base de données mise à jour avec la table Livres !")
