import json
import os
from typing import Dict, List, Any
from datetime import datetime

class DynamicKnowledgeUpdater:
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
    
    def save_dynamic_knowledge(self):
        """Save the updated dynamic knowledge graph"""
        os.makedirs(os.path.dirname(self.dynamic_knowledge_path), exist_ok=True)
        with open(self.dynamic_knowledge_path, "w", encoding="utf-8") as f:
            json.dump(self.dynamic_knowledge, f, indent=2, ensure_ascii=False)
    
    def update_character_state(self, character_name: str, user_action: str, consequences: Dict[str, Any]):
        """Update character state based on user actions"""
        characters = self.dynamic_knowledge.get("user_specific_knowledge_graph", {}).get("characters", [])
        
        for char in characters:
            if char.get("name") == character_name:
                # Update emotional state
                if "emotional_state_trends" not in char:
                    char["emotional_state_trends"] = ""
                char["emotional_state_trends"] += f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {user_action}: {consequences.get('emotional_impact', '')}"
                
                # Update character arc
                if "character_arc" not in char:
                    char["character_arc"] = ""
                char["character_arc"] += f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {user_action}: {consequences.get('arc_development', '')}"
                
                # Update items if any
                if "items" not in char:
                    char["items"] = []
                if consequences.get("items_gained"):
                    char["items"].extend(consequences["items_gained"])
                if consequences.get("items_lost"):
                    for item in consequences["items_lost"]:
                        if item in char["items"]:
                            char["items"].remove(item)
                
                break
    
    def add_story_event(self, event_description: str, impact_level: str = "medium"):
        """Add a new story event to the timeline"""
        storyline = self.dynamic_knowledge.get("user_specific_knowledge_graph", {}).get("storyline", {})
        
        if "main_events" not in storyline:
            storyline["main_events"] = []
        
        new_event = {
            "timestamp": datetime.now().isoformat(),
            "description": event_description,
            "impact_level": impact_level,
            "user_generated": True
        }
        
        storyline["main_events"].append(new_event)
    
    def update_relationships(self, character_a: str, character_b: str, relationship_change: str):
        """Update relationships between characters"""
        relationships = self.dynamic_knowledge.get("user_specific_knowledge_graph", {}).get("relationships", [])
        
        # Find existing relationship or create new one
        existing_rel = None
        for rel in relationships:
            if (rel.get("character_a") == character_a and rel.get("character_b") == character_b) or \
               (rel.get("character_a") == character_b and rel.get("character_b") == character_a):
                existing_rel = rel
                break
        
        if existing_rel:
            existing_rel["current_dynamic"] += f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {relationship_change}"
        else:
            new_relationship = {
                "character_a": character_a,
                "character_b": character_b,
                "relationship_type": "dynamic",
                "history": f"Relationship started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                "current_dynamic": relationship_change
            }
            relationships.append(new_relationship)
    
    def add_alternative_ending_branch(self, branch_description: str, conditions: List[str]):
        """Add a new alternative ending branch"""
        if "alternative_endings" not in self.dynamic_knowledge:
            self.dynamic_knowledge["alternative_endings"] = []
        
        new_branch = {
            "id": len(self.dynamic_knowledge["alternative_endings"]) + 1,
            "description": branch_description,
            "conditions": conditions,
            "created_at": datetime.now().isoformat(),
            "storyline_changes": []
        }
        
        self.dynamic_knowledge["alternative_endings"].append(new_branch)
    
    def analyze_user_response(self, user_response: str, current_character: str) -> Dict[str, Any]:
        """Analyze user response and determine consequences"""
        # This is a simplified analysis - in a real implementation, you might use AI to analyze
        consequences = {
            "emotional_impact": "",
            "arc_development": "",
            "items_gained": [],
            "items_lost": [],
            "relationship_changes": [],
            "story_direction": ""
        }
        
        # Simple keyword-based analysis
        response_lower = user_response.lower()
        
        if any(word in response_lower for word in ["fight", "attack", "confront"]):
            consequences["emotional_impact"] = "Increased tension and aggression"
            consequences["arc_development"] = "Character becomes more confrontational"
            consequences["story_direction"] = "conflict"
        
        elif any(word in response_lower for word in ["help", "save", "protect"]):
            consequences["emotional_impact"] = "Increased empathy and heroism"
            consequences["arc_development"] = "Character develops heroic traits"
            consequences["story_direction"] = "heroic"
        
        elif any(word in response_lower for word in ["run", "escape", "hide"]):
            consequences["emotional_impact"] = "Increased fear and caution"
            consequences["arc_development"] = "Character becomes more cautious"
            consequences["story_direction"] = "survival"
        
        elif any(word in response_lower for word in ["talk", "negotiate", "diplomacy"]):
            consequences["emotional_impact"] = "Increased diplomacy and wisdom"
            consequences["arc_development"] = "Character becomes more diplomatic"
            consequences["story_direction"] = "diplomatic"
        
        return consequences
    
    def update_based_on_user_response(self, user_response: str, current_character: str):
        """Main method to update dynamic knowledge based on user response"""
        # Analyze the response
        consequences = self.analyze_user_response(user_response, current_character)
        
        # Update character state
        self.update_character_state(current_character, user_response, consequences)
        
        # Add story event
        self.add_story_event(f"User action: {user_response}", "medium")
        
        # Add alternative ending branch if significant
        if consequences["story_direction"]:
            self.add_alternative_ending_branch(
                f"Story takes {consequences['story_direction']} direction",
                [f"User chose {consequences['story_direction']} path"]
            )
        
        # Save updates
        self.save_dynamic_knowledge()
        
        return consequences 