import gensim
import numpy as np
import requests
import random
import time
import sys
from scipy.spatial.distance import cosine

# API Endpoints
host = "http://172.18.4.158:8000"  # Add your server host URL
post_url = f"{host}/submit-word"
get_url = f"{host}/get-word"
status_url = f"{host}/status"

# Game Constants
NUM_ROUNDS = 5
MODEL_PATH = "GoogleNews-vectors-negative300.bin"

# Load Word2Vec Model
print("Loading Word2Vec model...")
try:
    model = gensim.models.KeyedVectors.load_word2vec_format(MODEL_PATH, binary=True)
    print("Model loaded successfully!")
except FileNotFoundError:
    print(f"Error: Word2Vec model file '{MODEL_PATH}' not found. Make sure it's in the correct location.")
    sys.exit(1)

# List of words available in the game
WORDS = [
    "Feather", "Coal", "Pebble", "Leaf", "Paper", "Rock", "Water", "Twig", "Sword", "Shield", "Gun", "Flame", "Rope",
    "Disease", "Cure", "Bacteria", "Shadow", "Light", "Virus", "Sound", "Time", "Fate", "Earthquake", "Storm",
    "Vaccine", "Logic", "Gravity", "Robots", "Stone", "Echo", "Thunder", "Karma", "Wind", "Ice", "Sandstorm",
    "Laser", "Magma", "Peace", "Explosion", "War", "Enlightenment", "Nuclear Bomb", "Volcano", "Whale", "Earth",
    "Moon", "Star", "Tsunami", "Supernova", "Antimatter", "Plague", "Rebirth", "Tectonic Shift", "Gamma-Ray Burst",
    "Human Spirit", "Apocalyptic Meteor", "Earth’s Core", "Neutron Star", "Supermassive Black Hole", "Entropy"
]

# Predefined rules (you can update this with word_beats.json logic)
BEATS_RULES = {
    "Feather": ["Wind", "Fire", "Tornado"],
    "Coal": ["Water", "Oxygen", "Ice"],
    "Pebble": ["Hammer", "Flood", "Earthquake"],
    "Leaf": ["Fire", "Drought", "Locust"],
    "Paper": ["Scissors", "Fire", "Ink"]
}

# Synonyms dictionary
SYNONYMS = {
    "Water": ["Liquid", "Aqua", "H2O", "Stream", "River"],
    "Fire": ["Flame", "Blaze", "Inferno", "Heat", "Burn"],
    "War": ["Conflict", "Battle", "Fight", "Struggle", "Combat"],
    # Add more synonyms as needed
}


def find_best_counter(system_word):
    """Finds the best word to play against the system's word."""

    # If we have a predefined rule, use it
    if system_word in BEATS_RULES:
        return random.choice(BEATS_RULES[system_word])  # Choose randomly from predefined counters

    try:
        system_vector = model[system_word]  # Get vector for system's word
    except KeyError:
        print(f"'{system_word}' not found in Word2Vec model, choosing a random word.")
        return random.choice(WORDS)  # Random fallback if the word is missing

    # Calculate cosine similarity with all words in our list
    best_word = None
    max_distance = -1  # Higher means more different (better counter)

    for word in WORDS:
        related_words = [word] + SYNONYMS.get(word, [])  # Include synonyms

        for related_word in related_words:
            try:
                word_vector = model[related_word]
                distance = cosine(system_vector, word_vector)

                if distance > max_distance:
                    max_distance = distance
                    best_word = word  # Choose the most different word

            except KeyError:
                continue  # Skip missing words

    return best_word if best_word else random.choice(WORDS)  # Fallback to random word


def play_game(player_id):
    """Main game loop that plays the game using API requests."""

    for round_id in range(1, NUM_ROUNDS + 1):
        round_num = -1

        # Wait for the correct round to start
        while round_num != round_id:
            response = requests.get(get_url)
            data = response.json()
            print(data)

            sys_word = data.get("word")
            round_num = data.get("round")

            time.sleep(1)  # Small delay before retrying

        if round_id > 1:
            status = requests.get(status_url)
            print(status.json())  # Show previous round results

        # Choose the best counter-word
        chosen_word = find_best_counter(sys_word)

        print({chosen_word})
        # Submit the chosen word
        data = {"player_id": player_id, "word_id": chosen_word, "round_id": round_id}
        response = requests.post(post_url, json=data)
        print(response.json())  # Show submission result
