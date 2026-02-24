# 📊 AI-Powered PPT Maker

An end-to-end AI tool that takes a topic as input, autonomously researches it using **Groq API (LLaMA 3.3 70B)**, and generates a complete, well-structured Google Slides presentation — fully automated, no manual writing or design required.

---

## 🚀 Sample Presentations

| Topic | Link |
|---|---|
| 💹 Finance and Trading | [Open Presentation](https://docs.google.com/presentation/d/1fFEAcrLw1er6roRHJp8_efrHwij42nekzlpzzhebYcw/edit) |
| 🎲 Probability and Luck | [Open Presentation](https://docs.google.com/presentation/d/12vE_Ljbli4W9PZBmCNEs9OfxuX_akbUpkZhiT2CfYAY/edit) |
| 🤖 AI and Robotics | [Open Presentation](https://docs.google.com/presentation/d/1CqzqQX1IcbGzTQRPj4RdTRmBiJRAY3C8kqOH47C6QwA/edit) |

---

## 🧠 How It Works

The system follows a **two-phase AI pipeline**:

### Phase 1 — AI Research Agent
- Takes a topic as input from the user
- Uses **Groq API (LLaMA 3.3 70B)** to deeply research the topic
- Generates a structured JSON outline: titles, detailed bullet points (15–25 words each), speaker notes, image queries, and optional table data per slide
- Validates the output using **Pydantic** models before passing it downstream

### Phase 2 — Google Slides Generator
- Authenticates with **Google Slides API** via a Service Account
- Creates a blank presentation and deletes the default slide
- Maps AI-generated content onto slides with consistent formatting
- Fetches **per-slide images** automatically from **Pexels API**
- Builds **tables** (pros/cons, comparisons, metrics) on relevant slides
- Applies theme-based formatting: background colors, title colors, body text colors, table header colors
- Shares the deck publicly via **Google Drive API**
- Returns a shareable Google Slides link instantly

---

## ✨ Features

- ⚡ **Groq AI Research** — LLaMA 3.3 70B researches any topic and structures it into detailed slides
- 🎨 **4 Themes** — Default, Minimal, Dark, Corporate
- 🖼️ **Auto Images** — Per-slide images auto-fetched from Pexels (toggleable)
- 🖼️ **Hero Image** — Optional custom image URL for the title slide
- 📊 **Auto Tables** — Pros/cons and comparison tables auto-generated on relevant slides
- 📝 **Speaker Notes** — Detailed auto-generated notes on every slide
- ⏱️ **Time Logging** — Displays research time + generation time separately
- 🔗 **Shareable Link** — Returns a public Google Slides link instantly
- 🧹 **No Overlap** — Text and images are precisely split left/right per slide
- ✌🏻 **Number Of Slides** - User can select the number of slides he wants 

---

## 🗂️ Project Structure

```
ppt-maker-ai/
│
├── app.py                  # Streamlit UI
├── research_agent.py       # Phase 1 — Groq AI research + outline generation
├── slides_generator.py     # Phase 2 — Google Slides API slide creation
├── image_search.py         # Pexels API image fetcher
├── models.py               # Pydantic models (PresentationOutline, SlideContent, TableData)
├── google_auth.py          # Google Slides + Drive API authentication
├── requirements.txt        # Python dependencies
├── .env                    # API keys (NOT committed to GitHub)
├── credentials.json        # Google Service Account key (NOT committed to GitHub)
├── .gitignore              # Ignores .env, credentials.json, token.json
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

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select existing)
3. Enable **Google Slides API** and **Google Drive API**
4. Go to **IAM & Admin → Service Accounts**
5. Create a new Service Account
6. Click on it → **Keys → Add Key → Create new key → JSON**
7. Download the JSON file and rename it to `credentials.json`
8. Place `credentials.json` in the project root

### 4. Set up environment variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
PEXELS_API_KEY=your_pexels_api_key_here
```

- Get Groq API key → [Groq Console](https://console.groq.com/)
- Get Pexels API key → [Pexels API](https://www.pexels.com/api/)

### 5. Run the app
```bash
streamlit run app.py
```

---

## 🔑 Configuration Files

### `.env` — should look like this:
```env
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
PEXELS_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### `credentials.json` — should look like this:
```json
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "private_key": "-----BEGIN RSA PRIVATE KEY-----\nXXXXXX\n-----END RSA PRIVATE KEY-----\n",
  "client_email": "your-service-account@your-project-id.iam.gserviceaccount.com",
  "client_id": "xxxxxxxxxxxxxxxxxxxx",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/your-service-account%40your-project-id.iam.gserviceaccount.com"
}
```

> ⚠️ **Never share or commit these files to GitHub.**

---

## 🤖 LLM Used — Groq API (LLaMA 3.3 70B)

**Why Groq?**
- Extremely fast inference — significantly faster than most LLM providers
- Free tier available — no billing required for this project
- LLaMA 3.3 70B produces high quality, detailed, structured JSON output reliably

**Prompt Design:**

The research prompt instructs the model to return a strict JSON structure:
```json
{
  "topic": "Topic Title",
  "slides": [
    {
      "title": "Slide Title",
      "bullets": ["15-25 word detailed bullet", "..."],
      "notes": "2-3 sentence speaker notes",
      "image_query": "pexels search term",
      "table": null
    },
    {
      "title": "Pros and Cons",
      "bullets": [],
      "notes": "Speaker notes for table slide",
      "image_query": "",
      "table": {
        "headers": ["Pros", "Cons"],
        "rows": [["Point 1", "Point 1"], ["Point 2", "Point 2"]]
      }
    }
  ]
}
```

**Pydantic validation** ensures no malformed output reaches the Slides API — if the LLM returns invalid JSON, the error is caught and reported cleanly.

---

## 🎨 Available Themes

| Theme | Background | Best For |
|---|---|---|
| Default | White (Google default) | General use |
| Minimal | Off-white | Clean, simple decks |
| Dark | Near-black | Tech, modern topics |
| Corporate | Light blue-grey | Business presentations |


---

## 🧪 Testing

Tested with 3+ topics of varying complexity:
- ✅ AI-generated content is accurate, detailed, and well-structured
- ✅ Slide formatting is consistent across all 6 themes
- ✅ Images placed on right half without overlapping text
- ✅ Tables render correctly with theme-matched header colors
- ✅ Dark theme table text is white and fully readable
- ✅ Speaker notes generated on every slide
- ✅ Shareable Google Slides link returned every time

---

## 📦 Requirements

```
streamlit
google-api-python-client
google-auth
groq
pydantic
requests
python-dotenv
```

Install all with:
```bash
pip install -r requirements.txt
```

---

## 🔒 Security

| File | What it contains | Committed to GitHub? |
|---|---|---|
| `.env` | Groq + Pexels API keys | ❌ Never |
| `credentials.json` | Google Service Account private key | ❌ Never |
| `token.json` | OAuth token (if generated) | ❌ Never |

Make sure your `.gitignore` contains:
```
.env
credentials.json
token.json
__pycache__/
*.pyc
```

---

## 📄 License

MIT License — free to use and modify.
