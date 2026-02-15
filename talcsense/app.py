import streamlit as st
import pandas as pd
import plotly.express as px
import streamlit.components.v1 as components
import os

# Configuration de la page
st.set_page_config(page_title="TalcSense", page_icon="💄", layout="wide")

# Style CSS 
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
    h1 { color: #ff4b4b; font-family: 'Segoe UI', sans-serif; }
    </style>
    """, unsafe_allow_html=True)

# --- CHARGEMENT SÉCURISÉ ---
url = "https://raw.githubusercontent.com/gevargas/predcompact/main/375_cosmetikwatch_19_08_2025.xlsx"

@st.cache_data
def load_data():
    data = pd.read_excel(url)
    # Nettoyage profond des noms de colonnes
    data.columns = [str(c).strip() for c in data.columns]
    return data

try:
    df = load_data()
    
    # Titre principal
    st.title("💄 TalcSense : Analyse du Talc")
    
    # --- KPI : LES CHIFFRES CLÉS ---
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Produits Analysés", len(df))
    # On utilise la position de la colonne pour éviter les erreurs de noms
    c2.metric("Marques", df.iloc[:, 1].nunique()) 
    c3.metric("Précision IA", "88%")
    c4.metric("Concepts INCI", "1 182")

    st.divider()

    # --- ANALYSE VISUELLE ---
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("📊 Répartition par Catégorie")
        # Sélection automatique de la colonne Catégorie par position (souvent la 4ème)
        cat_col = df.columns[3] 
        counts = df[cat_col].value_counts()
        # On ne garde que le top pour éviter l'effet "rayures" illisible (image 9)
        df_pie = df[df[cat_col].isin(counts.head(10).index)]
        fig_pie = px.pie(df_pie, names=cat_col, hole=0.5, color_discrete_sequence=px.colors.sequential.RdBu)
        fig_pie.update_layout(showlegend=True)
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_right:
        st.subheader("🏆 Top 10 des Marques")
        brand_col = df.columns[1]
        top_m = df[brand_col].value_counts().head(10).reset_index()
        fig_bar = px.bar(top_m, x=top_m.columns[1], y=top_m.columns[0], orientation='h', 
                         color=top_m.columns[1], color_continuous_scale='Reds')
        fig_bar.update_layout(yaxis={'categoryorder':'total ascending'}, showlegend=False)
        st.plotly_chart(fig_bar, use_container_width=True)

    st.divider()

    # --- LE RÉSEAU INTERACTIF (PHASE 3.7) ---
    st.header("🧬 Réseau des Ingrédients (Standardisation)")
    st.info("Ce graphe illustre le regroupement des variantes INCI en concepts standards.")
    
    # Vérification du fichier sur GitHub
    if os.path.exists("graphe_inci.html"):
        with open("graphe_inci.html", 'r', encoding='utf-8') as f:
            html_data = f.read()
        components.html(html_data, height=800, scrolling=True)
    else:
        st.error("⚠️ Fichier 'graphe_inci.html' manquant sur GitHub. Merci de l'ajouter pour activer cette vue.")

    # --- EXPLORATEUR ---
    st.header("🔍 Explorateur de Formulations")
    st.dataframe(df.iloc[:, [2, 1, 13]], use_container_width=True)

except Exception as e:
    st.error(f"Une erreur système est survenue : {e}")
