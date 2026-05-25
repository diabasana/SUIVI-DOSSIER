import streamlit as st
import pandas as pd

st.set_page_config(page_title="Mon Suivi Dossier", layout="centered")

@st.cache_data
def charger_donnees():
   df_data = pd.read_excel("suivi-dosiers.xlsx", sheet_name="Donnees")
   df_users = pd.read_excel("suivi-dosiers.xlsx", sheet_name="Utilisateurs")

   # Sécurité ultime : on nettoie les noms des colonnes (majuscules et sans espaces)
   df_data.columns = df_data.columns.astype(str).str.strip().str.upper()
   df_users.columns = df_users.columns.astype(str).str.strip().str.upper()

   return df_data, df_users

try:
   df_data, df_users = charger_donnees()
except Exception as e:
   st.error(f"Erreur technique de lecture : {e}")
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

   # On vérifie si la colonne IDENTIFIANT ou IDENTIFIANTS existe pour éviter le crash
   col_client = 'IDENTIFIANT' if 'IDENTIFIANT' in df_data.columns else ('IDENTIFIANTS' if 'IDENTIFIANTS' in df_data.columns else None)

   if col_client is None:
       st.error("Désolé, la colonne avec votre Identifiant est introuvable dans l'onglet Donnees. Vérifiez son nom dans Excel.")
   else:
       df_data[col_client] = df_data[col_client].astype(str).str.strip()
       user_data = df_data[df_data[col_client] == st.session_state["user"]]

       if user_data.empty:
           st.warning("Aucune donnée disponible pour votre profil pour le moment.")
       else:
           st.subheader("📋 L'état de votre dossier")
           st.dataframe(user_data.drop(columns=[col_client]), use_container_width=True)
