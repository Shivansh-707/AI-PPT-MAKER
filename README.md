# 📊 AI-Powered PPT Maker

An end-to-end AI tool that takes a topic as input, autonomously researches it using Google Gemini, and generates a complete, well-structured Google Slides presentation — fully automated, no manual writing or design required.

---

## 🚀 Sample Presentations

- 🔗 [Artificial Intelligence](https://docs.google.com/presentation/d/1xyuyFPyGRLGeHjKMBxVCGg-oebCIjdjyqhgaf6kHa8M/edit)
- 🔗 [Tigers and Their Breeds](https://docs.google.com/presentation/d/1NAG9e-MIddYbDHAZqUwpipotgtgeZiUwsvGD7L-uWfk/edit)
- 🔗 [Mobile Phones](https://docs.google.com/presentation/d/15C2QzbSTK1JD6sGBsWT1-B_KSIhJyFSXErszC6EeH3Q/edit)

---

## 🧠 How It Works

The system follows a **two-phase AI pipeline**:

### Phase 1 — AI Research Agent
- Takes a topic as input
- Uses **Google Gemini** to research the topic and generate structured slide content
- Outputs a validated JSON outline: titles, bullet points, speaker notes, and image queries per slide

### Phase 2 — Google Slides Generator
- Authenticates with **Google Slides API** via a Service Account
- Creates a blank presentation and maps AI content onto slides
- Fetches **per-slide images** from **Pexels API** based on each slide's topic
- Applies theme-based formatting (colors, fonts, layout)
- Shares the deck publicly and returns a shareable link

---

## ✨ Features

- 🤖 **AI Research** — Gemini researches any topic and structures it into slides
- 🎨 **4 Themes** — Default, Minimal, Dark, Corporate
- 🖼️ **Auto Images** — Per-slide images auto-fetched from Pexels (toggleable)
- 🖼️ **Hero Image** — Optional custom image URL for the title slide
- 📝 **Speaker Notes** — Auto-generated notes on every slide
- ⏱️ **Time Logging** — Displays research time + generation time separately
- 🔗 **Shareable Link** — Returns a public Google Slides link instantly
- 🧹 **No Overlap** — Text and images are precisely split left/right per slide

---

## 🗂️ Project Structure

```
ppt-maker-ai/
│
├── app.py                  # Streamlit UI
├── research_agent.py       # Phase 1 — Gemini AI research + outline generation
├── slides_generator.py     # Phase 2 — Google Slides API slide creation
├── image_search.py         # Pexels API image fetcher
├── models.py               # Pydantic models (PresentationOutline, SlideContent)
├── google_auth.py          # Google Slides + Drive API authentication
├── requirements.txt        # Python dependencies
├── .env                    # API keys (not committed)
├── credentials.json        # Google Service Account credentials (not committed)
└── README.md
```

---

## ⚙️ Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/Shivansh-707/AI-PPT-MAKER.git
cd AI-PPT-MAKER
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set up Google Cloud
- Go to [Google Cloud Console](https://console.cloud.google.com/)
- Enable **Google Slides API** and **Google Drive API**
- Create a **Service Account** and download `credentials.json`
- Place `credentials.json` in the project root

### 4. Set up environment variables
Create a `.env` file in the root:
```env
GEMINI_API_KEY=your_gemini_api_key_here
PEXELS_API_KEY=your_pexels_api_key_here
```

- Get Gemini API key → [Google AI Studio](https://aistudio.google.com/)
- Get Pexels API key → [Pexels API](https://www.pexels.com/api/)

### 5. Run the app
```bash
streamlit run app.py
```

---

## 🤖 LLM Used — Google Gemini

**Why GROQ?**
- Free tier is generous — no billing required for this project
- Have been personally using this for quite a while, really love the accurate response
- Native JSON mode makes structured slide output reliable
- Fast response times suitable for real-time generation

**Prompt Design:**
The research prompt instructs Gemini to return a strict JSON structure with `topic`, and a `slides` array — each slide containing `title`, `bullets` (3–5 points), `notes`, and `image_query`. Pydantic validation ensures no malformed output reaches the Slides API.

---

## 🧪 Testing

Tested with 3+ topics of varying complexity:
- ✅ AI-generated content is accurate and well-structured
- ✅ Slide formatting is consistent across all themes
- ✅ Images placed without overlapping text
- ✅ Speaker notes generated on every slide
- ✅ Shareable Google Slides link returned every time

---

## 📦 Requirements

```
streamlit
google-api-python-client
google-auth
google-generativeai
pydantic
requests
python-dotenv
```

Install all with:
```bash
pip install -r requirements.txt
```

---

## 🔒 Environment Variables

| Variable | Description |
|---|---|
| `GROQ_API_KEY` | GROQ API key |
| `PEXELS_API_KEY` | Pexels image search API key |

Never commit `.env` or `credentials.json` to GitHub.

---

## 📄 License

MIT License — free to use and modify.
