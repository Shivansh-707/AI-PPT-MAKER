# 🤖 AI-Powered PPT Maker

An end-to-end AI system that takes a topic as input, autonomously researches it using an LLM, and generates a complete, well-structured Google Slides presentation — all without manual content writing or slide design.

---

## 🎯 Project Overview

This tool automates the entire presentation creation pipeline:

**User Input (Topic)** → **AI Research Agent** → **Structured Content (JSON)** → **Google Slides Generator** → **Shareable Presentation Link**

---

## 🏗️ Architecture

### Two-Phase Pipeline

#### Phase 1: AI Research Agent (research_agent.py)
- Uses Groq LLaMA 3.1 8B Instant to research the given topic
- Generates structured JSON with slide titles, bullet points, and speaker notes
- Validates output using Pydantic models
- Handles malformed JSON with automatic cleanup and retry logic

#### Phase 2: Google Slides Generator (slides_generator.py)
- Authenticates with Google Slides API and Drive API via OAuth 2.0
- Creates a blank presentation using presentations.create()
- Uses batchUpdate() to add slides, insert text, and apply formatting
- Inserts speaker notes into each slide's notes pane
- Shares the presentation publicly and returns the shareable link

#### User Interface (app.py)
- Streamlit web app for easy interaction
- Displays real-time progress with separate spinners for research and generation phases
- Logs and displays time taken for each phase
- Shows slide title preview before generation
- Includes showcase section with 3 sample presentations

---

## 📂 Project Structure

```
ai-ppt-maker/
├── app.py                  # Streamlit UI
├── research_agent.py       # LLM research pipeline
├── slides_generator.py     # Google Slides API logic
├── google_auth.py          # OAuth authentication
├── models.py               # Pydantic data models
├── .env                    # API keys (not in repo)
├── credentials.json        # Google OAuth credentials (not in repo)
├── token.json              # Google auth token (not in repo)
├── .gitignore              # Excludes sensitive files
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

---

## 🚀 Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/ai-ppt-maker.git
cd ai-ppt-maker
```

### 2. Install Dependencies

```bash
pip3 install -r requirements.txt
```

### 3. Set Up Google Cloud

1. Go to https://console.cloud.google.com/
2. Create a new project or select an existing one
3. Enable Google Slides API and Google Drive API
4. Create OAuth 2.0 Client ID credentials:
   - Go to APIs & Services → Credentials
   - Configure OAuth consent screen (External, add your email as test user)
   - Create credentials → OAuth 2.0 Client ID → Desktop app
   - Download the JSON file and save it as credentials.json in the project root

### 4. Get Groq API Key

1. Sign up at https://console.groq.com/
2. Create an API key
3. Create a .env file in the project root:

```
GROQ_API_KEY=your_groq_api_key_here
```

### 5. Run the Application

```bash
python3 -m streamlit run app.py
```

On first run, a browser window will open asking you to authenticate with Google.

---

## 🧠 LLM Choice and Reasoning

### Why Groq LLaMA 3.1 8B Instant?

1. Speed: Groq's LPU inference is extremely fast (~300 tokens/sec), critical for a real-time UI
2. Cost: Free tier with generous daily limits — sufficient for this use case
3. Quality: LLaMA 3.1 8B provides strong reasoning and structured output generation
4. Rate Limit Compatibility: Smaller model consumes fewer tokens per request, avoiding rate limit issues

---

## 📝 Prompt Design

### Strategy

The prompt is designed to:
1. Be explicit about output format — includes a JSON schema example
2. Set quality expectations — specific, data-driven, informative bullets
3. Enforce structure — exactly 8 slides, 3 bullets per slide, speaker notes
4. Prevent hallucination — no markdown, no code fences, only JSON

### Validation

After LLM response:
- Strip markdown code blocks if present
- Parse JSON and validate with Pydantic
- Retry with 30-second backoff on rate limit errors
- Fail gracefully with clear error messages

---

## ⏱️ Performance Benchmarks

| Phase | Avg Time |
|-------|----------|
| AI Research | 3-5 seconds |
| Slide Generation | 4-6 seconds |
| Total | 7-11 seconds |

---

## 📊 Sample Presentations

1. iPhone 14: https://docs.google.com/presentation/d/1SzMPuvTtVGt0Dn7ASVIniBsNRgi4fVgzcXx_IoTAQWk/edit
2. Tiger Breeds and Differences: https://docs.google.com/presentation/d/1_sI-HtEzBEZDVpeRFiiGWuJRDaD12vsUNi-A9hfzLBw/edit
3. Machine Learning vs Deep Learning: https://docs.google.com/presentation/d/16k2I4BDgu5fG0FfshFbDWZko0SfXatkAcEhMXFzmhzo/edit

---

## 🛠️ Error Handling

- Rate limit handling: Automatic retry with exponential backoff
- Malformed JSON: Strips markdown code blocks, validates with Pydantic
- Google API failures: Try-except blocks with user-friendly error messages in Streamlit

---

## 🔒 Security

.gitignore prevents committing sensitive files:
- credentials.json (Google OAuth)
- token.json (Google auth token)
- .env (API keys)

---

## 🎨 Features

- AI-powered research using Groq LLaMA 3.1
- Structured JSON output with validation
- Google Slides creation with formatting
- Speaker notes insertion
- Public sharing with one-click links
- Real-time progress tracking
- Phase-wise time logging
- Streamlit web interface
- Sample presentation showcase

---

## 📈 Future Enhancements

- Web search integration (Tavily/SerpAPI) for live data
- Export as .pptx file
- Custom theme selection
- Image generation and insertion
- Multi-language support

---

## 👤 Author

Shivansh Jha
CSE Final Year Student | Kaggle Enthusiast
