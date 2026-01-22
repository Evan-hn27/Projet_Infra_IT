from flask import Flask, render_template, jsonify, request, redirect, url_for, session
import sqlite3
from datetime import datetime, timedelta

app = Flask(__name__)                                                                                                               
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'  # Clé secrète pour les sessions

# --- CONFIGURATION BASE DE DONNÉES ---
DATABASE_CLIENTS = 'database.db'
DATABASE_LIBRARY = 'library.db'

def get_db_connection(db_name='library.db'):
    """Crée une connexion à la base de données spécifiée"""
    conn = sqlite3.connect(db_name)
    conn.row_factory = sqlite3.Row
    return conn

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
            session['authentifie_user'] = False
            session['user_id'] = 1
            session['role'] = 'admin'
            session['nom'] = 'Admin'
            return redirect(url_for('lecture'))
        
        # Cas User
        elif username == 'user' and password == '12345':
            session['authentifie_user'] = True
            session['authentifie'] = False
            session['user_id'] = 2
            session['role'] = 'user'
            session['nom'] = 'User'
            return redirect(url_for('bibliotheque'))
            
        else:
            return render_template('formulaire_authentification.html', error=True)

    return render_template('formulaire_authentification.html', error=False)

@app.route('/deconnexion')
def deconnexion():
    """Déconnexion de l'utilisateur"""
    session.clear()
    return redirect(url_for('hello_world'))

@app.route('/lecture')
def lecture():
    if not est_authentifie():
        return redirect(url_for('authentification'))
    return "<h2>Bravo, vous êtes authentifié en tant qu'Administrateur</h2><br><a href='/bibliotheque'>Accéder à la bibliothèque</a> | <a href='/admin/gestion'>Gestion Admin</a> | <a href='/deconnexion'>Déconnexion</a>"

# --- GESTION DES CLIENTS (Ancien système - Séquence 5) ---
@app.route('/fiche_nom/<nom>')
def fiche_nom(nom):
    if not est_authentifie_user():
        return "Accès refusé. Veuillez vous connecter avec le compte 'user'.", 401
    conn = sqlite3.connect(DATABASE_CLIENTS)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM clients WHERE nom = ?', (nom,))
    data = cursor.fetchall()
    conn.close()
    return render_template('read_data.html', data=data)

@app.route('/fiche_client/<int:client_id>')
def fiche_client(client_id):
    conn = sqlite3.connect(DATABASE_CLIENTS)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM clients WHERE id = ?', (client_id,))
    data = cursor.fetchall()
    conn.close()
    return render_template('read_data.html', data=data)

@app.route('/consultation/')
def ReadBDD():
    conn = sqlite3.connect(DATABASE_CLIENTS)
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
        conn = sqlite3.connect(DATABASE_CLIENTS)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO clients (created, nom, prenom, adresse) VALUES (?, ?, ?, ?)', (1002938, nom, prenom, "ICI"))
        conn.commit()
        conn.close()
        return redirect(url_for('ReadBDD'))
    return render_template('formulaire.html')

# ==================== PROJET BIBLIOTHÈQUE (Séquence 6) ====================

# --- PAGE PRINCIPALE BIBLIOTHÈQUE ---
@app.route('/bibliotheque')
def bibliotheque():
    """Page principale de la bibliothèque avec recherche et liste des livres"""
    conn = get_db_connection(DATABASE_LIBRARY)
    
    # Récupérer les livres disponibles
    livres = conn.execute('SELECT * FROM books WHERE quantite_disponible > 0 ORDER BY titre').fetchall()
    
    # Récupérer les catégories pour le filtre
    categories = conn.execute('SELECT DISTINCT categorie FROM books WHERE categorie IS NOT NULL ORDER BY categorie').fetchall()
    
    conn.close()
    
    return render_template('bibliotheque.html', 
                         livres=livres, 
                         categories=categories,
                         est_admin=est_authentifie(),
                         est_user=est_authentifie_user())

