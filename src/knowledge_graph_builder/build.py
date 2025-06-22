import os
import yaml
import re
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
book_path = "book_data/harrypotter.txt"  # This will be the uploaded file from web
output_path = "knowledge_base/world_knowledge_graph.yaml"

# 4. Read book
if not os.path.exists(book_path):
    print(f"Book file not found: {book_path}")
    exit(1)

with open(book_path, "r", encoding="utf-8") as f:
    book_text = f.read()

def create_fallback_knowledge_graph(book_text):
    """Create a basic knowledge graph structure from actual text analysis"""
    print("Creating fallback knowledge graph from text analysis...")
    
    # Basic analysis of the text
    lines = book_text.split('\n')
    title = ""
    characters = []
    
    # Extract title from first few lines
    for i, line in enumerate(lines[:10]):
        line = line.strip()
        if line and not line.startswith('CHAPTER') and not line.startswith('Chapter'):
            title = line
            break
    
    # Extract character names using various patterns
    character_names = set()
    
    # Pattern 1: Look for capitalized names (likely character names)
    for line in lines:
        words = line.split()
        for word in words:
            # Clean the word
            clean_word = re.sub(r'[^\w\s]', '', word)
            if (len(clean_word) > 2 and 
                clean_word[0].isupper() and 
                clean_word[1:].islower() and
                clean_word not in ['The', 'And', 'But', 'For', 'With', 'From', 'Into', 'During', 'Before', 'After', 'Above', 'Below', 'Between', 'Among', 'Through', 'Within', 'Without', 'Against', 'Toward', 'Towards', 'Upon', 'About', 'Around', 'Across', 'Behind', 'Beneath', 'Beside', 'Beyond', 'Inside', 'Outside', 'Under', 'Over', 'Along', 'Throughout', 'Until', 'Since', 'While', 'When', 'Where', 'Why', 'How', 'What', 'Who', 'Which', 'That', 'This', 'These', 'Those']):
                character_names.add(clean_word)
    
    # Pattern 2: Look for dialogue patterns (character names followed by dialogue)
    for i, line in enumerate(lines):
        if ':' in line and len(line.split(':')) == 2:
            speaker = line.split(':')[0].strip()
            if speaker and speaker[0].isupper():
                character_names.add(speaker)
    
    # Pattern 3: Look for "said [Name]" patterns
    for line in lines:
        matches = re.findall(r'said\s+([A-Z][a-z]+)', line, re.IGNORECASE)
        for match in matches:
            character_names.add(match)
    
    # Convert to list and filter out common words
    character_list = list(character_names)
    character_list = [name for name in character_list if len(name) > 2]
    
    # Create character entries
    for name in character_list[:20]:  # Limit to first 20 characters
        characters.append({
            "name": name,
            "aliases": [],
            "description": f"Character from {title or 'the story'}",
            "roles": ["Character"],
            "traits": [],
            "skills_or_powers": [],
            "items": [],
            "motivations": "",
            "arc": "",
            "relationships": [],
            "quotes": ""
        })
    
    # Extract main events from the text
    main_events = []
    paragraphs = book_text.split('\n\n')
    
    for i, paragraph in enumerate(paragraphs[:10]):  # Limit to first 10 paragraphs
        if len(paragraph.strip()) > 50:  # Only significant paragraphs
            main_events.append({
                "event": f"Event {i+1}",
                "quotes": "",
                "details": paragraph.strip()[:200] + "..." if len(paragraph) > 200 else paragraph.strip()
            })
    
    # Create basic knowledge graph structure
    knowledge_graph = {
        "book_info": {
            "title": title or "Uploaded Story",
            "author": "Unknown",
            "publication_year": "",
            "genre": "Story",
            "themes": [],
            "tone_and_style": "",
            "narrative_point_of_view": "",
            "summary": f"Story uploaded by user containing {len(character_list)} characters and {len(main_events)} main events.",
            "intended_audience": "General audience"
        },
        "characters": characters,
        "storyline": {
            "main_events": main_events,
            "timeline": [],
            "locations": [],
            "foreshadowing": [],
            "motifs_symbols": [],
            "narrative_tension": []
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