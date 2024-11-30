import streamlit as st
import pandas as pd
import plotly.express as px
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from PIL import Image
import io

# Ajouter une image en haut, autour du thème "Analyse PME"
st.image("https://plus.unsplash.com/premium_vector-1725721898452-b13b7b01cd36?q=80&w=1170&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D", use_container_width=True)

# Titre de l'application
st.title("Diagnostic Automatisé pour PME")

# Couleur de fond en utilisant st.markdown pour une section
page_bg_img = '''
<style>
[data-testid="stMain"] {
background-color: #21cbe1; /* Couleur de fond */
}
</style>
'''

st.markdown(page_bg_img, unsafe_allow_html=True)

# Décrire le format du fichier CSV attendu
st.markdown("""
### Description du fichier CSV à fournir :
Le fichier CSV doit contenir les colonnes suivantes :
- **Magasin** : Le nom du magasin ou de l'entité commerciale (Ex : "Énergie Verte Nord").
- **Produit** : Le produit vendu (Ex : "Panneaux solaires").
- **Revenu** : Le revenu généré par ce produit (en euros).
- **Coût** : Le coût associé à la vente du produit (en euros).
- **Clients** : Le nombre de clients ou ventes réalisées.
- **Avis** : La note moyenne des avis clients (entre 1 et 5).

#### Exemple de format CSV :
| Magasin          | Produit            | Revenu | Coût | Clients | Avis |
|------------------|--------------------|--------|------|---------|------|
| Énergie Verte Nord | Panneaux solaires  | 15000  | 8000 | 120     | 4.5  |
| ÉcoSolaires Sud  | Batteries de stockage | 20000  | 12000| 150     | 4.8  |
""")

# Bouton de téléchargement de l'exemple Excel vierge
st.markdown("""
### Exemple de fichier Excel vierge
Téléchargez un modèle vierge de fichier Excel que vous pourrez remplir :
""")
empty_excel = pd.DataFrame(columns=["Magasin", "Produit", "Revenu", "Coût", "Clients", "Avis"])

# Utilisation de BytesIO pour générer un fichier Excel binaire
excel_file = io.BytesIO()
with pd.ExcelWriter(excel_file, engine='xlsxwriter') as writer:
    empty_excel.to_excel(writer, index=False, sheet_name="Données")
excel_file.seek(0)