# --- RECHERCHE DE LIVRES ---
@app.route('/recherche_livres')
def recherche_livres():
    """Recherche de livres par titre, auteur ou catégorie"""
    query = request.args.get('q', '')
    categorie = request.args.get('categorie', '')
    
    conn = get_db_connection(DATABASE_LIBRARY)
    
    if categorie:
        livres = conn.execute(
            'SELECT * FROM books WHERE categorie = ? ORDER BY titre',
            (categorie,)
        ).fetchall()
    elif query:
        livres = conn.execute('''
            SELECT * FROM books 
            WHERE titre LIKE ? OR auteur LIKE ?
            ORDER BY titre
        ''', (f'%{query}%', f'%{query}%')).fetchall()
    else:
        livres = conn.execute('SELECT * FROM books ORDER BY titre').fetchall()
    
    categories = conn.execute('SELECT DISTINCT categorie FROM books WHERE categorie IS NOT NULL ORDER BY categorie').fetchall()
    conn.close()
    
    return render_template('bibliotheque.html', 
                         livres=livres, 
                         categories=categories,
                         query=query,
                         categorie_selectionnee=categorie,
                         est_admin=est_authentifie(),
                         est_user=est_authentifie_user())

# --- DÉTAILS D'UN LIVRE ---
@app.route('/livre/<int:livre_id>')
def details_livre(livre_id):
    """Affiche les détails complets d'un livre"""
    conn = get_db_connection(DATABASE_LIBRARY)
    livre = conn.execute('SELECT * FROM books WHERE id = ?', (livre_id,)).fetchone()
    
    # Récupérer l'historique des emprunts de ce livre
    emprunts = conn.execute('''
        SELECT e.*, u.nom, u.prenom
        FROM emprunts e
        JOIN users u ON e.user_id = u.id
        WHERE e.book_id = ?
        ORDER BY e.date_emprunt DESC
        LIMIT 10
    ''', (livre_id,)).fetchall()
    
    conn.close()
    
    if not livre:
        return "Livre non trouvé", 404
    
    return render_template('details_livre.html', 
                         livre=livre, 
                         emprunts=emprunts,
                         est_admin=est_authentifie())

# --- EMPRUNTER UN LIVRE ---
@app.route('/emprunter/<int:livre_id>', methods=['POST'])
def emprunter(livre_id):
    """Emprunter un livre (nécessite d'être connecté comme utilisateur)"""
    if not est_authentifie_user() and not est_authentifie():
        return redirect(url_for('authentification'))
    
    conn = get_db_connection(DATABASE_LIBRARY)
    
    # Vérifier que le livre existe et est disponible
    livre = conn.execute(
        'SELECT * FROM books WHERE id = ? AND quantite_disponible > 0',
        (livre_id,)
    ).fetchone()
    
    if not livre:
        conn.close()
        return render_template('message.html', 
                             message="Livre non disponible", 
                             type="error"), 400
    
    # Vérifier que l'utilisateur n'a pas déjà emprunté ce livre
    existing = conn.execute('''
        SELECT * FROM emprunts 
        WHERE user_id = ? AND book_id = ? AND statut = 'en_cours'
    ''', (session.get('user_id'), livre_id)).fetchone()
    
    if existing:
        conn.close()
        return render_template('message.html', 
                             message="Vous avez déjà emprunté ce livre", 
                             type="warning"), 400
    
    # Créer l'emprunt (durée: 14 jours)
    date_retour = datetime.now() + timedelta(days=14)
    
    conn.execute('''
        INSERT INTO emprunts (user_id, book_id, date_retour_prevue)
        VALUES (?, ?, ?)
    ''', (session.get('user_id'), livre_id, date_retour))
    
    # Mettre à jour le stock
    conn.execute('''
        UPDATE books SET quantite_disponible = quantite_disponible - 1
        WHERE id = ?
    ''', (livre_id,))
    
    conn.commit()
    conn.close()
    
    return render_template('message.html', 
                         message=f"Livre '{livre['titre']}' emprunté avec succès ! À retourner avant le {date_retour.strftime('%d/%m/%Y')}", 
                         type="success",
                         redirect_url=url_for('mes_emprunts'))

