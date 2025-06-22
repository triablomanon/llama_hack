# Interactive Story Experience

A dynamic, AI-powered interactive story system that creates personalized narratives based on user choices. The system updates a dynamic knowledge graph in real-time, generating alternative endings based on user responses.

## 🎭 Features

- **Dynamic Knowledge Graph**: Real-time updates based on user choices
- **Alternative Endings**: Multiple story branches created through user interactions
- **Character Development**: Characters evolve based on user decisions
- **Interactive Chat Interface**: Real-time story progression through chat
- **Story Progress Tracking**: Monitor your journey and available paths
- **Session Persistence**: Save and continue your story later

## 📁 Project Structure

```
llama_hack/
├── src/
│   ├── choose_character.py          # Character selection and initialization
│   ├── interactive_story.py         # Main execution file
│   ├── chat_interface.py            # Real-time chat handling
│   ├── dynamic_updater.py           # Dynamic knowledge graph updates
│   ├── story_generator.py           # Story content generation
│   └── knowledge_graph_builder/
│       └── test_llama_api copy.py   # Static knowledge graph creation
├── knowledge_base/
│   ├── world_knowledge_graph.json   # Static world knowledge
│   └── dynamic_world_knowledge.json # Dynamic user-specific knowledge
├── book_data/
│   └── harrypotter.txt              # Source material
├── conversation_logs/               # Saved conversation histories
└── requirements.txt
```

## 🚀 Quick Start

### 1. Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Set up your API key (if using Llama API)
echo "LLAMA_API_KEY=your_api_key_here" > .env
```

### 2. Initialize the World

```bash
# Create static knowledge graph from book data
python src/knowledge_graph_builder/test_llama_api\ copy.py

# Choose character and initialize dynamic knowledge
python src/choose_character.py
```

### 3. Start Interactive Story

```bash
# Launch the interactive story experience
python src/interactive_story.py
```

## 🎮 How to Play

1. **Character Selection**: Choose your character from the available options
2. **Interactive Chat**: Respond to story prompts and make choices
3. **Story Evolution**: Watch as your choices create new story branches
4. **Commands**: Use special commands during gameplay:
   - `status` - Check your character status
   - `progress` - View story progress
   - `endings` - See available story branches
   - `quit` - End the session

## 🔧 Module Details

### Dynamic Knowledge Updater (`dynamic_updater.py`)
- Analyzes user responses for emotional and narrative impact
- Updates character states, relationships, and story events
- Creates alternative ending branches based on user choices
- Maintains timestamped history of all changes

### Story Generator (`story_generator.py`)
- Generates contextual story segments based on user choices
- Creates character status updates and progress reports
- Provides previews of alternative endings
- Tracks story complexity and branching

### Chat Interface (`chat_interface.py`)
- Handles real-time user interactions
- Processes special commands and user responses
- Maintains conversation history
- Saves session data for later continuation

## 📊 Story Mechanics

### User Response Analysis
The system analyzes user responses using keyword detection:
- **Conflict**: "fight", "attack", "confront" → Aggressive story direction
- **Heroic**: "help", "save", "protect" → Heroic story direction  
- **Survival**: "run", "escape", "hide" → Cautious story direction
- **Diplomatic**: "talk", "negotiate", "diplomacy" → Diplomatic story direction

### Dynamic Updates
- **Character Development**: Emotional states and character arcs evolve
- **Relationship Changes**: Interactions between characters are tracked
- **Story Events**: New events are added to the timeline
- **Alternative Endings**: New story branches are created based on choices

## 🔮 Future Possibilities

- **Multiplayer Support**: Collaborative storytelling in group chats
- **Movie Adaptation**: Using movies instead of books as source material
- **Story Generation**: AI-generated original stories and worlds
- **Enhanced AI Integration**: More sophisticated response analysis
- **Visual Interface**: Web-based or mobile app interface

## 🛠️ Development

### Adding New Story Directions
To add new story directions, modify the `analyze_user_response` method in `dynamic_updater.py`:

```python
elif any(word in response_lower for word in ["your_keywords"]):
    consequences["emotional_impact"] = "Your emotional impact description"
    consequences["arc_development"] = "Your character development description"
    consequences["story_direction"] = "your_direction_name"
```

### Customizing Story Templates
Add new story templates in `story_generator.py`:

```python
story_templates = {
    "your_direction_name": [
        "Your story template 1...",
        "Your story template 2...",
        "Your story template 3..."
    ]
}
```

## 📝 Requirements

- Python 3.7+
- `python-dotenv`
- `llama-api-client` (optional, for enhanced AI features)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.
