#!/usr/bin/env python3
"""
Interactive Story Experience - Main Execution File

This file integrates all modules to create a complete interactive story experience
where user responses update the dynamic knowledge graph and create alternative endings.
"""

import json
import os
import sys
from typing import Dict, List, Any

# Add src directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from .choose_character import choose_character_and_initialize
from .chat_interface import ChatInterface
from .dynamic_updater import DynamicKnowledgeUpdater
from .story_generator import StoryGenerator

class InteractiveStoryExperience:
    def __init__(self):
        self.chat_interface = None
        self.selected_character = None
        self.user_language = "English"
        
    def run(self):
        """Main execution loop"""
        print("🎭 Welcome to the Interactive Story Experience! 🎭")
        print("=" * 50)
        
        # Step 1: Initialize character and dynamic knowledge
        try:
            self.selected_character, self.user_language = self._initialize_experience()
        except Exception as e:
            print(f"Error during initialization: {e}")
            return
        
        # Step 2: Start interactive chat
        self._start_interactive_chat()
    
    def _initialize_experience(self) -> tuple:
        """Initialize the story experience with character selection"""
        print("Step 1: Character Selection and World Initialization")
        print("-" * 40)
        
        # Use the existing character selection logic
        character_name, user_language = choose_character_and_initialize()
        
        print(f"\n✅ Character selected: {character_name}")
        print(f"✅ Language: {user_language}")
        print(f"✅ Dynamic knowledge graph initialized")
        
        return character_name, user_language
    
    def _start_interactive_chat(self):
        """Start the interactive chat session"""
        print("\nStep 2: Interactive Story Session")
        print("-" * 40)
        
        # Initialize chat interface
        self.chat_interface = ChatInterface()
        
        # Start chat session
        welcome_message = self.chat_interface.initialize_chat(self.selected_character)
        print(welcome_message)
        
        # Main chat loop
        while True:
            try:
                # Get user input
                user_input = input(f"\n[{self.selected_character}] > ").strip()
                
                if not user_input:
                    print("Please enter a response to continue the story.")
                    continue
                
                # Process user input
                response = self.chat_interface.process_user_input(user_input)
                print(f"\n{response}")
                
                # Check if user wants to quit
                if user_input.lower() == 'quit':
                    break
                    
            except KeyboardInterrupt:
                print("\n\n🛑 Session interrupted. Saving progress...")
                self._save_session_data()
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                print("Continuing with the story...")
        
        # Final summary
        self._show_session_summary()
    
    def _save_session_data(self):
        """Save session data when interrupted"""
        if self.chat_interface:
            try:
                self.chat_interface._save_conversation_history()
                print("✅ Session data saved successfully.")
            except Exception as e:
                print(f"❌ Error saving session data: {e}")
    
    def _show_session_summary(self):
        """Show summary of the session"""
        if not self.chat_interface:
            return
        
        summary = self.chat_interface.get_conversation_summary()
        
        print("\n" + "=" * 50)
        print("📊 SESSION SUMMARY 📊")
        print("=" * 50)
        print(f"Character: {summary['character']}")
        print(f"Total Interactions: {summary['total_interactions']}")
        print(f"User Messages: {summary['user_messages']}")
        print(f"Story Segments: {summary['story_segments']}")
        print(f"Story Progress: {summary['story_progress']}")
        
        # Show alternative endings created
        try:
            progress = self.chat_interface.generator.get_story_progress()
            print(f"Alternative Endings Created: {progress['alternative_endings_available']}")
            print(f"Story Complexity: {progress['story_complexity']}/100")
        except:
            pass
        
        print("\n🎭 Thank you for playing! 🎭")
        print("Your story has been saved and can be continued later.")

def main():
    """Main entry point"""
    try:
        # Check if required files exist
        required_files = [
            "knowledge_base/world_knowledge_graph.yaml",
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
            print("\nPlease run the character selection process first:")
            print("   python src/choose_character.py")
            return
        
        # Start the interactive story experience
        experience = InteractiveStoryExperience()
        experience.run()
        
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        print("Please check your setup and try again.")

if __name__ == "__main__":
    main() 