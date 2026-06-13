import streamlit as st
import pandas as pd
st.set_page_config(page_title="Mon Suivi Dossier", layout="centered")
@st.cache_data
def charger_donnees():
df_data = pd.read_excel("suivi-dosiers.xlsx", sheet_name="Donnees")
df_users = pd.read_excel("suivi-dosiers.xlsx", sheet_name="Utilisateurs")
# Nettoyage automatique des noms de colonnes
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
user_row = df_users[(df_users['IDENTIFIANT'] == identifiant.strip()) &
(df_users['MOT_DE_PASS'] == mot_de_passe.strip())]
if not user_row.empty:
st.session_state["connecte"] = True
st.session_state["user"] = identifiant.strip()
st.session_state["nom"] = user_row['NOM'].values[0]
st.rerun()
else:
st.error("Identifiant ou mot de passe incorrect.")
else:
st.success(f"Bienvenue {st.session_state['nom']} 👋 ")
if st.button("Se déconnecter"):
st.session_state["connecte"] = False
st.rerun()
st.write("---")
col_client = 'IDENTIFIANT' if 'IDENTIFIANT' in df_data.columns else ('IDENTIFIANTS' if
'IDENTIFIANTS' in df_data.columns else None)
if col_client is None:
st.error("Désolé, la colonne avec l'Identifiant est introuvable dans l'onglet Donnees.")
else:
df_data[col_client] = df_data[col_client].astype(str).str.strip()
# --- MODE MASTER / ADMIN ---
# Si l'utilisateur connecté est "master", il voit TOUT
if st.session_state["user"].lower() == "master":
st.subheader("📊 Tableau de bord Master (Vue Globale)")
# Optionnel : Un petit menu pour filtrer par client si tu veux analyser un profil précis
liste_utilisateurs = ["TOUS LES CLIENTS"] + sorted(list(df_data[col_client].unique()))
choix_filtre = st.selectbox("Filtrer la vue sur un utilisateur spécifique :", liste_utilisateurs)
if choix_filtre == "TOUS LES CLIENTS":
st.dataframe(df_data, use_container_width=True)
else:
donnees_filtrees = df_data[df_data[col_client] == choix_filtre]
st.dataframe(donnees_filtrees, use_container_width=True)
# --- MODE CLIENT NORMAL ---
# Si c'est un client classique, il ne voit que ses lignes
else:
user_data = df_data[df_data[col_client] == st.session_state["user"]]
if user_data.empty:
st.warning("Aucune donnée disponible pour votre profil pour le moment.")
else:
st.subheader("📋 L'état de votre dossier")
st.dataframe(user_data.drop(columns=[col_client]), use_container_width=True)
