import streamlit as st
import pandas as pd

# Configuration pour écran mobile
st.set_page_config(page_title="Mon Suivi Dossier", layout="centered")

# Chargement des données Excel
@st.cache_data
def charger_donnees():
   # header=3 permet de sauter les lignes vides pour démarrer exactement à la ligne 4 de ton Excel
   df_data = pd.read_excel("suivi-dosiers.xlsx", sheet_name="Donnees", header=3)
   df_users = pd.read_excel("suivi-dosiers.xlsx", sheet_name="Utilisateurs", header=3)
   return df_data, df_users

try:
   df_data, df_users = charger_donnees()
except Exception as e:
   st.error("Erreur de lecture du fichier Excel. Vérifiez les colonnes.")
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
           # Nettoyage des espaces pour éviter les erreurs de frappe
           df_users['IDENTIFIANT'] = df_users['IDENTIFIANT'].astype(str).str.strip()
           df_users['MOT_DE_PASS'] = df_users['MOT_DE_PASS'].astype(str).str.strip()

           # Vérification stricte des identifiants et mots de passe (en MAJUSCULES comme sur ta photo)
           user_row = df_users[(df_users['IDENTIFIANT'] == identifiant.strip()) & (df_users['MOT_DE_PASS'] == mot_de_passe.strip())]

           if not user_row.empty:
               st.session_state["connecte"] = True
               st.session_state["user"] = identifiant.strip()
               st.session_state["nom"] = user_row['NOM'].values[0]
               st.rerun()
           else:
               st.error("Identifiant ou mot de passe incorrect.")

# --- ÉCRAN CLIENT (Une fois connecté) ---
else:
   st.success(f"Bienvenue {st.session_state['nom']} 👋")

   if st.button("Se déconnecter"):
       st.session_state["connecte"] = False
       st.rerun()

   st.write("---")

   # Filtrer les données : l'utilisateur ne voit QUE ses lignes
   df_data['IDENTIFIANT'] = df_data['IDENTIFIANT'].astype(str).str.strip()
   user_data = df_data[df_data['IDENTIFIANT'] == st.session_state["user"]]

   if user_data.empty:
       st.warning("Aucune donnée disponible pour votre profil pour le moment.")
   else:
       st.subheader("📋 L'état de votre dossier")

       # Affichage du tableau complet de l'utilisateur (on cache juste la colonne IDENTIFIANT pour le design)
       st.dataframe(user_data.drop(columns=['IDENTIFIANT']), use_container_width=True)
