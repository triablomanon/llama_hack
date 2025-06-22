import json
import os
import sys
from typing import Dict, List, Any, Optional

# Add current directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

try:
    from dynamic_updater import DynamicKnowledgeUpdater
    from story_generator import StoryGenerator
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure all required modules are in the same directory.")
    sys.exit(1)

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
        if not self.current_character:
            return "No character selected."
        
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
        if not self.current_character:
            return "No character selected."
        
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

def main():
    """Main execution function for running the chat interface directly"""
    print("🎭 Interactive Story Chat Interface 🎭")
    print("=" * 50)
    
    # Check if required files exist
    required_files = [
        "knowledge_base/world_knowledge_graph.json",
        "knowledge_base/dynamic_world_knowledge.json"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ Missing required files:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        print("\nPlease ensure the knowledge base files exist before running.")
        return
    
    # Load available characters from world knowledge
    try:
        with open("knowledge_base/world_knowledge_graph.json", "r", encoding="utf-8") as f:
            world_knowledge = json.load(f)
        
        characters = world_knowledge.get("characters", [])
        if not characters:
            print("❌ No characters found in world knowledge.")
            return
        
        print("Available characters:")
        for i, char in enumerate(characters[:10], 1):  # Show first 10 characters
            if isinstance(char, dict):
                print(f"{i}. {char.get('name', 'Unknown')}")
            else:
                print(f"{i}. {str(char)}")
        
        # Simple character selection
        while True:
            try:
                choice = input(f"\nSelect a character (1-{min(len(characters), 10)}): ").strip()
                choice_num = int(choice)
                if 1 <= choice_num <= min(len(characters), 10):
                    selected_char = characters[choice_num - 1]
                    if isinstance(selected_char, dict):
                        character_name = selected_char.get('name', 'Unknown')
                    else:
                        character_name = str(selected_char)
                    break
                else:
                    print(f"Please enter a number between 1 and {min(len(characters), 10)}")
            except ValueError:
                print("Please enter a valid number")
            except KeyboardInterrupt:
                print("\nExiting...")
                return
        
        print(f"\n✅ Selected character: {character_name}")
        
        # Initialize chat interface
        chat_interface = ChatInterface()
        
        # Start chat session
        welcome_message = chat_interface.initialize_chat(character_name)
        print(welcome_message)
        
        # Main chat loop
        while True:
            try:
                # Get user input
                user_input = input(f"\n[{character_name}] > ").strip()
                
                if not user_input:
                    print("Please enter a response to continue the story.")
                    continue
                
                # Process user input
                response = chat_interface.process_user_input(user_input)
                print(f"\n{response}")
                
                # Check if user wants to quit
                if user_input.lower() == 'quit':
                    break
                    
            except KeyboardInterrupt:
                print("\n\n🛑 Session interrupted. Saving progress...")
                chat_interface._save_conversation_history()
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                print("Continuing with the story...")
        
        # Final summary
        summary = chat_interface.get_conversation_summary()
        print("\n" + "=" * 50)
        print("📊 SESSION SUMMARY 📊")
        print("=" * 50)
        print(f"Character: {summary['character']}")
        print(f"Total Interactions: {summary['total_interactions']}")
        print(f"User Messages: {summary['user_messages']}")
        print(f"Story Segments: {summary['story_segments']}")
        print(f"Story Progress: {summary['story_progress']}")
        print("\n🎭 Thank you for playing! 🎭")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Please check your setup and try again.")

if __name__ == "__main__":
    main() 