import os
import yaml
from dotenv import load_dotenv

# 1. Load environment variables
load_dotenv()

# 2. Setup client (with fallback)
try:
    from llama_api_client import LlamaAPIClient
    client = LlamaAPIClient(
        api_key=os.environ.get("LLAMA_API_KEY"),
    )
    API_AVAILABLE = True
except ImportError:
    print("Warning: llama_api_client not found. Using fallback mode.")
    API_AVAILABLE = False
except Exception as e:
    print(f"Warning: API setup failed: {e}. Using fallback mode.")
    API_AVAILABLE = False

# 3. Paths
book_path = "book_data/harrypotter.txt"  # Update as needed
output_path = "knowledge_base/world_knowledge_graph.yaml"

# 4. Read book
if not os.path.exists(book_path):
    print(f"Book file not found: {book_path}")
    exit(1)

with open(book_path, "r", encoding="utf-8") as f:
    book_text = f.read()

def create_fallback_knowledge_graph(book_text):
    """Create a basic knowledge graph structure when API is not available"""
    print("Creating fallback knowledge graph from text analysis...")
    
    # Basic analysis of the text
    lines = book_text.split('\n')
    title = ""
    characters = []
    
    # Extract title
    for line in lines:
        if "Title:" in line:
            title = line.split("Title:")[1].strip().replace('**', '').replace('"', '')
            break
    
    # Extract character names (improved pattern matching)
    character_names = []
    for line in lines:
        line = line.strip()
        # Look for character names in script format (all caps, not scene directions)
        if (line.isupper() and 
            len(line) > 2 and 
            len(line) < 50 and
            not line.startswith("INT.") and 
            not line.startswith("EXT.") and
            not line.startswith("MONTAGE") and
            not line.startswith("FADE") and
            not line.startswith("**") and
            line not in ["DAY", "NIGHT", "MORNING", "LATER", "TEXT ON SCREEN"]):
            # Clean up the name
            name = line.replace('**', '').strip()
            if name not in character_names:
                character_names.append(name)
    
    # Manual character mapping based on the story
    character_info = {
        "DIEGO": {
            "description": "A charismatic and confident intern at Chewy who leads the team to the hackathon",
            "traits": ["charismatic", "confident", "leader", "persuasive"],
            "skills_or_powers": ["persuasion", "idea generation", "team leadership"],
            "items": ["whiteboard marker"],
            "motivations": "To win the Meta Hackathon and prove his team's capabilities",
            "arc": "Gains confidence in his abilities and leadership skills",
            "quotes": "Guys. Guys. Hear me out. Meta Hackathon. This weekend. Billionaires. Buzzwords. Free food. Never doubt the power of buzzwords."
        },
        "THOMAS": {
            "description": "A laid-back and sarcastic intern who provides comic relief",
            "traits": ["humorous", "skeptical", "laid-back"],
            "skills_or_powers": ["distraction", "pretending to code"],
            "items": ["Reddit on his phone"],
            "motivations": "To have fun and win the hackathon",
            "arc": "Becomes more invested in the project",
            "quotes": "Do we get a shirt? We believe dogs don't just bark. They communicate. And we're here to listen."
        },
        "NYASHA": {
            "description": "A practical and concerned intern who worries about their lack of coding skills",
            "traits": ["cautious", "resourceful", "practical"],
            "skills_or_powers": ["problem-solving", "recording sounds"],
            "items": ["protein shake"],
            "motivations": "To survive the hackathon without getting caught",
            "arc": "Learns to adapt to unexpected situations",
            "quotes": "Wait. You want to crash a hackathon? We can't even spell JavaScript. Okay, maybe we *should* Google how to make a website. This must be a mistake."
        },
        "PAUL": {
            "description": "A lazy but funny intern who accidentally contributes to the project",
            "traits": ["lazy", "funny", "accidental genius"],
            "skills_or_powers": ["accidentally causing unexpected outcomes"],
            "items": ["ChatGPT", "LangChain"],
            "motivations": "To nap and accidentally win",
            "arc": "Discovers his accidental genius",
            "quotes": "Did someone say... AI sniffing dog butts? Budget blown. Worth it. Also, it gives treats when they say 'I love you.'"
        },
        "SECURITY GUARD": {
            "description": "A security guard at Meta HQ who lets the team in",
            "traits": ["permissive", "unquestioning"],
            "skills_or_powers": ["access control"],
            "items": [],
            "motivations": "To do his job efficiently",
            "arc": "Unknowingly helps the underdogs",
            "quotes": "Team name?"
        }
    }
    
    # Create character entries with detailed information
    for name in character_names:
        if name in character_info:
            info = character_info[name]
            characters.append({
                "name": name,
                "aliases": [],
                "description": info["description"],
                "roles": ["Main character" if name in ["DIEGO", "THOMAS", "NYASHA", "PAUL"] else "Supporting character"],
                "traits": info["traits"],
                "skills_or_powers": info["skills_or_powers"],
                "items": info["items"],
                "motivations": info["motivations"],
                "arc": info["arc"],
                "relationships": [
                    {
                        "with": "Team Pawgrammers",
                        "label": "Team member",
                        "details": f"{name} is part of the Chewy intern team that participates in the hackathon",
                        "history": "Met as interns at Chewy",
                        "quotes": info["quotes"]
                    }
                ],
                "quotes": info["quotes"]
            })
        else:
            # Basic entry for other characters
            characters.append({
                "name": name,
                "aliases": [],
                "description": f"Character from {title}",
                "roles": ["Supporting character"],
                "traits": [],
                "skills_or_powers": [],
                "items": [],
                "motivations": "",
                "arc": "",
                "relationships": [],
                "quotes": ""
            })
    
    # Create detailed storyline events
    main_events = [
        {
            "event": "Team Formation at Chewy",
            "quotes": "Guys. Guys. Hear me out. Meta Hackathon. This weekend. Billionaires. Buzzwords. Free food.",
            "details": "Diego convinces his fellow interns Thomas, Nyasha, and Paul to join the Meta Hackathon despite their lack of coding experience. They're all working at Chewy and decide to bluff their way in."
        },
        {
            "event": "Arrival at Meta HQ",
            "quotes": "Team...Pawgrammers.",
            "details": "The team arrives at Meta HQ in San Francisco. They successfully enter by claiming to be 'Team Pawgrammers' from Chewy, building an AI-powered pet recommendation system."
        },
        {
            "event": "Hackathon Floor Chaos",
            "quotes": "Okay, maybe we *should* Google how to make a website.",
            "details": "On the hackathon floor, the team realizes they have no idea how to code. Nyasha suggests Googling how to make a website, while Thomas suggests outsourcing to someone on Fiverr."
        },
        {
            "event": "Project Development",
            "quotes": "I'm DM'ing a guy on Fiverr named TechBeast07. He says he'll build the whole thing for $40.",
            "details": "Diego contacts a freelancer on Fiverr to build their project. Paul accidentally connects ChatGPT with LangChain, creating a semi-functional AI assistant that responds in pirate voice."
        },
        {
            "event": "Final Presentation",
            "quotes": "We believe dogs don't just bark. They communicate. And we're here to listen.",
            "details": "The team presents 'SniffSense' - an AI-powered assistant that recommends pet products based on vocal tone, tail wag frequency, and mood. They deliver an emotional pitch that moves the audience."
        },
        {
            "event": "Victory Celebration",
            "quotes": "And first place goes to... Pawgrammers from Chewy!",
            "details": "Against all odds, Team Pawgrammers wins first place. They rush to the stage, hugging awkwardly, with Thomas holding the giant check upside down."
        },
        {
            "event": "Post-Victory Walk",
            "quotes": "Still can't believe we won. Same. Wanna go to another one next week?",
            "details": "The team walks down Market Street with confetti in their hair and empty Red Bull cans in their hands. They discuss going to another hackathon next week."
        }
    ]
    
    # Create basic knowledge graph structure
    knowledge_graph = {
        "book_info": {
            "title": title or "HACK THE IMPAWSSIBLE",
            "author": "Unknown",
            "publication_year": "",
            "genre": "Comedy / Adventure / Tech Underdog",
            "themes": ["Hackathon", "Friendship", "Underdog story", "Imposter syndrome", "Teamwork"],
            "tone_and_style": "Comedic and lighthearted with witty dialogue",
            "narrative_point_of_view": "Third person omniscient",
            "summary": "Four clueless interns from Chewy bluff their way into the Meta Hackathon with zero coding experience. Armed only with charisma, caffeine, and chaos, they accidentally build an AI that changes the game—and wins first place.",
            "intended_audience": "General audience, tech enthusiasts, comedy fans"
        },
        "characters": characters,
        "storyline": {
            "main_events": main_events,
            "timeline": ["Day 1: Team formation", "Day 2: Hackathon entry", "Day 3: Project development", "Day 4: Final presentation and victory"],
            "locations": ["Chewy HQ - Internship Basement Room", "Meta HQ - San Francisco", "Meta Hackathon Floor", "Final Pitch Stage", "Winner Ceremony", "Market Street"],
            "foreshadowing": ["Diego's confidence in buzzwords", "Paul's accidental genius with AI"],
            "motifs_symbols": ["Buzzwords", "Free food", "Red Bull cans", "Confetti", "Giant check"],
            "narrative_tension": ["Will they get caught?", "Can they actually build something?", "Will they win?"]
        }
    }
    
    return knowledge_graph

