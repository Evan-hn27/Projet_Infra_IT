from flask import Flask, render_template, jsonify, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)                                                                                                               
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'  # Clé secrète pour les sessions

# --- AUTHENTIFICATION ---
def est_authentifie():
    return session.get('authentifie')

def est_authentifie_user():
    return session.get('authentifie_user')

@app.route('/')
def hello_world():
    return render_template('hello.html')

@app.route('/authentification', methods=['GET', 'POST'])
def authentification():
    if request.method == 'POST':
        if request.form['username'] == 'admin' and request.form['password'] == 'password':
            session['authentifie'] = True
            return redirect(url_for('lecture'))
        elif request.form['username'] == 'user' and request.form['password'] == '12345':
            session['authentifie_user'] = True
            return redirect(url_for('ReadBDD'))
        else:
            return render_template('formulaire_authentification.html', error=True)
    return render_template('formulaire_authentification.html', error=False)

@app.route('/lecture')
def lecture():
    if not est_authentifie():
        return redirect(url_for('authentification'))
    return "<h2>Bravo, vous êtes authentifié</h2>"

# --- GESTION CLIENTS ---
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
        return redirect('/consultation/')
    return render_template('formulaire.html')

# --- GESTION BIBLIOTHÈQUE (Séquence 6) ---
@app.route('/admin/ajouter_livre', methods=['POST'])
def ajouter_livre():
    if not est_authentifie(): 
        return "Accès réservé à l'administration", 403
    titre = request.form['titre']
    auteur = request.form['auteur']
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO livres (titre, auteur, disponible) VALUES (?, ?, 1)', (titre, auteur))
    conn.commit()
    conn.close()
    return "Livre ajouté avec succès !"

@app.route('/recherche_livres')
def recherche_livres():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM livres WHERE disponible = 1')
    livres = cursor.fetchall()
    conn.close()
    return render_template('read_data.html', data=livres)

@app.route('/emprunter/<int:livre_id>')
def emprunter(livre_id):
    if not est_authentifie_user():
        return "Veuillez vous connecter", 401
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE livres SET disponible = 0 WHERE id = ? AND disponible = 1', (livre_id,))
    if cursor.rowcount == 0:
        conn.close()
        return "Livre indisponible."
    conn.commit()
    conn.close()
    return f"Livre {livre_id} emprunté !"

if __name__ == "__main__":
    app.run(debug=True)
