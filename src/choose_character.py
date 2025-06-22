import json
import os

# Paths
KG_PATH = "knowledge_base/world_knowledge_graph.json"
DYN_PATH = "knowledge_base/dynamic_world_knowledge.json"

def choose_character_and_initialize():
    """Main function to choose character and initialize dynamic knowledge"""
    # 1. Load static knowledge graph
    if not os.path.exists(KG_PATH):
        print(f"Knowledge graph file not found: {KG_PATH}")
        raise FileNotFoundError(f"Knowledge graph file not found: {KG_PATH}")

    with open(KG_PATH, "r", encoding="utf-8") as f:
        kg = json.load(f)

    # 2. Gather character list
    characters = kg.get("characters", [])
    if not characters:
        print("No characters found in the knowledge graph.")
        raise ValueError("No characters found in the knowledge graph.")

    # 3. Prompt for user language
    user_language = input("What language do you want to play in? (default: English): ").strip()
    if not user_language:
        user_language = "English"

    # 4. Show character choices
    print("\nAvailable characters:")
    for idx, char in enumerate(characters, start=1):
        print(f"{idx}. {char.get('name', f'Unnamed_{idx}')}")

    # 5. Prompt for character selection
    selected = None
    while not selected:
        choice = input("\nType the number or name of the character you want to play: ").strip()
        # Number?
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(characters):
                selected = characters[idx]
        else:
            # Name (case-insensitive)
            for char in characters:
                if char.get("name", "").lower() == choice.lower():
                    selected = char
                    break
        if not selected:
            print("Invalid choice. Try again.")

    selected_name = selected.get("name", "Unknown")

    # 6. Build dynamic world knowledge structure
    dynamic_world = {
        "user": {
            "language": user_language,
            "character_played": selected_name
        },
        "user_specific_knowledge_graph": {
            "characters": characters,  # full or could be filtered if you want
            "relationships": kg.get("relationships", []),
            "skills_or_powers": [
                c.get("skills_or_powers", []) for c in characters
            ],
            "items": [
                c.get("items", []) for c in characters
            ],
            "factions_affiliations": [
                c.get("factions_affiliations", []) for c in characters
            ],
            "character_arcs": [
                c.get("character_arc", "") for c in characters
            ],
            "emotional_state_trends": [
                c.get("emotional_state_trends", "") for c in characters
            ],
            "storyline": kg.get("storyline", {}),
            "main_events": kg.get("storyline", {}).get("main_events", []),
            "locations": kg.get("storyline", {}).get("locations", []),
            "conflict_points": kg.get("storyline", {}).get("conflict_points", []),
            "timeline": kg.get("storyline", {}).get("timeline", []),
            "foreshadowing_elements": kg.get("storyline", {}).get("foreshadowing_elements", []),
            "recurring_motifs_symbols": kg.get("storyline", {}).get("recurring_motifs_symbols", []),
            "narrative_tension_points": kg.get("storyline", {}).get("narrative_tension_points", []),
            "parallel_storylines": kg.get("storyline", {}).get("parallel_storylines", []),
        }
    }

    # 7. Save to dynamic file
    os.makedirs(os.path.dirname(DYN_PATH), exist_ok=True)
    with open(DYN_PATH, "w", encoding="utf-8") as f:
        json.dump(dynamic_world, f, indent=2, ensure_ascii=False)

    print(f"\nDynamic world knowledge created for user. File: {DYN_PATH}")
    print(f"Playing as: {selected_name}, Language: {user_language}")
    
    return selected_name, user_language

def main():
    """Main function when run directly"""
    try:
        character_name, user_language = choose_character_and_initialize()
        print(f"\n✅ Setup complete! You can now run the interactive story:")
        print(f"   python src/interactive_story.py")
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    return 0

if __name__ == "__main__":
    exit(main())

