import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import joblib
import numpy as np
import plotly.graph_objects as go

df = pd.read_excel("Football_data_Set.xlsx")
df.fillna(0, inplace=True)
model = joblib.load("football_match_winner_model.pkl")
label_encoders = joblib.load("label_encoders.pkl")

st.set_page_config(page_title="Football Match Predictor", layout="centered")
st.title("🏟️ Football Match Winner Predictor")
# Page Title
st.title("⚽ Football Stats Dashboard")


tab1, tab2, tab3 = st.tabs(["📊 Player vs Player", "🏆 Match Prediction", "🔥 Top Scorers & Key Players Overview"])



with tab1:
    st.header("Player Stats Comparison")

    teams = df["Team"].unique()
    team1 = st.selectbox("Select Team 1", teams)
    team2 = st.selectbox("Select Team 2", [team for team in teams if team != team1])

    positions = df["Position"].unique()
    selected_position = st.selectbox("Select Player Position", positions)

    # Player selection
    players_team1 = df[(df["Team"] == team1) & (df["Position"] == selected_position)]["Name"].unique()
    players_team2 = df[(df["Team"] == team2) & (df["Position"] == selected_position)]["Name"].unique()

    player1 = st.selectbox(f"Select Player from {team1}", players_team1)
    player2 = st.selectbox(f"Select Player from {team2}", players_team2)

    stats_to_compare = ["Goals", "Assists", "Tackle", "Saves", "Clean Sheets","Shots","Goals Conceded"]

    if st.button("Compare Players"):
        p1_stats = df[df["Name"] == player1][stats_to_compare].iloc[0]
        p2_stats = df[df["Name"] == player2][stats_to_compare].iloc[0]
        # Fetch full row for each player
        player1_row = df[df["Name"] == player1].iloc[0]
        player2_row = df[df["Name"] == player2].iloc[0]


        col1, col2 = st.columns(2)

        with col1:
                st.subheader(player1)
                photo1 = player1_row.get("Photo")
                if isinstance(photo1, str):
                    st.image(photo1 if photo1.startswith("http") else f"./{photo1}", width=150)

                # Jersey & Height below image
                Appearances1 = player1_row.get("Appearances") or player1_row.get("Appearances") or "N/A"
                jersey1 = player1_row.get("Jersey Number") or player1_row.get("Jersey") or "N/A"
                height1 = player1_row.get("Height") or player1_row.get("Height (cm)") or "N/A"
                nationality1 = player1_row.get("Nationality") or player1_row.get("Nationality") or "N/A"
                st.markdown(f"**Appearances:** {Appearances1}")
                st.markdown(f"**Jersey Number:** {jersey1}")
                st.markdown(f"**Height:** {height1} cm")
                st.markdown(f"**Nationality:** {nationality1}")

        with col2:
            st.subheader(player2)
            photo2 = player2_row.get("Photo")
            if isinstance(photo2, str):
                st.image(photo2 if photo2.startswith("http") else f"./{photo2}", width=150)


            Appearances2 = player1_row.get("Appearances") or player1_row.get("Appearances") or "N/A"
            jersey2 = player2_row.get("Jersey Number") or player2_row.get("Jersey") or "N/A"
            height2 = player2_row.get("Height") or player2_row.get("Height (cm)") or "N/A"
            nationality2 = player2_row.get("Nationality") or player2_row.get("Nationality") or "N/A"
            st.markdown(f"**Appearances:** {Appearances2}")
            st.markdown(f"**Jersey Number:** {jersey2}")
            st.markdown(f"**Height:** {height2} cm")
            st.markdown(f"**Nationality:** {nationality2}")

        values = list(p1_stats) + list(p2_stats)
        labels = [f"{stat} ({player1})" for stat in stats_to_compare] + [f"{stat} ({player2})" for stat in stats_to_compare]
        colors = plt.cm.Paired.colors[:len(values)]

        fig, ax = plt.subplots(figsize=(7, 7))
        wedges, _, autotexts = ax.pie(
            values,
            colors=colors,
            autopct=lambda pct: f'{pct:.1f}%' if pct > 0 else '',
            startangle=140,
            counterclock=False,
            textprops={'fontsize': 10}
        )

        ax.legend(wedges, labels, title="Stats", loc="center left", bbox_to_anchor=(1, 0.5), fontsize=9)
        ax.set_title(f"Stat Distribution Between {player1} and {player2}", fontsize=14)
        st.pyplot(fig)

