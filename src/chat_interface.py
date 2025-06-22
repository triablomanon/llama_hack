import json
import os
from typing import Dict, List, Any, Optional
from .dynamic_updater import DynamicKnowledgeUpdater
from .story_generator import StoryGenerator

class ChatInterface:
    def __init__(self, dynamic_knowledge_path: str = "knowledge_base/dynamic_world_knowledge.json"):
        self.dynamic_knowledge_path = dynamic_knowledge_path
        self.updater = DynamicKnowledgeUpdater(dynamic_knowledge_path)
        self.generator = StoryGenerator(dynamic_knowledge_path)
        self.current_character = None
        self.conversation_history = []
        self.story_progress = 0
        
    def initialize_chat(self, character_name: str):
        """Initialize the chat session with a selected character"""
        self.current_character = character_name
        self.conversation_history = []
        self.story_progress = 0
        
        # Generate initial story context
        initial_context = self.generator.generate_story_context(character_name)
        
        # Create welcome message
        welcome_message = f"""
🎭 Welcome to the Interactive Story Experience! 🎭

{initial_context}

You are now {character_name}. Your choices will shape the story and create unique paths.
Type your responses to continue the adventure!

Commands:
- 'status' - Check your character status
- 'progress' - View story progress
- 'endings' - See available story branches
- 'quit' - End the session

What would you like to do?
"""
        
        self.conversation_history.append({
            "type": "system",
            "content": welcome_message,
            "timestamp": self._get_timestamp()
        })
        
        return welcome_message
    
    def process_user_input(self, user_input: str) -> str:
        """Process user input and generate appropriate response"""
        if not self.current_character:
            return "Chat session not initialized. Please select a character first."
        
        # Handle special commands
        if user_input.lower() == 'quit':
            return self._handle_quit()
        elif user_input.lower() == 'status':
            return self._handle_status()
        elif user_input.lower() == 'progress':
            return self._handle_progress()
        elif user_input.lower() == 'endings':
            return self._handle_endings()
        
        # Add user input to history
        self.conversation_history.append({
            "type": "user",
            "content": user_input,
            "timestamp": self._get_timestamp()
        })
        
        # Update dynamic knowledge based on user response
        consequences = self.updater.update_based_on_user_response(user_input, self.current_character)
        
        # Generate next story segment
        next_story = self.generator.generate_next_story_segment(user_input, self.current_character, consequences)
        
        # Add story response to history
        self.conversation_history.append({
            "type": "story",
            "content": next_story,
            "timestamp": self._get_timestamp(),
            "consequences": consequences
        })
        
        # Update story progress
        self.story_progress += 1
        
        # Add some variety based on progress
        if self.story_progress % 5 == 0:  # Every 5 interactions
            progress_update = self._generate_progress_update()
            next_story += f"\n\n{progress_update}"
        
        return next_story
    
    def _handle_quit(self) -> str:
        """Handle quit command"""
        # Save conversation history
        self._save_conversation_history()
        
        farewell = f"""
🎭 Thank you for playing as {self.current_character}! 🎭

Your story has been saved with:
- {len(self.conversation_history)} interactions
- {self.story_progress} story progress points
- Multiple alternative endings explored

Come back anytime to continue your adventure!
"""
        
        self.conversation_history.append({
            "type": "system",
            "content": farewell,
            "timestamp": self._get_timestamp()
        })
        
        return farewell
    
    def _handle_status(self) -> str:
        """Handle status command"""
        status = self.generator.generate_character_status_update(self.current_character)
        
        self.conversation_history.append({
            "type": "system",
            "content": status,
            "timestamp": self._get_timestamp()
        })
        
        return status
    
    def _handle_progress(self) -> str:
        """Handle progress command"""
        progress = self.generator.get_story_progress()
        
        progress_text = f"""
📊 Story Progress Report 📊

Total Events: {progress['total_events']}
User-Generated Events: {progress['user_generated_events']}
Alternative Endings Available: {progress['alternative_endings_available']}
Story Complexity: {progress['story_complexity']}/100
Recent Activity: {progress['recent_activity']} events

You're making great progress in shaping this story!
"""
        
        self.conversation_history.append({
            "type": "system",
            "content": progress_text,
            "timestamp": self._get_timestamp()
        })
        
        return progress_text
    
    def _handle_endings(self) -> str:
        """Handle endings command"""
        ending_previews = self.generator.generate_alternative_ending_preview(self.current_character)
        
        if not ending_previews:
            endings_text = "No alternative endings have been discovered yet. Keep making choices to unlock new story paths!"
        else:
            endings_text = "🎯 Available Story Branches 🎯\n\n"
            for ending in ending_previews:
                endings_text += f"Branch {ending['id']}: {ending['description']}\n"
                endings_text += f"Preview: {ending['preview']}\n"
                endings_text += f"Conditions: {', '.join(ending['conditions'])}\n\n"
        
        self.conversation_history.append({
            "type": "system",
            "content": endings_text,
            "timestamp": self._get_timestamp()
        })
        
        return endings_text
    
    def _generate_progress_update(self) -> str:
        """Generate periodic progress updates"""
        progress = self.generator.get_story_progress()
        
        if progress['alternative_endings_available'] > 5:
            return "🌟 Your choices have created a rich, branching narrative with many possible outcomes!"
        elif progress['alternative_endings_available'] > 2:
            return "✨ The story is developing interesting new paths based on your decisions."
        else:
            return "📝 Your story is taking shape. Each choice matters!"
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def _save_conversation_history(self):
        """Save conversation history to file"""
        history_path = f"conversation_history_{self.current_character}_{self._get_timestamp().split('T')[0]}.json"
        
        history_data = {
            "character": self.current_character,
            "session_date": self._get_timestamp().split('T')[0],
            "total_interactions": len(self.conversation_history),
            "story_progress": self.story_progress,
            "conversation": self.conversation_history
        }
        
        os.makedirs("conversation_logs", exist_ok=True)
        with open(f"conversation_logs/{history_path}", "w", encoding="utf-8") as f:
            json.dump(history_data, f, indent=2, ensure_ascii=False)
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get a summary of the current conversation"""
        user_messages = [msg for msg in self.conversation_history if msg["type"] == "user"]
        story_messages = [msg for msg in self.conversation_history if msg["type"] == "story"]
        
        return {
            "character": self.current_character,
            "total_interactions": len(self.conversation_history),
            "user_messages": len(user_messages),
            "story_segments": len(story_messages),
            "story_progress": self.story_progress,
            "session_duration": "ongoing"
        }
    
    def export_story_data(self) -> Dict[str, Any]:
        """Export current story data for external use"""
        return {
            "character": self.current_character,
            "conversation_history": self.conversation_history,
            "story_progress": self.story_progress,
            "dynamic_knowledge": self.updater.dynamic_knowledge,
            "export_timestamp": self._get_timestamp()
        } 