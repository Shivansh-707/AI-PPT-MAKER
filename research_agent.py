import os
import json
import time
from groq import Groq
from dotenv import load_dotenv
from models import Slide, PresentationOutline

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def build_outline(topic: str) -> PresentationOutline:
    prompt = f"""You are a world-class researcher and presentation designer.

Create a detailed, professional presentation on the topic: '{topic}'

Return ONLY a valid JSON object in this exact format:
{{
  "topic": "{topic}",
  "slides": [
    {{
      "title": "Slide title (max 60 chars)",
      "bullets": [
        "Specific fact or insight with real data/statistics if possible",
        "Clear, informative point that adds value",
        "Actionable or thought-provoking insight"
      ],
      "notes": "Speaker note explaining this slide in 1-2 sentences.",
      "image_query": "a short descriptive phrase for an image that matches this slide"
    }}
  ]
}}

Requirements:
- Generate exactly 8 slides
- Start with an overview slide, end with a conclusion/future outlook slide
- Each bullet must be specific and informative
- Titles must be engaging and descriptive (max 60 chars)
- image_query must be a short 3-6 word phrase suitable for image search (e.g. "solar panels on rooftop")
- Return ONLY the JSON object, no extra text, no markdown, no code fences"""

    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=1500,
            )

            raw = response.choices[0].message.content.strip()

            if "```" in raw:
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
            raw = raw.strip()

            data = json.loads(raw)
            outline = PresentationOutline(**data)
            return outline

        except Exception as e:
            if "rate_limit" in str(e).lower() and attempt < max_retries - 1:
                print(f"Rate limit hit, waiting 30 seconds... (attempt {attempt+1})")
                time.sleep(30)
            else:
                raise e


if __name__ == "__main__":
    outline = build_outline("Climate Change")
    print(f"Topic: {outline.topic}")
    print(f"Number of slides: {len(outline.slides)}")
    for i, slide in enumerate(outline.slides, 1):
        print(f"\nSlide {i}: {slide.title}")
        for bullet in slide.bullets:
            print(f"  • {bullet}")
