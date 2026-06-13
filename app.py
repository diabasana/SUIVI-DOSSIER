import streamlit as st
import pandas as pd

st.set_page_config(page_title="Mon Suivi Dossier", layout="wide") # Passage en mode large pour mieux voir les colonnes

# Fonction pour appliquer des couleurs différentes aux colonnes
def colorer_colonnes(df):
    styles = pd.DataFrame('', index=df.index, columns=df.columns)
    
    # On applique des couleurs de fond soft (pastels) par bloc de colonnes si elles existent
    for col in df.columns:
        if 'IDENTIFIANT' in col:
            styles[col] = 'background-color: #f1f3f5; color: #212529;' # Gris clair
        elif col in ['NOM', 'PRENOM']:
            styles[col] = 'background-color: #e7f5ff; color: #004085;' # Bleu pastel
        elif 'DATE' in col:
            styles[col] = 'background-color: #ebfbee; color: #0f5132;' # Vert pastel
        else:
            styles[col] = 'background-color: #fff9db; color: #664d03;' # Jaune/Orange pastel
            
    return styles

# Chargement direct du fichier Excel
try:
    df_data = pd.read_excel("suivi-dosiers.xlsx", sheet_name="Donnees")
    df_users = pd.read_excel("suivi-dosiers.xlsx", sheet_name="Utilisateurs")
    
    # Nettoyage des colonnes
    df_data.columns = df_data.columns.astype(str).str.strip().str.upper()
    df_users.columns = df_users.columns.astype(str).str.strip().str.upper()
    
    # Nettoyage des dates (Suppression des heures 00:00:00)
    for col in df_data.columns:
        if "DATE" in col:
            df_data[col] = pd.to_datetime(df_data[col], errors='coerce').dt.strftime('%Y-%m-%d').fillna(df_data[col])
            
except Exception as e:
    st.error(f"Erreur technique de lecture du fichier Excel : {e}")
    st.stop()

# --- ÉCRAN DE CONNEXION ---
st.title("🔐 Espace Suivi Personnel")

if "connecte" not in st.session_state:
    st.session_state["connecte"] = False
    st.session_state["user"] = ""
    st.session_state["nom"] = ""

if not st.session_state["connecte"]:
    with st.form("Login"):
        identifiant = st.text_input("Identifiant (ex: user01)")
        mot_de_passe = st.text_input("Mot de passe", type="password")
        bouton_connexion = st.form_submit_button("Se connecter")
        
        if bouton_connexion:
            df_users['IDENTIFIANT'] = df_users['IDENTIFIANT'].astype(str).str.strip()
            df_users['MOT_DE_PASS'] = df_users['MOT_DE_PASS'].astype(str).str.strip()
            
            user_row = df_users[(df_users['IDENTIFIANT'] == identifiant.strip()) & (df_users['MOT_DE_PASS'] == mot_de_passe.strip())]
            
            if not user_row.empty:
                st.session_state["connecte"] = True
                st.session_state["user"] = identifiant.strip()
                st.session_state["nom"] = user_row['NOM'].values[0]
                st.rerun()
            else:
                st.error("Identifiant ou mot de passe incorrect.")
else:
    st.success(f"Bienvenue {st.session_state['nom']} 👋")
    
    if st.button("Se déconnecter"):
        st.session_state["connecte"] = False
        st.rerun()
        
    st.write("---")
    
    col_client = 'IDENTIFIANT' if 'IDENTIFIANT' in df_data.columns else ('IDENTIFIANTS' if 'IDENTIFIANTS' in df_data.columns else None)
    
    if col_client is None:
        st.error("Désolé, la colonne avec l'Identifiant est introuvable dans l'onglet Donnees.")
    else:
        df_data[col_client] = df_data[col_client].astype(str).str.strip()
        
        # --- VUE MASTER ---
        if st.session_state["user"].lower() == "master":
            st.subheader("📊 Tableau de bord Master (Vue Globale)")
            
            liste_utilisateurs = ["TOUS LES CLIENTS"] + sorted(list(df_data[col_client].unique()))
            choix_filtre = st.selectbox("Filtrer la vue sur un utilisateur spécifique :", liste_utilisateurs)
            
            if choix_filtre == "TOUS LES CLIENTS":
                df_a_afficher = df_data
            else:
                df_a_afficher = df_data[df_data[col_client] == choix_filtre]
            
            # Application du style de couleur
            df_style = df_a_afficher.style.apply(colorer_colonnes, axis=None)
            st.dataframe(df_style, use_container_width=True)
                
        # --- VUE CLIENT NORMAL ---
        else:
            user_data = df_data[df_data[col_client] == st.session_state["user"]]
            
            if user_data.empty:
                st.warning("Aucune donnée disponible pour votre profil pour le moment.")
            else:
                st.subheader("📋 L'état de votre dossier")
                # On enlève la colonne identifiant pour le client
                df_client = user_data.drop(columns=[col_client])
                # Application du style de couleur
                df_style = df_client.style.apply(colorer_colonnes, axis=None)
                st.dataframe(df_style, use_container_width=True)