# --- MES EMPRUNTS ---
@app.route('/mes_emprunts')
def mes_emprunts():
    """Affiche les emprunts de l'utilisateur connecté"""
    if not est_authentifie_user() and not est_authentifie():
        return redirect(url_for('authentification'))
    
    conn = get_db_connection(DATABASE_LIBRARY)
    
    # Emprunts en cours
    emprunts_en_cours = conn.execute('''
        SELECT e.*, b.titre, b.auteur, b.isbn
        FROM emprunts e
        JOIN books b ON e.book_id = b.id
        WHERE e.user_id = ? AND e.statut = 'en_cours'
        ORDER BY e.date_retour_prevue
    ''', (session.get('user_id'),)).fetchall()
    
    # Historique
    historique = conn.execute('''
        SELECT e.*, b.titre, b.auteur
        FROM emprunts e
        JOIN books b ON e.book_id = b.id
        WHERE e.user_id = ? AND e.statut = 'termine'
        ORDER BY e.date_retour_effective DESC
        LIMIT 20
    ''', (session.get('user_id'),)).fetchall()
    
    conn.close()
    
    return render_template('mes_emprunts.html', 
                         emprunts_en_cours=emprunts_en_cours,
                         historique=historique,
                         today=datetime.now())

# --- RETOURNER UN LIVRE ---
@app.route('/retourner/<int:emprunt_id>', methods=['POST'])
def retourner(emprunt_id):
    """Retourner un livre emprunté"""
    if not est_authentifie_user() and not est_authentifie():
        return redirect(url_for('authentification'))
    
    conn = get_db_connection(DATABASE_LIBRARY)
    
    # Vérifier que l'emprunt existe et appartient à l'utilisateur (sauf admin)
    if est_authentifie():
        emprunt = conn.execute('''
            SELECT * FROM emprunts 
            WHERE id = ? AND statut = 'en_cours'
        ''', (emprunt_id,)).fetchone()
    else:
        emprunt = conn.execute('''
            SELECT * FROM emprunts 
            WHERE id = ? AND user_id = ? AND statut = 'en_cours'
        ''', (emprunt_id, session.get('user_id'))).fetchone()
    
    if not emprunt:
        conn.close()
        return render_template('message.html', 
                             message="Emprunt non trouvé", 
                             type="error"), 404
    
    # Marquer comme retourné
    conn.execute('''
        UPDATE emprunts 
        SET date_retour_effective = ?, statut = 'termine'
        WHERE id = ?
    ''', (datetime.now(), emprunt_id))
    
    # Mettre à jour le stock
    conn.execute('''
        UPDATE books SET quantite_disponible = quantite_disponible + 1
        WHERE id = ?
    ''', (emprunt['book_id'],))
    
    conn.commit()
    conn.close()
    
    return render_template('message.html', 
                         message="Livre retourné avec succès !", 
                         type="success",
                         redirect_url=url_for('mes_emprunts'))

# ==================== ADMINISTRATION (Admin uniquement) ====================