st.download_button(
    label="Télécharger l'exemple Excel vierge",
    data=excel_file,
    file_name="exemple_pme.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# Sidebar pour uploader un fichier CSV ou Excel
st.sidebar.header("Fichiers CSV ou Excel")
uploaded_file = st.sidebar.file_uploader("Chargez vos données (CSV ou Excel)", type=["csv", "xlsx"])

# Fonction pour générer un graphique et l'enregistrer en tant qu'image
def generate_chart(df):
    # Créer le graphique
    fig = px.bar(df, x="Produit", y="Revenu", title="Revenu par produit")

    # Personnalisation du titre et des axes
    fig.update_layout(
        title={
            'text': "Revenu par produit",  # Titre du graphique
            'font': {'size': 18, 'color': 'blue'},  # Couleur du titre
            'x': 0.5,  # Centrer le titre
        },
        xaxis_title=None,  # Supprimer le titre de l'axe X
        yaxis_title=None,  # Supprimer le titre de l'axe Y
        xaxis=dict(
            tickangle=45,  # Rotation des étiquettes de l'axe X (pour améliorer la lisibilité)
            tickfont=dict(size=10, color='green'),
            tickmode='array',  # Utiliser un mode d'étiquetage personnalisé
            tickvals=df['Produit'],  # Utiliser les valeurs de produit comme étiquettes
        ),
        yaxis=dict(
            tickfont=dict(size=12, color='red')  # Changer la couleur et la taille des étiquettes de l'axe Y
        ),
        showlegend=False,
        margin={"l": 50, "r": 50, "t": 50, "b": 150}  # Désactiver la légende si elle existe
    )

    # Spécifiez le chemin du fichier où l'image sera sauvegardée
    chart_image_path = "chart.png"
    
    # Sauvegarder l'image du graphique
    fig.write_image(chart_image_path)

    return chart_image_path

# Fonction pour générer un PDF
def generate_pdf(dataframe, kpi_data, recommendations, chart_image):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4  # Taille de la page A4 (210 mm x 297 mm)
    
    # Position de départ
    y_position = height - 40  # Position initiale pour le titre
    

    # Titre du PDF
    c.setFont("Helvetica-Bold", 16)
    c.setFillColor(colors.HexColor("#1E90FF"))  # Bleu pour le titre
    c.drawCentredString(width / 2, y_position, "Diagnostic PME - Rapport d'Analyse")
    y_position -= 40  # Réduire la position après le titre
    
    # Indicateurs clés (KPI)
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(colors.HexColor("#FF6347"))  # Rouge pour les titres
    c.drawString(30, y_position, "Indicateurs clés")
    y_position -= 40
    
    # Revenu Total
    c.setFont("Helvetica", 12)
    c.setFillColor(colors.black)
    c.drawString(30, y_position, f"Revenu total : {kpi_data['total_revenue']} €")
    y_position -= 20
    
    # Coût Total
    c.drawString(30, y_position, f"Coût total : {kpi_data['total_cost']} €")
    y_position -= 20
    
    # Marge
    c.drawString(30, y_position, f"Marge brute : {kpi_data['margin_percentage']} %")
    y_position -= 20
    
    # Avis Moyens
    c.drawString(30, y_position, f"Avis moyen des clients : {kpi_data['avg_rating']} / 5")
    y_position -= 380 # Espacer un peu avant le graphique
    
    
    
    # Ajouter le graphique dans le PDF
    c.drawImage(chart_image, 30, y_position, width=550, height=300)
    y_position -= 80  # Réduire la position après le graphique
    
    # Recommandations
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(colors.HexColor("#FF6347"))  # Rouge pour les titres
    c.drawString(30, y_position, "Recommandations")
    y_position -= 40
    
    # Ajouter les recommandations
    for recommendation in recommendations:
        c.setFont("Helvetica", 12)
        c.setFillColor(colors.black)  # Retour au noir pour les valeurs
        c.drawString(30, y_position, recommendation)
        y_position -= 80
    
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(colors.HexColor("#1E90FF"))  # Rouge pour les titres
    c.drawString(460, y_position, "Fait par HP-Data")
    
    
    # Sauvegarder le PDF
    c.showPage()  # Toujours assurer de finir avec une page complète
    c.save()
    
    buffer.seek(0)
    return buffer




if uploaded_file:
    try:
        # Charger les données
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        st.write("### Aperçu des données")
        st.dataframe(df)

        # Calcul des KPI
        total_revenue = df["Revenu"].sum()
        total_cost = df["Coût"].sum()
        margin = total_revenue - total_cost
        margin_percentage = (margin / total_revenue) * 100
        avg_rating = df["Avis"].mean()

        kpi_data = {
            "total_revenue": total_revenue,
            "total_cost": total_cost,
            "margin_percentage": margin_percentage,
            "avg_rating": avg_rating
        }

        st.write("### Indicateurs clés")
        st.metric("Revenu total", f"{total_revenue} €")
        st.metric("Coût total", f"{total_cost} €")
        st.metric("Marge brute", f"{margin_percentage:.2f} %")
        st.metric("Note moyenne des avis", f"{avg_rating:.1f} / 5")

        # Graphique des revenus par produit
        st.write("### Revenu par produit")
        fig = px.bar(df, x="Produit", y="Revenu", title="Revenu par produit")
        st.plotly_chart(fig)
        

        # Recommandations
        recommendations = []
        if margin_percentage < 20:
            recommendations.append("Votre marge est faible. Envisagez de réduire les coûts ou d'augmenter les prix.")
        if avg_rating < 4:
            recommendations.append("Les avis clients sont faibles. Travaillez sur la qualité ou le service client.")

        st.write("### Recommandations")
        for rec in recommendations:
            st.warning(rec)

        # Générer le PDF et fournir un bouton de téléchargement
        chart_image_path = generate_chart(df)
        pdf_data = generate_pdf(df, kpi_data, recommendations, chart_image_path)
        st.download_button(
            label="Télécharger le rapport en PDF",
            data=pdf_data,
            file_name="rapport_pme.pdf",
            mime="application/pdf"
        )
        
    except Exception as e:
        st.error(f"Erreur lors du chargement du fichier : {e}")
else:
    st.info("Veuillez charger un fichier pour commencer.")

# Ajouter votre nom en bas de la page
st.markdown("""
    <footer>
        <p>Hadrien Poinseaux</p>
    </footer>
""", unsafe_allow_html=True)
