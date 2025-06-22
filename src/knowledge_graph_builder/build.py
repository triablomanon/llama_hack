import os
import json
from dotenv import load_dotenv
from llama_api_client import LlamaAPIClient

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
You are an ultra-meticulous literary-analysis AI. Your sole objective is to read the supplied text *exactly as given* and create **world_knowledge_graph.json** with three detailed sections:

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
**Scene context is mandatory** for each event: WHEN (incl. chapter/act), WHERE, WHO is present—and each person’s *role*—plus WHY it matters. All of this must live in `"details"`.  
**Relationship nuance** must cover: origin/history, current emotional dynamic, power balance, shared goals/conflicts, and a illustrative quotes.  
**Support with evidence.** Whenever a qupte illustrates a fact, include it in a `"quote"` field. All of the quotes should be unique and add to the understanding of the character or event.
**Output only valid JSON**—no markdown, headings, or commentary.  
If a field is truly absent, leave it empty (`""` or `[]`) but **keep the key**.

──────────────────────────────────────────────────────────────────────────────
DATA SPECIFICATION
──────────────────────────────────────────────────────────────────────────────
{{
  "book_info": {{
    "title": "",
    "author": "",
    "publication_year": "",
    "genre": "",
    "themes": [],
    "tone_and_style": "",
    "narrative_point_of_view": "",
    "summary": "",
    "intended_audience": ""
  }},
  "characters": [
    {{
      "name": "",
      "aliases": [],
      "description": "",
      "roles": [],
      "traits": [],
      "skills_or_powers": [],
      "items": [],
      "motivations": "",
      "arc": "",
      "relationships": [
        {{
          "with": "",
          "label": "",
          "details": "",
          "history": "",
          "quotes": ""   // For each character, include a whole paragraph of at least 20 sentences said by the character, capturing their voice and style. This is the most important part of the character description.
        }}
      ],
      "quotes": ""
    }}
  ],
  "storyline": {{
    "main_events": [  This should be a list of at least 20 key events in the story
      {{
        "event": "",      // descriptive title of the event
        "quotes": "",
        "details": ""     // ≥ 3 sentences naming EVERY character present, spelling out each role and actions, plus time/place and stakes
      }}
    ],
    "timeline": [],
    "locations": [],
    "foreshadowing": [],
    "motifs_symbols": [],
    "narrative_tension": [],
  }}
}}

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
Return **one complete JSON object** matching the schema above—nothing else.

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