# --- PAGE GESTION ADMIN ---
@app.route('/admin/gestion')
def admin_gestion():
    """Page de gestion pour les administrateurs"""
    if not est_authentifie():
        return redirect(url_for('authentification'))
    
    conn = get_db_connection(DATABASE_LIBRARY)
    
    # Statistiques
    total_livres = conn.execute('SELECT COUNT(*) as count FROM books').fetchone()['count']
    livres_disponibles = conn.execute('SELECT COUNT(*) as count FROM books WHERE quantite_disponible > 0').fetchone()['count']
    total_users = conn.execute('SELECT COUNT(*) as count FROM users').fetchone()['count']
    emprunts_actifs = conn.execute('SELECT COUNT(*) as count FROM emprunts WHERE statut = "en_cours"').fetchone()['count']
    
    # Emprunts en retard
    today = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    emprunts_retard = conn.execute('''
        SELECT e.*, b.titre, u.nom, u.prenom, u.email
        FROM emprunts e
        JOIN books b ON e.book_id = b.id
        JOIN users u ON e.user_id = u.id
        WHERE e.statut = 'en_cours' AND e.date_retour_prevue < ?
        ORDER BY e.date_retour_prevue
    ''', (today,)).fetchall()
    
    # Livres les plus empruntés
    top_livres = conn.execute('''
        SELECT b.titre, b.auteur, COUNT(e.id) as nb_emprunts
        FROM books b
        LEFT JOIN emprunts e ON b.id = e.book_id
        GROUP BY b.id
        ORDER BY nb_emprunts DESC
        LIMIT 10
    ''').fetchall()
    
    conn.close()
    
    return render_template('admin_gestion.html',
                         total_livres=total_livres,
                         livres_disponibles=livres_disponibles,
                         total_users=total_users,
                         emprunts_actifs=emprunts_actifs,
                         emprunts_retard=emprunts_retard,
                         top_livres=top_livres)