with tab2:
    st.header("🏆 Match Predictor")

    # Load options from the label encoders
    team1_list = list(label_encoders['Team_1'].classes_)
    team2_list = list(label_encoders['Team_2'].classes_)
    place_list = list(label_encoders['Place'].classes_)

    # User inputs
    team_a = st.selectbox("Select Team A", team1_list)
    team_b = st.selectbox("Select Team B", [team for team in team2_list if team != team_a])
    season = st.text_input("Season (e.g., 2024)", "2024")
    place = st.selectbox("Match Place", place_list)

    # Prediction button
    if st.button("Predict Match Outcome"):
        # Validate season input
        if not season.isdigit():
            st.error("Season must be a numeric value.")
        else:
            try:
                season = int(season)

                # Encode user inputs
                encoded_team_a = label_encoders['Team_1'].transform([team_a])[0]
                encoded_team_b = label_encoders['Team_2'].transform([team_b])[0]
                encoded_place = label_encoders['Place'].transform([place])[0]

                # Create feature array
                features = [[encoded_team_a, encoded_team_b, season, encoded_place]]

                # Model prediction
                prediction = model.predict(features)[0]
                proba = model.predict_proba(features)[0]

                # Interpret result properly
                if prediction == 0:
                    result = "Draw"
                elif prediction == 1:
                    result = f"{team_a} Wins"
                else:
                    result = f"{team_b} Wins"

                # Display result
                st.subheader(f"🏆 Predicted Result: {result}")

                # Win probability pie chart
                fig = go.Figure(data=[go.Pie(
                    labels=[f"{team_a} Win", "Draw", f"{team_b} Win"],
                    values=[proba[1], proba[0], proba[2]],   # [Team A Win, Draw, Team B Win]
                    hole=0.4,
                    marker=dict(colors=["#1f77b4", "#2ca02c", "#d62728"]),
                    hoverinfo='label+percent'
                )])
                fig.update_layout(
                    title_text="🔮 Win Probability",
                    showlegend=True
                )
                st.plotly_chart(fig)

            except Exception as e:
                st.error(f"Prediction failed: {e}")


with tab3:
    st.header("🔥 Top Scorers & Key Players")

    st.subheader("🏅 Overall Top Scorers")

    top_scorers = df.sort_values(by="Goals", ascending=False).reset_index(drop=True).head(10)


    top_scorers.insert(0, "Rank", range(1, len(top_scorers) + 1))


    if 'Photo' in df.columns:
        def player_with_image(row):
            return f'<img src="{row["Photo"]}" width="40"/> {row["Name"]}'


        top_scorers["Player"] = top_scorers.apply(player_with_image, axis=1)
        st.markdown(
            top_scorers.to_html(escape=False, index=False, columns=["Rank", "Player", "Team", "Goals", "Assists"]),
            unsafe_allow_html=True)
    else:
        st.table(top_scorers[["Rank", "Name", "Team", "Goals", "Assists"]])

    st.markdown("---")

    # 🔍 Team-wise & Position-wise Top Players
    st.subheader("🔍 Team-wise & Position-wise Top Players")

    col1, col2 = st.columns(2)
    with col1:
        selected_team = st.selectbox("Select Team", df["Team"].unique(), key="select_team")
    with col2:
        all_positions = df["Position"].dropna().unique()
        selected_position = st.selectbox("Select Position", np.append(["All"], sorted(all_positions)),
                                         key="select_position")


    filtered_data = df[df["Team"] == selected_team]
    if selected_position != "All":
        filtered_data = filtered_data[filtered_data["Position"] == selected_position]

    if not filtered_data.empty:
        filtered_data["Total Contribution"] = filtered_data["Goals"] + filtered_data["Assists"]
        filtered_data = filtered_data.sort_values(by="Total Contribution", ascending=False).reset_index(drop=True)
        filtered_data.insert(0, "Rank", range(1, len(filtered_data) + 1))

        display_cols = ["Rank", "Name", "Position", "Goals", "Assists", "Saves"]
        st.table(filtered_data[display_cols].head(10))
    else:
        st.warning("No players found for the selected team and position.")
