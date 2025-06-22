import os
import json
import yaml
import re
import subprocess
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from dotenv import load_dotenv
from llama_api_client import LlamaAPIClient

# Load environment variables
load_dotenv()

# Setup app
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev_secret_key")

# Setup Llama client
client = LlamaAPIClient(
    api_key=os.environ.get("LLAMA_API_KEY"),
)

# Paths
KG_PATH = "knowledge_base/world_knowledge_graph.yaml"
DYN_PATH = "knowledge_base/dynamic_world_knowledge.json"
CHAT_HISTORY_PATH = "knowledge_base/chat_history.json"

# Add this near the top with other configuration
UPLOAD_FOLDER = 'book_data'
ALLOWED_EXTENSIONS = {'txt'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    """Check if the file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_knowledge_graph():
    """Load the static knowledge graph"""
    if not os.path.exists(KG_PATH):
        return None
    
    with open(KG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def load_dynamic_world():
    """Load the dynamic world knowledge"""
    if not os.path.exists(DYN_PATH):
        return None  # Add this line
    
    with open(DYN_PATH, "r", encoding="utf-8") as f:
        return json.load(f)  # Add this line

def save_dynamic_world(dynamic_world):
    """Save the dynamic world knowledge"""
    os.makedirs(os.path.dirname(DYN_PATH), exist_ok=True)
    with open(DYN_PATH, "w", encoding="utf-8") as f:
        json.dump(dynamic_world, f, indent=2, ensure_ascii=False)  # Add this line

def save_chat_history(character, chat_history):
    """Save the chat history to a structure in the history file
    
    This saves history in a format that allows multiple conversation threads
    to be stored in the same file, organized by character.
    """
    history_data = {
        "character": character,
        "timestamp": datetime.now().isoformat(),
        "messages": chat_history
    }
    
    all_histories = []
    if os.path.exists(CHAT_HISTORY_PATH):
        with open(CHAT_HISTORY_PATH, "r", encoding="utf-8") as f:
            try:
                all_histories = json.load(f)
            except:
                all_histories = []
    
    all_histories.append(history_data)
    
    os.makedirs(os.path.dirname(CHAT_HISTORY_PATH), exist_ok=True)
    with open(CHAT_HISTORY_PATH, "w", encoding="utf-8") as f:
        json.dump(all_histories, f, indent=2, ensure_ascii=False)

def extract_world_updates(text):
    """Extract world updates from the LLM response"""
    # Look for a special format in the response that indicates world updates
    pattern = r'\[WORLD_UPDATE\](.*?)\[/WORLD_UPDATE\]'
    match = re.search(pattern, text, re.DOTALL)
    
    if match:
        update_text = match.group(1).strip()
        try:
            updates = json.loads(update_text)
            return updates
        except:
            print(f"Error parsing world updates: {update_text}")
    
    return None

@app.route('/api/chat', methods=['POST'])
def chat():
    """API endpoint for chat"""
    data = request.json
    message = data.get('message', '')
    character = data.get('character', '')
    
    # Get or initialize chat history
    if 'unified_chat_history' not in session:
        session['unified_chat_history'] = []
    
    chat_history = session['unified_chat_history']
    
    # Add user message to history
    chat_history.append({
        "sender": "user",
        "content": message,
        "timestamp": datetime.now().isoformat()
    })
    
    # Load dynamic world
    dynamic_world = load_dynamic_world()
    if not dynamic_world:
        return jsonify({"error": "Dynamic world knowledge not found"}), 400
    
    # Get character-specific conversation history
    character_chat_history = [
        msg for msg in chat_history 
        if msg.get("sender") == "user" or msg.get("character") == character
    ][-10:]  # Only use last 10 messages to avoid context length issues
    
    # Create prompt
    prompt = create_character_prompt(character, dynamic_world, character_chat_history)
    
    # Call Llama API
    try:
        completion = client.chat.completions.create(
            model="Llama-4-Maverick-17B-128E-Instruct-FP8",  # Or whichever model you're using
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ]
        )
        
        response_text = completion.completion_message.content.text
        
        # Extract world updates if any
        world_updates = extract_world_updates(response_text)
        
        # Clean response (remove the world update block)
        clean_response = re.sub(r'\[WORLD_UPDATE\].*?\[/WORLD_UPDATE\]', '', response_text, flags=re.DOTALL).strip()
        
        # Add response to chat history
        chat_history.append({
            "sender": "character",
            "character": character,
            "content": clean_response,
            "timestamp": datetime.now().isoformat()
        })
        
        # Update session
        session['unified_chat_history'] = chat_history
        
        # Update dynamic world if needed
        if world_updates:
            update_type = world_updates.get("update_type")
            
            if update_type == "item_acquired":
                char_name = world_updates.get("character")
                item = world_updates.get("item")
                
                # Find character and add item
                for char in dynamic_world["user_specific_knowledge_graph"]["characters"]:
                    if char.get("name") == char_name:
                        if "items" not in char:
                            char["items"] = []
                        if item not in char["items"]:
                            char["items"].append(item)
                        break
            
            elif update_type == "item_lost":
                char_name = world_updates.get("character")
                item = world_updates.get("item")
                
                # Find character and remove item
                for char in dynamic_world["user_specific_knowledge_graph"]["characters"]:
                    if char.get("name") == char_name:
                        if "items" in char and item in char["items"]:
                            char["items"].remove(item)
                        break
            
            elif update_type == "skill_acquired":
                char_name = world_updates.get("character")
                skill = world_updates.get("skill")
                
                # Find character and add skill
                for char in dynamic_world["user_specific_knowledge_graph"]["characters"]:
                    if char.get("name") == char_name:
                        if "skills_or_powers" not in char:
                            char["skills_or_powers"] = []
                        if skill not in char["skills_or_powers"]:
                            char["skills_or_powers"].append(skill)
                        break
            
            elif update_type == "skill_lost":
                char_name = world_updates.get("character")
                skill = world_updates.get("skill")
                
                # Find character and remove skill
                for char in dynamic_world["user_specific_knowledge_graph"]["characters"]:
                    if char.get("name") == char_name:
                        if "skills_or_powers" in char and skill in char["skills_or_powers"]:
                            char["skills_or_powers"].remove(skill)
                        break
            
            elif update_type == "location_change":
                char_name = world_updates.get("character")
                location = world_updates.get("location")
                
                # Find character and update location
                for char in dynamic_world["user_specific_knowledge_graph"]["characters"]:
                    if char.get("name") == char_name:
                        char["current_location"] = location
                        break
            
            # Save updated dynamic world
            save_dynamic_world(dynamic_world)
        
        # Save chat history to file (for persistence)
        save_chat_history_to_file(chat_history)
        
        return jsonify({
            "response": clean_response,
            "world_updated": world_updates is not None
        })
        
    except Exception as e:
        print(f"Error calling Llama API: {e}")
        return jsonify({"error": str(e)}), 500

def save_chat_history_to_file(chat_history):
    """Save the unified chat history to a file"""
    os.makedirs(os.path.dirname(CHAT_HISTORY_PATH), exist_ok=True)
    
    with open(CHAT_HISTORY_PATH, "w", encoding="utf-8") as f:
        json.dump(chat_history, f, indent=2, ensure_ascii=False)

def create_character_prompt(character, dynamic_world, chat_history):
    """Create a prompt for the character interaction"""
    # Get character details
    character_details = None
    for char in dynamic_world["user_specific_knowledge_graph"]["characters"]:
        if char.get("name") == character:
            character_details = char
            break
    
    if not character_details:
        return "Error: Character not found in knowledge graph"
    
    # Build the prompt
    prompt = f"""You are roleplaying as {character} from the story. Use the character's personality, talking style, and knowledge to respond to the user. 

CHARACTER DETAILS:
- Name: {character}
- Talking style: {character_details.get('talking_style', 'Not specified')}
- Personality traits: {', '.join(character_details.get('personality_traits', []))}
- Skills/powers: {', '.join(character_details.get('skills_or_powers', []))}
- Current items: {', '.join(character_details.get('items', []))}
- Affiliations: {', '.join(character_details.get('factions_affiliations', []))}

WORLD KNOWLEDGE:
The user is playing as {dynamic_world["user"]["character_played"]}.

IMPORTANT INSTRUCTIONS:
1. Stay in character at all times.
2. If your character wouldn't know something, don't pretend to know it.
3. When events occur that should update the world state, include a special JSON block with the appropriate update_type:
    [WORLD_UPDATE]

4. Use the user's preferred language: {dynamic_world["user"]["language"]}

CONVERSATION HISTORY:
"""
    
    # Add conversation history
    for msg in chat_history:
        sender = "User" if msg["sender"] == "user" else character
        prompt += f"{sender}: {msg['content']}\n"
    
    return prompt

@app.route('/')
def index():
    """Landing page - single chat interface for all characters"""
    dynamic_world = load_dynamic_world()
    
    if not dynamic_world:
        return render_template('setup_required.html')
    
    character_played = dynamic_world["user"]["character_played"]
    return render_template('unified_chat.html', 
                          character_played=character_played,
                          characters=dynamic_world["user_specific_knowledge_graph"]["characters"])

@app.route('/api/world', methods=['GET'])
def get_world():
    """API endpoint to get current world state"""
    dynamic_world = load_dynamic_world()
    if not dynamic_world:
        return jsonify({"error": "Dynamic world knowledge not found"}), 400
    
    return jsonify(dynamic_world)

@app.route('/api/reset', methods=['POST'])
def reset_chat():
    """Reset the chat history from session and file system"""
    # Clear session chat history
    if 'unified_chat_history' in session:
        session.pop('unified_chat_history')
    
    # Delete the chat history file if it exists
    if os.path.exists(CHAT_HISTORY_PATH):
        try:
            os.remove(CHAT_HISTORY_PATH)
        except Exception as e:
            print(f"Error removing chat history file: {e}")
    
    return jsonify({"status": "success"})

@app.route('/api/chat-history', methods=['GET'])
def get_chat_history():
    """API endpoint to get the unified chat history"""
    # Return the entire session chat history
    if 'unified_chat_history' in session:
        return jsonify({"messages": session['unified_chat_history']})
    else:
        return jsonify({"messages": []})

@app.route('/api/check-setup', methods=['GET'])
def check_setup():
    """Check if knowledge graph and character selection exists"""
    knowledge_graph_exists = os.path.exists(KG_PATH)
    character_selected = os.path.exists(DYN_PATH)
    
    selected_character = "Unknown"
    if character_selected:
        try:
            with open(DYN_PATH, 'r') as f:
                data = json.load(f)
                selected_character = data["user"]["character_played"]
        except:
            pass
    
    return jsonify({
        "knowledge_graph_exists": knowledge_graph_exists,
        "character_selected": character_selected,
        "selected_character": selected_character
    })

@app.route('/api/upload-and-generate', methods=['POST'])
def upload_and_generate():
    """Upload file and generate knowledge graph"""
    if 'bookFile' not in request.files:
        return jsonify({"success": False, "error": "No file part"}), 400
    
    file = request.files['bookFile']
    
    if file.filename == '':
        return jsonify({"success": False, "error": "No file selected"}), 400
    
    if file and allowed_file(file.filename):
        # Create upload directory if it doesn't exist
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        
        # Save the uploaded file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'harrypotter.txt')  # Use a fixed name for simplicity
        file.save(filepath)
        
        try:
            # Run the knowledge graph generation script
            # This approach uses the existing script with the uploaded file
            result = generate_knowledge_graph()
            
            if result:
                return jsonify({"success": True})
            else:
                return jsonify({"success": False, "error": "Failed to generate knowledge graph"}), 500
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500
    
    return jsonify({"success": False, "error": "Invalid file format, only .txt files are allowed"}), 400

@app.route('/api/generate-knowledge', methods=['POST'])
def generate_knowledge_api():
    """Generate knowledge graph with built-in data"""
    try:
        result = generate_knowledge_graph()
        
        if result:
            return jsonify({"success": True})
        else:
            return jsonify({"success": False, "error": "Failed to generate knowledge graph"}), 500
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/save-character', methods=['POST'])
def save_character():
    """Save character selection"""
    try:
        data = request.json
        character_name = data.get('character')
        language = data.get('language', 'English')
        
        if not character_name:
            return jsonify({"success": False, "error": "No character selected"}), 400
        
        # Load knowledge graph
        if not os.path.exists(KG_PATH):
            return jsonify({"success": False, "error": "Knowledge graph not found"}), 404
        
        with open(KG_PATH, 'r', encoding='utf-8') as f:
            kg = json.load(f)
            
        characters = kg.get("characters", [])
        if not characters:
            return jsonify({"success": False, "error": "No characters found in knowledge graph"}), 404
        
        # Find selected character
        selected = None
        for char in characters:
            if char.get('name', '') == character_name:
                selected = char
                break
        
        if not selected:
            return jsonify({"success": False, "error": f"Character '{character_name}' not found"}), 404
        
        # Create dynamic world knowledge structure (similar to choose_character.py)
        dynamic_world = {
            "user": {
                "language": language,
                "character_played": character_name
            },
            "user_specific_knowledge_graph": {
                "characters": characters,
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
        
        # Save to dynamic file
        os.makedirs(os.path.dirname(DYN_PATH), exist_ok=True)
        with open(DYN_PATH, 'w', encoding='utf-8') as f:
            json.dump(dynamic_world, f, indent=2, ensure_ascii=False)
        
        return jsonify({"success": True})
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/get-characters', methods=['GET'])
def get_characters():
    """Get characters from knowledge graph"""
    try:
        if not os.path.exists(KG_PATH):
            return jsonify({"success": False, "error": "Knowledge graph not found"}), 404
        
        with open(KG_PATH, 'r', encoding='utf-8') as f:
            kg = json.load(f)
            
        characters = kg.get("characters", [])
        if not characters:
            return jsonify({"success": False, "error": "No characters found in knowledge graph"}), 404
        
        return jsonify({"success": True, "characters": characters})
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

def generate_knowledge_graph():
    """Generate knowledge graph from the book text"""
    try:
        # Get the directory of this script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Build path to knowledge graph builder script
        script_path = os.path.join(script_dir, "knowledge_graph_builder/test_llama_api copy.py")
        
        # Run the script as a subprocess
        result = subprocess.run(['python3', script_path], capture_output=True, text=True)
        
        if result.returncode == 0:
            return True
        else:
            print(f"Error generating knowledge graph: {result.stderr}")
            return False
    except Exception as e:
        print(f"Exception during knowledge graph generation: {e}")
        return False

@app.route('/api/choose-character', methods=['POST'])
def choose_character_api():
    """Run character selection script"""
    try:
        # Make sure the knowledge graph exists first
        if not os.path.exists(KG_PATH):
            return jsonify({"success": False, "error": "Knowledge graph doesn't exist yet"}), 400
        
        # Run the character selection as a subprocess
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "choose_character.py")
        result = subprocess.run(['python3', script_path], capture_output=True, text=True)
        
        if result.returncode == 0:
            # Try to get the selected character name
            selected_character = "Unknown"
            if os.path.exists(DYN_PATH):
                with open(DYN_PATH, 'r') as f:
                    try:
                        data = json.load(f)
                        selected_character = data["user"]["character_played"]
                    except:
                        pass
            
            return jsonify({"success": True, "character": selected_character})
        else:
            return jsonify({"success": False, "error": result.stderr}), 500
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)