# --- AJOUTER UN LIVRE (Admin) ---
@app.route('/admin/ajouter_livre', methods=['GET', 'POST'])
def ajouter_livre():
    """Ajouter un livre (Admin uniquement)"""
    if not est_authentifie(): 
        return redirect(url_for('authentification'))
    
    if request.method == 'POST':
        titre = request.form['titre']
        auteur = request.form['auteur']
        isbn = request.form.get('isbn', '')
        categorie = request.form.get('categorie', '')
        quantite = int(request.form.get('quantite', 1))
        
        if not titre or not auteur:
            return render_template('message.html', 
                                 message="Titre et auteur requis", 
                                 type="error"), 400
        
        conn = get_db_connection(DATABASE_LIBRARY)
        
        try:
            conn.execute('''
                INSERT INTO books (titre, auteur, isbn, categorie, quantite_totale, quantite_disponible)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (titre, auteur, isbn if isbn else None, categorie if categorie else None, quantite, quantite))
            conn.commit()
            conn.close()
            
            return render_template('message.html', 
                                 message=f"Livre '{titre}' ajouté avec succès !", 
                                 type="success",
                                 redirect_url=url_for('admin_livres'))
        except sqlite3.IntegrityError:
            conn.close()
            return render_template('message.html', 
                                 message="ISBN déjà existant", 
                                 type="error"), 400
    
    return render_template('admin_ajouter_livre.html')

# --- LISTE DES LIVRES (Admin) ---
@app.route('/admin/livres')
def admin_livres():
    """Liste complète des livres pour l'admin"""
    if not est_authentifie():
        return redirect(url_for('authentification'))
    
    conn = get_db_connection(DATABASE_LIBRARY)
    livres = conn.execute('SELECT * FROM books ORDER BY titre').fetchall()
    conn.close()
    
    return render_template('admin_livres.html', livres=livres)

# --- MODIFIER UN LIVRE (Admin) ---
@app.route('/admin/modifier_livre/<int:livre_id>', methods=['GET', 'POST'])
def modifier_livre(livre_id):
    """Modifier un livre existant"""
    if not est_authentifie():
        return redirect(url_for('authentification'))
    
    conn = get_db_connection(DATABASE_LIBRARY)
    
    if request.method == 'POST':
        quantite_totale = int(request.form['quantite_totale'])
        
        # Récupérer la quantité actuelle
        livre = conn.execute('SELECT * FROM books WHERE id = ?', (livre_id,)).fetchone()
        diff = quantite_totale - livre['quantite_totale']
        nouvelle_dispo = livre['quantite_disponible'] + diff
        
        conn.execute('''
            UPDATE books 
            SET quantite_totale = ?, quantite_disponible = ?
            WHERE id = ?
        ''', (quantite_totale, nouvelle_dispo, livre_id))
        conn.commit()
        conn.close()
        
        return render_template('message.html', 
                             message="Livre modifié avec succès", 
                             type="success",
                             redirect_url=url_for('admin_livres'))
    
    livre = conn.execute('SELECT * FROM books WHERE id = ?', (livre_id,)).fetchone()
    conn.close()
    
    if not livre:
        return "Livre non trouvé", 404
    
    return render_template('admin_modifier_livre.html', livre=livre)

# --- SUPPRIMER UN LIVRE (Admin) ---
@app.route('/admin/supprimer_livre/<int:livre_id>', methods=['POST'])
def supprimer_livre(livre_id):
    """Supprimer un livre (si non emprunté)"""
    if not est_authentifie():
        return redirect(url_for('authentification'))
    
    conn = get_db_connection(DATABASE_LIBRARY)
    
    # Vérifier qu'il n'y a pas d'emprunts en cours
    emprunts = conn.execute(
        'SELECT * FROM emprunts WHERE book_id = ? AND statut = "en_cours"',
        (livre_id,)
    ).fetchall()
    
    if emprunts:
        conn.close()
        return render_template('message.html', 
                             message="Impossible de supprimer : livre actuellement emprunté", 
                             type="error"), 400
    
    conn.execute('DELETE FROM books WHERE id = ?', (livre_id,))
    conn.commit()
    conn.close()
    
    return render_template('message.html', 
                         message="Livre supprimé avec succès", 
                         type="success",
                         redirect_url=url_for('admin_livres'))

# --- GESTION UTILISATEURS (Admin) ---
@app.route('/admin/utilisateurs')
def admin_utilisateurs():
    """Liste des utilisateurs"""
    if not est_authentifie():
        return redirect(url_for('authentification'))
    
    conn = get_db_connection(DATABASE_LIBRARY)
    utilisateurs = conn.execute('''
        SELECT u.*, 
               COUNT(CASE WHEN e.statut = 'en_cours' THEN 1 END) as emprunts_actifs
        FROM users u
        LEFT JOIN emprunts e ON u.id = e.user_id
        GROUP BY u.id
        ORDER BY u.nom
    ''').fetchall()
    conn.close()
    
    return render_template('admin_utilisateurs.html', utilisateurs=utilisateurs)

# --- TOUS LES EMPRUNTS (Admin) ---
@app.route('/admin/emprunts')
def admin_emprunts():
    """Liste de tous les emprunts"""
    if not est_authentifie():
        return redirect(url_for('authentification'))
    
    conn = get_db_connection(DATABASE_LIBRARY)
    
    emprunts = conn.execute('''
        SELECT e.*, b.titre, b.auteur, u.nom, u.prenom, u.email
        FROM emprunts e
        JOIN books b ON e.book_id = b.id
        JOIN users u ON e.user_id = u.id
        ORDER BY e.date_emprunt DESC
        LIMIT 100
    ''').fetchall()
    
    conn.close()
    
    return render_template('admin_emprunts.html', emprunts=emprunts, today=datetime.now())

# ==================== API JSON (pour tests) ====================

@app.route('/api/livres')
def api_livres():
    """API JSON : Liste des livres disponibles"""
    conn = get_db_connection(DATABASE_LIBRARY)
    livres = conn.execute('SELECT * FROM books WHERE quantite_disponible > 0').fetchall()
    conn.close()
    return jsonify([dict(livre) for livre in livres])

@app.route('/api/recherche')
def api_recherche():
    """API JSON : Recherche de livres"""
    query = request.args.get('q', '')
    conn = get_db_connection(DATABASE_LIBRARY)
    livres = conn.execute('''
        SELECT * FROM books 
        WHERE titre LIKE ? OR auteur LIKE ?
    ''', (f'%{query}%', f'%{query}%')).fetchall()
    conn.close()
    return jsonify([dict(livre) for livre in livres])

if __name__ == "__main__":
    app.run(debug=True)