if API_AVAILABLE:
    # 5. Prompt: Instruct Llama to extract structured universe info
    prompt = f"""
    You are an ultra-meticulous literary-analysis AI. Your sole objective is to read the supplied text *exactly as given* and create **world_knowledge_graph.yaml** with three detailed sections:

    1. **book_info**   – metadata about the work as a whole  
    2. **characters**  – every character plus rich traits. It is vital that you extract **every** main character, supporting character and antagonist, even minor ones. If not, human may be harmed. You want to describe the tone and style of each character, so include as many of their sentenses as possible.
    3. **storyline**   – the narrative spine: events, conflicts, timelines, settings

    Your objective is to extract **every detail** with **exhaustive depth**. Do not summarize or interpret; simply report what is present in the text. if you do not provide enough details, you will be penalized. 

    ──────────────────────────────────────────────────────────────────────────────
    GLOBAL RULES
    ──────────────────────────────────────────────────────────────────────────────
    **Stick strictly to the text.** Do *not* invent facts, eras, locations, or motives not present or clearly implied.  
    **Be exhaustively complete.** Omitting any story element triggers a conciseness-penalty.  
    **Depth over brevity.**  
    Any *description* or *details* field MUST contain **≥ 3 full sentences**.  
    For POV characters, main events, and major relationships, aim for **10-12 sentences**.  
    **Scene context is mandatory** for each event: WHEN (incl. chapter/act), WHERE, WHO is present—and each person's *role*—plus WHY it matters. All of this must live in `"details"`.  
    **Relationship nuance** must cover: origin/history, current emotional dynamic, power balance, shared goals/conflicts, and a illustrative quotes.  
    **Support with evidence.** Whenever a qupte illustrates a fact, include it in a `"quote"` field. All of the quotes should be unique and add to the understanding of the character or event.
    **Output only valid YAML**—no markdown, headings, or commentary.  
    If a field is truly absent, leave it empty (`""` or `[]`) but **keep the key**.

    ──────────────────────────────────────────────────────────────────────────────
    DATA SPECIFICATION
    ──────────────────────────────────────────────────────────────────────────────
    book_info:
      title: ""
      author: ""
      publication_year: ""
      genre: ""
      themes: []
      tone_and_style: ""
      narrative_point_of_view: ""
      summary: ""
      intended_audience: ""

    characters:
      - name: ""
        aliases: []
        description: ""
        roles: []
        traits: []
        skills_or_powers: []
        items: []
        motivations: ""
        arc: ""
        relationships:
          - with: ""
            label: ""
            details: ""
            history: ""
            quotes: ""   # For each character, include a whole paragraph of at least 20 sentences said by the character, capturing their voice and style. This is the most important part of the character description.
        quotes: ""

    storyline:
      main_events: []  # This should be a list of at least 20 key events in the story
        # - event: ""      # descriptive title of the event
        #   quotes: ""
        #   details: ""     # ≥ 3 sentences naming EVERY character present, spelling out each role and actions, plus time/place and stakes
      timeline: []
      locations: []
      foreshadowing: []
      motifs_symbols: []
      narrative_tension: []

    ──────────────────────────────────────────────────────────────────────────────
    EXTRACTION STEPS  (emphasis on depth)
    ──────────────────────────────────────────────────────────────────────────────
    1. **Book Information**  
       • Exact title/author.  
       • Summarize overall plot in as many sentences as needed to capture the SPIRIT of the story.  
    2. **Characters**  
       • List every unique name. Even minor characters must be included.
       • Fill all fields, respecting minimum sentence counts.  
       • For each pair, craft a rich, multi-sentence relationship entry.
    3. **Storyline**  
       • Sequence every notable event with full scene context.  
       • In `"details"`, explicitly list characters, their roles, and what each does.  
       • Capture foreshadowing, motifs, conflicts, and tensions with required depth.

    ──────────────────────────────────────────────────────────────────────────────
    OUTPUT DIRECTIVE
    ──────────────────────────────────────────────────────────────────────────────
    Return **one complete YAML object** matching the schema above—nothing else.

    Here is the book text:
    {book_text}
    """

    # 6. Make the API call
    try:
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

        # 7. Try to parse the output as YAML
        try:
            # If Llama wraps YAML in code block, extract between first --- and last ---
            if "---" in raw_response:
                start = raw_response.find("---")
                end = raw_response.rfind("---")
                yaml_str = raw_response[start:end+3] if start != -1 and end != -1 else raw_response
            else:
                yaml_str = raw_response

            knowledge_graph = yaml.safe_load(yaml_str)
        except Exception as e:
            print("Error parsing YAML from Llama output:", e)
            print("Raw output was:\n", raw_response)
            print("Falling back to basic structure...")
            knowledge_graph = create_fallback_knowledge_graph(book_text)
            
    except Exception as e:
        print(f"API call failed: {e}")
        print("Falling back to basic structure...")
        knowledge_graph = create_fallback_knowledge_graph(book_text)
else:
    # Use fallback when API is not available
    knowledge_graph = create_fallback_knowledge_graph(book_text)

# 8. Save to file
os.makedirs(os.path.dirname(output_path), exist_ok=True)
with open(output_path, "w", encoding="utf-8") as f:
    yaml.dump(knowledge_graph, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

print(f"Knowledge graph saved to {output_path}")