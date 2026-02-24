import os
import json
from groq import Groq
from dotenv import load_dotenv
from models import SlideContent, PresentationOutline

load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))


def build_outline(topic: str, num_slides: int = 8) -> PresentationOutline:
    prompt = f"""
Research the topic '{topic}' deeply and return a comprehensive, detailed JSON object with this exact structure:

{{
  "topic": "Main Topic Title",
  "slides": [
    {{
      "title": "Introduction",
      "bullets": [
        "Detailed bullet point with 15-25 words explaining the concept thoroughly",
        "Another comprehensive point with specific examples and context",
        "Third point with statistics, facts, or real-world applications"
      ],
      "notes": "Detailed speaker notes with 2-3 sentences providing background and extra context for the presenter",
      "image_query": "relevant search term for image",
      "table": null
    }},
    {{
      "title": "Comparison / Pros & Cons / Key Metrics",
      "bullets": [],
      "notes": "Explain the table content and key takeaways in 2-3 sentences",
      "image_query": "",
      "table": {{
        "headers": ["Column 1", "Column 2", "Column 3"],
        "rows": [
          ["Detailed point 1 in col 1", "Detailed point 1 in col 2", "Detail 1 in col 3"],
          ["Detailed point 2 in col 1", "Detailed point 2 in col 2", "Detail 2 in col 3"],
          ["Detailed point 3 in col 1", "Detailed point 3 in col 2", "Detail 3 in col 3"]
        ]
      }}
    }}
  ]
}}

**STRICT RULES:**
- Generate EXACTLY {num_slides} slides (no more, no less)
- Include 1-2 table slides within those {num_slides} slides
- Each bullet must be 15-25 words long — comprehensive and detailed
- Include specific examples, statistics, facts, or real-world applications
- Speaker notes must be 2-3 full sentences with extra context
- Table slides should have empty bullets array and no image_query
- Non-table slides must have 4-5 detailed bullets
- Return ONLY valid JSON, no markdown, no explanations
"""

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You are a research assistant that generates comprehensive, detailed slide content. Always return pure JSON.",
            },
            {"role": "user", "content": prompt},
        ],
        model="llama-3.3-70b-versatile",
        temperature=0.7,
        max_tokens=8000,
    )

    raw_response = chat_completion.choices[0].message.content.strip()

    # Clean response
    if raw_response.startswith("```json"):
        raw_response = raw_response[7:]
    if raw_response.startswith("```"):
        raw_response = raw_response[3:]
    if raw_response.endswith("```"):
        raw_response = raw_response[:-3]
    raw_response = raw_response.strip()

    try:
        data = json.loads(raw_response)
        outline = PresentationOutline(**data)
        print(f"✅ Generated {len(outline.slides)} slides for '{outline.topic}'")
        return outline
    except Exception as e:
        print(f"❌ Parse error: {e}")
        print(f"Raw response: {raw_response[:500]}")
        raise


if __name__ == "__main__":
    outline = build_outline("Artificial Intelligence", num_slides=8)
    print(f"\nTopic: {outline.topic}")
    for i, slide in enumerate(outline.slides, start=1):
        print(f"\nSlide {i}: {slide.title}")
        if slide.table:
            print(f"  [TABLE with {len(slide.table.rows)} rows]")
        else:
            for bullet in slide.bullets:
                print(f"  • {bullet}")
