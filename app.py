import streamlit as st
import pandas as pd

# Configuration pour écran mobile
st.set_page_config(page_title="Mon Suivi", layout="centered")

# Chargement des données Excel (remplacez par le nom de votre fichier)
# Pour le test local, le fichier Excel doit être dans le même dossier
@st.cache_data
def charger_donnees():
   df_data = pd.read_excel("suivi_progression.xlsx", sheet_name="Donnees")
   df_users = pd.read_excel("suivi_progression.xlsx", sheet_name="Utilisateurs")
   return df_data, df_users

try:
   df_data, df_users = charger_donnees()
except Exception as e:
   st.error("Erreur de chargement du fichier Excel. Vérifiez le nom et les onglets.")
   st.stop()

# --- ÉCRAN DE CONNEXION ---
st.title("🔐 Espace Suivi Personnel")

if "connecte" not in st.session_state:
   st.session_state["connecte"] = False
   st.session_state["user"] = ""

if not st.session_state["connecte"]:
   with st.form("Login"):
       identifiant = st.text_input("Identifiant")
       mot_de_passe = st.text_input("Mot de passe", type="password")
       bouton_connexion = st.form_submit_button("Se connecter")

       if bouton_connexion:
           # Vérification dans le fichier Excel
           user_row = df_users[(df_users['Identifiant'] == identifiant) & (df_users['Mot_de_passe'].astype(str) == mot_de_passe)]

           if not user_row.empty:
               st.session_state["connecte"] = True
               st.session_state["user"] = identifiant
               st.session_state["nom"] = user_row.__getattr__('Nom').values[0]
               st.rerun()
           else:
               st.error("Identifiant ou mot de passe incorrect.")

# --- ÉCRAN CLIENT (Une fois connecté) ---
else:
   st.success(f"Bienvenue {st.session_state['nom']} 👋")

   # Déconnexion
   if st.button("Se déconnecter"):
       st.session_state["connecte"] = False
       st.rerun()

   st.write("---")

   # Filtrer les données UNIQUEMENT pour cet utilisateur
   user_data = df_data[df_data['Identifiant'] == st.session_state["user"]]

   if user_data.empty:
       st.warning("Aucune donnée disponible pour votre profil pour le moment.")
   else:
       # 1. Graphique de progression personnalisé
       st.subheader("📈 Votre graphique de progression")
       # On utilise le 'Mois' comme axe X et la 'Progression' comme courbe
       chart_data = user_data[['Mois', 'Progression']].set_index('Mois')
       st.line_chart(chart_data)

       # 2. Tableau de chiffres textuels
       st.subheader("📋 Vos données détaillées")
       # Masquer la colonne Identifiant pour que le rendu soit plus propre
       st.dataframe(user_data.drop(columns=['Identifiant']), use_container_width=True)
