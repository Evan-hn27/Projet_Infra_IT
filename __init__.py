from flask import Flask, render_template, jsonify, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)                                                                                                               
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'  # Clé secrète pour les sessions

# --- FONCTIONS D'AUTHENTIFICATION ---
def est_authentifie():
    """Vérifie si l'administrateur est connecté"""
    return session.get('authentifie')

def est_authentifie_user():
    """Vérifie si l'utilisateur standard est connecté"""
    return session.get('authentifie_user')

# --- ROUTES D'ACCUEIL ET CONNEXION ---
@app.route('/')
def hello_world():
    return render_template('hello.html')

@app.route('/authentification', methods=['GET', 'POST'])
def authentification():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Cas Admin
        if username == 'admin' and password == 'password':
            session['authentifie'] = True
            session['authentifie_user'] = False # On reset l'autre mode
            return redirect(url_for('lecture'))
        
        # Cas User (Séquence 5)
        elif username == 'user' and password == '12345':
            session['authentifie_user'] = True
            session['authentifie'] = False # On reset l'admin
            return redirect(url_for('recherche_livres'))
            
        else:
            return render_template('formulaire_authentification.html', error=True)

    return render_template('formulaire_authentification.html', error=False)

@app.route('/lecture')
def lecture():
    if not est_authentifie():
        return redirect(url_for('authentification'))
    return "<h2>Bravo, vous êtes authentifié en tant qu'Administrateur</h2>"

# --- GESTION DES CLIENTS (Séquence 5) ---
@app.route('/fiche_nom/<nom>')
def fiche_nom(nom):
    if not est_authentifie_user():
        return "Accès refusé. Veuillez vous connecter avec le compte 'user'.", 401
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM clients WHERE nom = ?', (nom,))
    data = cursor.fetchall()
    conn.close()
    return render_template('read_data.html', data=data)

@app.route('/consultation/')
def ReadBDD():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM clients;')
    data = cursor.fetchall()
    conn.close()
    return render_template('read_data.html', data=data)

@app.route('/enregistrer_client', methods=['GET', 'POST'])
def enregistrer_client():
    if request.method == 'POST':
        nom = request.form['nom']
        prenom = request.form['prenom']
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO clients (created, nom, prenom, adresse) VALUES (?, ?, ?, ?)', (1002938, nom, prenom, "ICI"))
        conn.commit()
        conn.close()
        return redirect(url_for('ReadBDD'))
    return render_template('formulaire.html')

# --- PROJET BIBLIOTHÈQUE (Séquence 6) ---

@app.route('/recherche_livres')
def recherche_livres():
    """Affiche la page de la bibliothèque avec le tableau des livres dispos"""
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM livres WHERE disponible = 1')
    livres = cursor.fetchall()
    conn.close()
    # Utilise le template bibliotheque.html créé précédemment
    return render_template('bibliotheque.html', data=livres)

@app.route('/admin/ajouter_livre', methods=['POST'])
def ajouter_livre():
    """Ajoute un livre et redirige vers la liste"""
    if not est_authentifie(): 
        return "Accès réservé à l'administration", 403
    
    titre = request.form['titre']
    auteur = request.form['auteur']
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO livres (titre, auteur, disponible) VALUES (?, ?, 1)', (titre, auteur))
    conn.commit()
    conn.close()
    return redirect(url_for('recherche_livres'))

@app.route('/emprunter/<int:livre_id>')
def emprunter(livre_id):
    """Marque un livre comme emprunté et redirige vers la liste"""
    if not est_authentifie_user():
        return "Veuillez vous connecter en tant qu'utilisateur pour emprunter", 401
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    # On met à jour la disponibilité
    cursor.execute('UPDATE livres SET disponible = 0 WHERE id = ? AND disponible = 1', (livre_id,))
    
    conn.commit()
    conn.close()
    return redirect(url_for('recherche_livres'))

if __name__ == "__main__":
    app.run(debug=True)
