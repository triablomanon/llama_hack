import json
import yaml
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Paths
KG_PATH = "knowledge_base/world_knowledge_graph.yaml"
DYN_PATH = "knowledge_base/dynamic_world_knowledge.json"

def generate_character_with_api(character_name: str, world_context: dict) -> dict:
    """Generate enhanced character information using API"""
    try:
        from llama_api_client import LlamaAPIClient
        
        # Setup client
        client = LlamaAPIClient(
            api_key=os.environ.get("LLAMA_API_KEY"),
        )
        
        # Create prompt for character enhancement
        prompt = f"""
        Based on the world context provided, enhance the character "{character_name}" with detailed information.
        
        World Context:
        {json.dumps(world_context, indent=2)}
        
        Please generate a detailed character profile for "{character_name}" including:
        - Enhanced personality traits
        - Detailed backstory
        - Current motivations and goals
        - Relationships with other characters
        - Character development arc
        - Emotional state and trends
        - Signature quotes and speaking style
        
        Return the enhanced character information in JSON format.
        """
        
        # Make API call
        completion = client.chat.completions.create(
            model="Llama-4-Maverick-17B-128E-Instruct-FP8",
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ]
        )
        
        raw_response = completion.completion_message.content.text
        
        # Parse JSON response
        start = raw_response.find("{")
        end = raw_response.rfind("}")
        json_str = raw_response[start:end+1] if start != -1 and end != -1 else raw_response
        
        enhanced_character = json.loads(json_str)
        return enhanced_character
        
    except Exception as e:
        print(f"API call failed: {e}")
        print("Falling back to basic character data...")
        return None

def choose_character_and_initialize():
    """Main function to choose character and initialize dynamic knowledge"""
    # 1. Load static knowledge graph
    if not os.path.exists(KG_PATH):
        print(f"Knowledge graph file not found: {KG_PATH}")
        raise FileNotFoundError(f"Knowledge graph file not found: {KG_PATH}")

    with open(KG_PATH, "r", encoding="utf-8") as f:
        kg = yaml.safe_load(f)

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
    
    # 6. Ask if user wants to enhance character with API
    use_api = input(f"\nDo you want to enhance {selected_name} with AI-generated content? (y/n): ").strip().lower()
    
    if use_api == 'y' or use_api == 'yes':
        print(f"\n🔄 Generating enhanced character profile for {selected_name}...")
        
        # Create world context for API
        world_context = {
            "book_info": kg.get("book_info", {}),
            "characters": characters,
            "storyline": kg.get("storyline", {})
        }
        
        # Generate enhanced character
        enhanced_character = generate_character_with_api(selected_name, world_context)
        
        if enhanced_character:
            # Merge enhanced character with original
            for i, char in enumerate(characters):
                if char.get("name") == selected_name:
                    characters[i] = {**char, **enhanced_character}
                    selected = characters[i]
                    print(f"✅ {selected_name} enhanced with AI-generated content!")
                    break
        else:
            print(f"⚠️  Using original character data for {selected_name}")
    else:
        print(f"Using original character data for {selected_name}")

    # 7. Build dynamic world knowledge structure
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

    # 8. Save to dynamic file
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

