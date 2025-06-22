import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class StoryGenerator:
    def __init__(self, dynamic_knowledge_path: str = "knowledge_base/dynamic_world_knowledge.json"):
        self.dynamic_knowledge_path = dynamic_knowledge_path
        self.load_dynamic_knowledge()
    
    def load_dynamic_knowledge(self):
        """Load the current dynamic knowledge graph"""
        if os.path.exists(self.dynamic_knowledge_path):
            with open(self.dynamic_knowledge_path, "r", encoding="utf-8") as f:
                self.dynamic_knowledge = json.load(f)
        else:
            raise FileNotFoundError(f"Dynamic knowledge file not found: {self.dynamic_knowledge_path}")
    
    def generate_story_context(self, current_character: str) -> str:
        """Generate current story context based on dynamic knowledge"""
        characters = self.dynamic_knowledge.get("user_specific_knowledge_graph", {}).get("characters", [])
        storyline = self.dynamic_knowledge.get("user_specific_knowledge_graph", {}).get("storyline", {})
        
        # Find current character info
        char_info = None
        for char in characters:
            if isinstance(char, dict) and char.get("name") == current_character:
                char_info = char
                break
        
        if not char_info:
            return "Character information not found."
        
        # Build context
        context = f"You are {current_character}.\n\n"
        
        # Character background
        if char_info.get("backstory"):
            context += f"Background: {char_info['backstory']}\n\n"
        
        # Current emotional state
        if char_info.get("emotional_state_trends"):
            context += f"Recent emotional changes: {char_info['emotional_state_trends'].split('\n')[-1] if '\n' in char_info['emotional_state_trends'] else char_info['emotional_state_trends']}\n\n"
        
        # Current items
        if char_info.get("items"):
            context += f"Items you have: {', '.join(char_info['items'])}\n\n"
        
        # Recent story events
        main_events = storyline.get("main_events", [])
        if main_events:
            recent_events = main_events[-3:]  # Last 3 events
            context += "Recent events:\n"
            for event in recent_events:
                if isinstance(event, dict):
                    context += f"- {event.get('description', 'Unknown event')}\n"
                else:
                    context += f"- {str(event)}\n"
            context += "\n"
        
        # Alternative endings available
        alternative_endings = self.dynamic_knowledge.get("alternative_endings", [])
        if alternative_endings:
            context += f"Story branches available: {len(alternative_endings)}\n"
            for ending in alternative_endings[-2:]:  # Last 2 branches
                if isinstance(ending, dict):
                    context += f"- {ending.get('description', 'Unknown branch')}\n"
                else:
                    context += f"- {str(ending)}\n"
            context += "\n"
        
        return context
    
    def generate_story_segment_with_api(self, user_response: str, current_character: str, consequences: Dict[str, Any]) -> str:
        """Generate story segment using API for more creative and dynamic content"""
        try:
            from llama_api_client import LlamaAPIClient
            
            # Setup client
            client = LlamaAPIClient(
                api_key=os.environ.get("LLAMA_API_KEY"),
            )
            
            # Get current story context
            characters = self.dynamic_knowledge.get("user_specific_knowledge_graph", {}).get("characters", [])
            storyline = self.dynamic_knowledge.get("user_specific_knowledge_graph", {}).get("storyline", {})
            
            # Create prompt for story generation
            prompt = f"""
            Generate the next story segment based on the user's response and the current story context.
            
            User Response: "{user_response}"
            Current Character: {current_character}
            
            Character Information:
            {json.dumps([c for c in characters if c.get('name') == current_character], indent=2)}
            
            Consequences Analysis:
            {json.dumps(consequences, indent=2)}
            
            Current Story Context:
            {json.dumps(storyline, indent=2)}
            
            Please generate a compelling story segment that:
            1. Responds to the user's action naturally
            2. Shows the consequences of their choice
            3. Advances the story in an interesting way
            4. Maintains character consistency
            5. Creates tension or opportunity for the next choice
            
            Write in a narrative style that immerses the reader in the story.
            Keep it to 2-3 paragraphs maximum.
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
            
            story_segment = completion.completion_message.content.text
            return story_segment.strip()
            
        except Exception as e:
            print(f"API story generation failed: {e}")
            print("Falling back to template-based generation...")
            return self.generate_next_story_segment_template(user_response, current_character, consequences)

    def generate_next_story_segment_template(self, user_response: str, current_character: str, consequences: Dict[str, Any]) -> str:
        """Fallback template-based story generation when API is not available"""
        story_direction = consequences.get("story_direction", "")
        emotional_impact = consequences.get("emotional_impact", "")
        
        # Base story templates based on direction
        story_templates = {
            "conflict": [
                f"As {current_character}, your aggressive stance has consequences. The situation escalates...",
                f"Your confrontational approach changes the dynamics. Others react with {emotional_impact.lower()}...",
                f"The tension rises as you choose to fight. This path leads to new challenges..."
            ],
            "heroic": [
                f"Your heroic choice to help others inspires those around you. {emotional_impact}...",
                f"As {current_character}, your selfless act creates new opportunities and allies...",
                f"Your protective nature opens new story paths. People remember your kindness..."
            ],
            "survival": [
                f"Your cautious approach keeps you safe for now. {emotional_impact}...",
                f"As {current_character}, you choose survival over confrontation. This changes your options...",
                f"Your decision to avoid conflict has consequences. New paths emerge from your caution..."
            ],
            "diplomatic": [
                f"Your diplomatic approach creates new possibilities. {emotional_impact}...",
                f"As {current_character}, your negotiation skills open doors that force cannot...",
                f"Your wisdom in choosing dialogue over violence reveals hidden opportunities..."
            ]
        }
        
        # Select appropriate template
        if story_direction in story_templates:
            import random
            template = random.choice(story_templates[story_direction])
        else:
            template = f"As {current_character}, your response '{user_response}' changes the story in unexpected ways..."
        
        # Add dynamic elements
        characters = self.dynamic_knowledge.get("user_specific_knowledge_graph", {}).get("characters", [])
        other_characters = [c for c in characters if c.get("name") != current_character]
        
        if other_characters:
            import random
            random_char = random.choice(other_characters)
            template += f"\n\n{random_char.get('name', 'Someone')} notices your actions and reacts accordingly."
        
        return template
    
    def generate_alternative_ending_preview(self, current_character: str) -> List[Dict[str, str]]:
        """Generate previews of possible alternative endings"""
        alternative_endings = self.dynamic_knowledge.get("alternative_endings", [])
        characters = self.dynamic_knowledge.get("user_specific_knowledge_graph", {}).get("characters", [])
        
        char_info = None
        for char in characters:
            if isinstance(char, dict) and char.get("name") == current_character:
                char_info = char
                break
        
        ending_previews = []
        
        for ending in alternative_endings[-3:]:  # Last 3 alternative endings
            direction = ending.get("description", "").split()[-1] if isinstance(ending, dict) and ending.get("description") else "unknown"
            
            preview_templates = {
                "conflict": f"If you continue on this path, {current_character} will face ultimate challenges that test your resolve.",
                "heroic": f"Following this heroic path, {current_character} will become a legend remembered for generations.",
                "survival": f"On this survival path, {current_character} will discover hidden strengths and unexpected allies.",
                "diplomatic": f"Through diplomacy, {current_character} will unite factions and create lasting peace."
            }
            
            preview = preview_templates.get(direction, f"This path leads {current_character} to an unknown destiny.")
            
            ending_previews.append({
                "id": ending.get("id", 0) if isinstance(ending, dict) else 0,
                "description": ending.get("description", "") if isinstance(ending, dict) else str(ending),
                "preview": preview,
                "conditions": ending.get("conditions", []) if isinstance(ending, dict) else []
            })
        
        return ending_previews
    
    def generate_character_status_update(self, current_character: str) -> str:
        """Generate a status update for the current character"""
        characters = self.dynamic_knowledge.get("user_specific_knowledge_graph", {}).get("characters", [])
        
        char_info = None
        for char in characters:
            if isinstance(char, dict) and char.get("name") == current_character:
                char_info = char
                break
        
        if not char_info:
            return "Character status unavailable."
        
        status = f"=== {current_character} Status ===\n"
        
        # Personality traits
        if char_info.get("personality_traits"):
            status += f"Traits: {', '.join(char_info['personality_traits'])}\n"
        
        # Skills and powers
        if char_info.get("skills_or_powers"):
            status += f"Skills: {', '.join(char_info['skills_or_powers'])}\n"
        
        # Current items
        if char_info.get("items"):
            status += f"Items: {', '.join(char_info['items'])}\n"
        
        # Recent character development
        if char_info.get("character_arc"):
            recent_arc = char_info["character_arc"].split('\n')[-1] if '\n' in char_info["character_arc"] else char_info["character_arc"]
            if recent_arc:
                status += f"Recent development: {recent_arc}\n"
        
        # Emotional state
        if char_info.get("emotional_state_trends"):
            recent_emotion = char_info["emotional_state_trends"].split('\n')[-1] if '\n' in char_info["emotional_state_trends"] else char_info["emotional_state_trends"]
            if recent_emotion:
                status += f"Current emotional state: {recent_emotion}\n"
        
        return status
    
    def get_story_progress(self) -> Dict[str, Any]:
        """Get overall story progress and statistics"""
        storyline = self.dynamic_knowledge.get("user_specific_knowledge_graph", {}).get("storyline", {})
        alternative_endings = self.dynamic_knowledge.get("alternative_endings", [])
        
        main_events = storyline.get("main_events", [])
        user_generated_events = [e for e in main_events if e.get("user_generated", False)]
        
        progress = {
            "total_events": len(main_events),
            "user_generated_events": len(user_generated_events),
            "alternative_endings_available": len(alternative_endings),
            "story_complexity": len(alternative_endings) * 10,  # Simple complexity metric
            "recent_activity": len([e for e in main_events if "user_generated" in e and e["user_generated"]])
        }
        
        return progress 