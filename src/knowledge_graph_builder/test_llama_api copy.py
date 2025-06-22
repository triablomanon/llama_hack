import os
import json
from dotenv import load_dotenv
import llama_cpp
import llama

# 1. Load environment variables
load_dotenv()

# 2. Setup client
client = LlamaAPIClient(
    api_key=os.environ.get("LLAMA_API_KEY"),
)

# 3. Paths
book_path = "book_data/harrypotter.txt"  # Update as needed
output_path = "knowledge_base/world_knowledge_graph.json"

# 4. Read book
if not os.path.exists(book_path):
    print(f"Book file not found: {book_path}")
    exit(1)

with open(book_path, "r", encoding="utf-8") as f:
    book_text = f.read()

# 5. Prompt: Instruct Llama to extract structured universe info
prompt = f"""
You are a highly advanced literary analysis AI. Your task is to read the following book and extract a comprehensive, structured JSON knowledge graph of its universe. 
Be extremely thorough. Extract every major and secondary character and all their relationships, traits, skills, talking style, backstory, items, motivations, affiliations, emotional arcs, and signature quotes.
Identify all important locations, events, conflicts, timelines, narrative tension points, foreshadowing, motifs, and parallel storylines.
Include book-wide information: title, author, genre, themes, tone/style, point of view, publication info, intended audience, and historical/cultural context.
**Output ONLY valid JSON in this structure**:

{{
  "book_info": {{
    "title": "",
    "author": "",
    "genre": "",
    "themes": [],
    "tone_and_style": "",
    "narrative_point_of_view": "",
    "publication_info": "",
    "intended_audience": "",
    "cultural_historical_context": ""
  }},
  "characters": [
    {{
      "name": "",
      "talking_style": "",
      "personality_traits": [],
      "skills_or_powers": [],
      "items": [],
      "backstory": "",
      "objective_motivations": "",
      "factions_affiliations": [],
      "character_arc": "",
      "emotional_state_trends": "",
      "signature_quotes": []
    }}
  ],
  "relationships": [
    {{
      "character_a": "",
      "character_b": "",
      "relationship_type": "",
      "history": "",
      "current_dynamic": ""
    }}
  ],
  "storyline": {{
    "main_events": [],
    "locations": [],
    "conflict_points": [],
    "timeline": [],
    "foreshadowing_elements": [],
    "recurring_motifs_symbols": [],
    "narrative_tension_points": [],
    "parallel_storylines": []
  }},
  "world_guidelines": {{
    "rules": "",
    "tone_and_style": "",
    "other_notes": ""
  }}
}}
Summarize and organize as much as possible based on the text, leaving fields blank if no info is found. Output ONLY the JSON, with no explanations, markdown, or prose.
Here is the book text:
{book_text}
"""

# 6. Make the API call
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

# 7. Try to parse the output as JSON
try:
    # If Llama wraps JSON in code block, extract between first { and last }
    start = raw_response.find("{")
    end = raw_response.rfind("}")
    json_str = raw_response[start:end+1] if start != -1 and end != -1 else raw_response

    knowledge_graph = json.loads(json_str)
except Exception as e:
    print("Error parsing JSON from Llama output:", e)
    print("Raw output was:\n", raw_response)
    exit(1)

# 8. Save to file
os.makedirs(os.path.dirname(output_path), exist_ok=True)
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(knowledge_graph, f, indent=2, ensure_ascii=False)

print(f"Knowledge graph saved to {output_path}")
