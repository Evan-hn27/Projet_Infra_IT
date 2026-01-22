import sqlite3
from datetime import datetime

# Connexion à la base de données existante
conn = sqlite3.connect('library.db')
cursor = conn.cursor()

# Table des tâches
cursor.execute('''
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titre TEXT NOT NULL,
    description TEXT,
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_echeance DATE,
    terminee INTEGER DEFAULT 0,
    user_id INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
)
''')

# Insertion de tâches de test pour l'utilisateur ID 2 (user)
taches_test = [
    ('Finaliser le projet bibliothèque', 'Compléter toutes les fonctionnalités de la séquence 6', '2026-01-30', 0, 2),
    ('Réviser pour l\'examen', 'Revoir les chapitres 1 à 5 du cours de base de données', '2026-01-25', 0, 2),
    ('Préparer la présentation', 'Créer les slides pour la soutenance du projet', '2026-02-05', 0, 2),
    ('Rapport de stage', 'Rédiger le rapport de stage', '2026-02-15', 0, 2),
    ('Faire les courses', 'Acheter les ingrédients pour la semaine', '2026-01-23', 1, 2),
]

for tache in taches_test:
    cursor.execute('''
    INSERT OR IGNORE INTO tasks (titre, description, date_echeance, terminee, user_id)
    VALUES (?, ?, ?, ?, ?)
    ''', tache)

# Tâches de test pour l'admin (ID 1)
taches_admin = [
    ('Gérer les emprunts en retard', 'Contacter les utilisateurs avec des livres en retard', '2026-01-24', 0, 1),
    ('Inventaire annuel', 'Faire l\'inventaire complet de la bibliothèque', '2026-01-31', 0, 1),
    ('Commander nouveaux livres', 'Passer commande des livres demandés par les utilisateurs', '2026-01-28', 1, 1),
]

for tache in taches_admin:
    cursor.execute('''
    INSERT OR IGNORE INTO tasks (titre, description, date_echeance, terminee, user_id)
    VALUES (?, ?, ?, ?, ?)
    ''', tache)

conn.commit()
conn.close()

print("✅ Table 'tasks' créée avec succès dans library.db!")
print(f"📝 {len(taches_test)} tâches ajoutées pour l'utilisateur")
print(f"📝 {len(taches_admin)} tâches ajoutées pour l'admin")
print("🔗 Les tâches sont liées aux utilisateurs existants")
