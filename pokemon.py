import streamlit as st
import pandas as pd

# Load the dataset (assumes it's saved as 'pokemon_data.csv')
# For deployment, place the CSV in the same directory as this script
import os

# Load CSV from the current directory (compatible with Streamlit Cloud)
import os

csv_path = os.path.join(os.path.dirname(__file__), 'pokemon_data_pokeapi.csv')
df = pd.read_csv(csv_path)


# Define Pokémon type effectiveness chart
type_effectiveness = {
    'Normal': {'weak': ['Fighting'], 'strong': [], 'immune': ['Ghost']},
    'Fighting': {'weak': ['Flying', 'Psychic', 'Fairy'], 'strong': ['Normal', 'Rock', 'Steel', 'Ice', 'Dark'],
                 'immune': []},
    'Flying': {'weak': ['Rock', 'Electric', 'Ice'], 'strong': ['Fighting', 'Bug', 'Grass'], 'immune': ['Ground']},
    'Poison': {'weak': ['Ground', 'Psychic'], 'strong': ['Grass', 'Fairy'], 'immune': []},
    'Ground': {'weak': ['Water', 'Grass', 'Ice'], 'strong': ['Poison', 'Rock', 'Steel', 'Fire', 'Electric'],
               'immune': ['Electric']},
    'Rock': {'weak': ['Fighting', 'Ground', 'Steel', 'Water', 'Grass'], 'strong': ['Flying', 'Bug', 'Fire', 'Ice'],
             'immune': []},
    'Bug': {'weak': ['Flying', 'Rock', 'Fire'], 'strong': ['Grass', 'Psychic', 'Dark'], 'immune': []},
    'Ghost': {'weak': ['Ghost', 'Dark'], 'strong': ['Ghost', 'Psychic'], 'immune': ['Normal', 'Fighting']},
    'Steel': {'weak': ['Fighting', 'Ground', 'Fire'], 'strong': ['Rock', 'Ice', 'Fairy'], 'immune': ['Poison']},
    'Fire': {'weak': ['Water', 'Rock', 'Ground'], 'strong': ['Bug', 'Steel', 'Grass', 'Ice'], 'immune': []},
    'Water': {'weak': ['Grass', 'Electric'], 'strong': ['Fire', 'Ground', 'Rock'], 'immune': []},
    'Grass': {'weak': ['Flying', 'Poison', 'Bug', 'Fire', 'Ice'], 'strong': ['Water', 'Ground', 'Rock'], 'immune': []},
    'Electric': {'weak': ['Ground'], 'strong': ['Flying', 'Water'], 'immune': []},
    'Psychic': {'weak': ['Bug', 'Ghost', 'Dark'], 'strong': ['Fighting', 'Poison'], 'immune': []},
    'Ice': {'weak': ['Fighting', 'Rock', 'Steel', 'Fire'], 'strong': ['Flying', 'Ground', 'Grass', 'Dragon'],
            'immune': []},
    'Dragon': {'weak': ['Ice', 'Dragon', 'Fairy'], 'strong': ['Dragon'], 'immune': []},
    'Dark': {'weak': ['Fighting', 'Bug', 'Fairy'], 'strong': ['Ghost', 'Psychic'], 'immune': ['Psychic']},
    'Fairy': {'weak': ['Poison', 'Steel'], 'strong': ['Fighting', 'Dragon', 'Dark'], 'immune': ['Dragon']}
}


# Function to calculate weaknesses and strengths
def get_type_matchups(type1, type2=None):
    weaknesses = set(type_effectiveness[type1]['weak'])
    strengths = set(type_effectiveness[type1]['strong'])
    immunities = set(type_effectiveness[type1]['immune'])

    if type2:
        weaknesses.update(type_effectiveness[type2]['weak'])
        strengths.update(type_effectiveness[type2]['strong'])
        immunities.update(type_effectiveness[type2]['immune'])

        # Adjust for type interactions
        weaknesses = weaknesses - immunities
        for t in type_effectiveness:
            if t in strengths and t in type_effectiveness[type1]['weak'] and t not in type_effectiveness[type2]['weak']:
                weaknesses.discard(t)
            elif t in strengths and t in type_effectiveness[type2]['weak'] and t not in type_effectiveness[type1][
                'weak']:
                weaknesses.discard(t)

    return list(weaknesses), list(strengths)


# Function to find counters
def find_counters(pokemon_name):
    pokemon = df[df['Name'].str.lower() == pokemon_name.lower()]
    if pokemon.empty:
        return "Pokémon not found."

    type1 = pokemon['Type1'].values[0]
    type2 = pokemon['Type2'].values[0] if pd.notna(pokemon['Type2'].values[0]) else None
    weaknesses, _ = get_type_matchups(type1, type2)

    # Find Pokémon strong against this one
    counters = df[df['Type1'].isin(weaknesses) | df['Type2'].isin(weaknesses)]
    return counters['Name'].head(3).tolist()


# Main prediction function
def predict_pokemon_info(pokemon_name):
    pokemon = df[df['Name'].str.lower() == pokemon_name.lower()]
    if pokemon.empty:
        return "Pokémon not found."

    type1 = pokemon['Type1'].values[0]
    type2 = pokemon['Type2'].values[0] if pd.notna(pokemon['Type2'].values[0]) else None
    weaknesses, strengths = get_type_matchups(type1, type2)
    counters = find_counters(pokemon_name)

    return {
        'Weaknesses': weaknesses,
        'Strengths': strengths,
        'Counters': counters
    }


# Streamlit app
def main():
    st.title("Pokémon Info Predictor")
    st.write("Enter a Pokémon name to discover its weaknesses, strengths, and counters!")

    # Input field for Pokémon name
    pokemon_name = st.text_input("Pokémon Name", placeholder="e.g., Charizard")

    if pokemon_name:
        result = predict_pokemon_info(pokemon_name)

        if isinstance(result, str):  # Error message
            st.error(result)
        else:
            st.subheader(f"Results for {pokemon_name}")

            # Display weaknesses
            st.write("**Weaknesses:**")
            st.write(", ".join(result['Weaknesses']) if result['Weaknesses'] else "None")

            # Display strengths
            st.write("**Strengths:**")
            st.write(", ".join(result['Strengths']) if result['Strengths'] else "None")

            # Display counters
            st.write("**Counters:**")
            st.write(", ".join(result['Counters']) if result['Counters'] else "None found")

    st.write("---")



if __name__ == "__main__":
    main()