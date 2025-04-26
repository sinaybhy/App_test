import streamlit as st
import pandas as pd
from streamlit_folium import st_folium
import folium
import os

st.title("Interface de collecte de données")

# --- 1. Upload de fichier ---
uploaded_file = st.file_uploader("Sélectionner un fichier", type=["nc"])
if uploaded_file:
    st.success(f"Fichier '{uploaded_file.name}' chargé !")

# --- 2. Carte interactive ---

# --- Initialiser la session pour stocker les points ---
if "trajet_points" not in st.session_state:
    st.session_state.trajet_points = []

# --- Mise en page : Carte à gauche, tableau à droite ---
col1, col2 = st.columns([2, 1])  # Largeur 2/3 carte, 1/3 tableau

with col1:
    st.subheader("Cliquez sur la carte pour ajouter des points")

        # Center on last point if available
    if st.session_state.trajet_points:
        last_point = st.session_state.trajet_points[-1]
        center = [last_point["lat"], last_point["lon"]]
    else:
        center = [46.603354, 1.888334]  # default: center of France

    m = folium.Map(location=center,zoom_start=4)  # Zoom in closer to last point
    m.add_child(folium.LatLngPopup())

    # Marqueurs + tracé du trajet
    for point in st.session_state.trajet_points:
        folium.Marker(location=[point["lat"], point["lon"]],
                      popup=f"{point['lat']:.4f}, {point['lon']:.4f}").add_to(m)

    if len(st.session_state.trajet_points) >= 2:
        folium.PolyLine(locations=[(p["lat"], p["lon"]) for p in st.session_state.trajet_points],
                        color="blue").add_to(m)

    # Afficher la carte et capter les clics
    map_data = st_folium(m, width=600, height=500)

    if map_data and map_data.get("last_clicked"):
        lat = map_data["last_clicked"]["lat"]
        lon = map_data["last_clicked"]["lng"]
        if not st.session_state.trajet_points or \
           (lat, lon) != (st.session_state.trajet_points[-1]["lat"], st.session_state.trajet_points[-1]["lon"]):
            st.session_state.trajet_points.append({"lat": lat, "lon": lon})
            st.rerun()
            
with col2:
     # Champ pour nom du trajet
    st.subheader("2️⃣")
    trajet_name = st.text_input("Nom du trajet")

    # Tableau des points sélectionnés
    st.subheader("3️⃣")
    if st.session_state.trajet_points:
            # Convertir en DataFrame
        df = pd.DataFrame(st.session_state.trajet_points)

        # Ajout colonne de sélection (checkbox)
        df["Supprimer"] = False
        edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)

        # Mettre à jour les points avec les valeurs éditées
        st.session_state.trajet_points = edited_df.drop(columns="Supprimer").to_dict(orient="records")

        # Supprimer les lignes sélectionnées
        if st.button("🗑️ Supprimer les lignes sélectionnées"):
            st.session_state.trajet_points = edited_df[edited_df["Supprimer"] == False].drop(columns="Supprimer").to_dict(orient="records")
            st.success("Point(s) supprimé(s)")
            st.rerun()
    else:
        st.info("Aucun point sélectionné pour l’instant")

    # Bouton d'enregistrement
    st.subheader("4️⃣")
    if st.button("💾 Enregistrer dans un CSV"):
        if not st.session_state.trajet_points:
            st.warning("Veuillez d'abord sélectionner des points sur la carte.")
        elif trajet_name.strip() == "":
            st.error("Veuillez entrer un nom de trajet.")
        else:
            df = pd.DataFrame(st.session_state.trajet_points)
            file_name = f"{trajet_name.replace(' ', '_')}.csv"
            df.to_csv(file_name, index=False)
            st.success(f"✅ Trajet '{trajet_name}' enregistré dans '{file_name}'")

# Bouton global pour réinitialiser les points
st.divider()
if st.button("🔄 Réinitialiser les points"):
    st.session_state.trajet_points = []
    st.rerun()
# --- 3. Champs d'entrée utilisateur ---
name = st.text_input("Nom du site ou de la mesure")
value = st.number_input("Valeur mesurée", step=0.1)

# --- 4. Enregistrement dans un CSV ---
if st.button("Enregistrer dans CSV"):
    if latitude is not None and longitude is not None:
        data = {
            "Nom": [name],
            "Valeur": [value],
            "Latitude": [latitude],
            "Longitude": [longitude],
        }
        df = pd.DataFrame(data)
        csv_path = "donnees_collectees.csv"

        if os.path.exists(csv_path):
            df.to_csv(csv_path, mode="a", header=False, index=False)
        else:
            df.to_csv(csv_path, index=False)
        st.success("Données enregistrées dans 'donnees_collectees.csv'")
    else:
        st.error("Veuillez sélectionner un point sur la carte.")

# --- 5. Lancer un script / une action ---
if st.button("Lancer le traitement"):
    st.info("Traitement en cours...")
    # ICI : appelle ton vrai script
    st.success("Traitement terminé !")
