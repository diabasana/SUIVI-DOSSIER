import streamlit as st
import pandas as pd

st.set_page_config(page_title="Mon Suivi Dossier", layout="centered")

@st.cache_data
def charger_donnees():
   # On force ici le nom exact avec un seul 's' à dosiers
   df_data = pd.read_excel("suivi-dosiers.xlsx", sheet_name="Donnees")
   df_users = pd.read_excel("suivi-dosiers.xlsx", sheet_name="Utilisateurs")
   return df_data, df_users

try:
   df_data, df_users = charger_donnees()
except Exception as e:
   # Ce message va nous afficher la VRAIE raison du bug (ex: "Worksheet Utilisateurs not found")
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
   df_data['IDENTIFIANT'] = df_data['IDENTIFIANT'].astype(str).str.strip()
   user_data = df_data[df_data['IDENTIFIANT'] == st.session_state["user"]]
   if user_data.empty:
       st.warning("Aucune donnée disponible pour votre profil pour le moment.")
   else:
       st.subheader("📋 L'état de votre dossier")
       st.dataframe(user_data.drop(columns=['IDENTIFIANT']), use_container_width=True)
