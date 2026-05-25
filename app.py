import streamlit as st
import pandas as pd

# Configuration pour écran mobile
st.set_page_config(page_title="Mon Suivi Dossier", layout="centered")

# Chargement des données Excel
@st.cache_data
def charger_donnees():
   # Lit le fichier avec les nouveaux noms d'onglets propres
   df_data = pd.read_excel("suivi-dosiers.xlsx", sheet_name="Donnees")
   df_users = pd.read_excel("suivi-dosiers.xlsx", sheet_name="Utilisateurs")
   return df_data, df_users

try:
   df_data, df_users = charger_donnees()
except Exception as e:
   st.error("Erreur de lecture du fichier Excel. Vérifiez que les onglets s'appellent bien 'Donnees' et 'Utilisateurs'.")
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
           # Vérification stricte des identifiants et mots de passe
           user_row = df_users[(df_users['Identifiant'].astype(str) == identifiant) & (df_users['Mot_de_passe'].astype(str) == mot_de_passe)]

           if not user_row.empty:
               st.session_state["connecte"] = True
               st.session_state["user"] = identifiant
               st.session_state["nom"] = user_row['Nom'].values[0]
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
   user_data = df_data[df_data['Identifiant'] == st.session_state["user"]]

   if user_data.empty:
       st.warning("Aucune donnée disponible pour votre profil pour le moment.")
   else:
       st.subheader("📋 L'état de votre dossier")

       # Affichage du tableau complet de l'utilisateur (on cache juste la colonne Identifiant pour le design)
       st.dataframe(user_data.drop(columns=['Identifiant']), use_container_width=True)
