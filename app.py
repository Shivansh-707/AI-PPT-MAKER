import streamlit as st
import time
from research_agent import build_outline
from slides_generator import create_presentation

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI PPT Maker",
    page_icon="📊",
    layout="wide",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Main background */
    .stApp { background-color: #0f1117; }

    /* Hide default header */
    #MainMenu, footer, header { visibility: hidden; }

    /* Hero section */
    .hero {
        text-align: center;
        padding: 3rem 1rem 1.5rem 1rem;
    }
    .hero h1 {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea, #764ba2, #f093fb);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .hero p {
        color: #9ca3af;
        font-size: 1.1rem;
        margin-top: 0;
    }

    /* Input card */
    .input-card {
        background: #1a1d27;
        border: 1px solid #2d2f3e;
        border-radius: 16px;
        padding: 2rem;
        margin: 1rem auto;
        max-width: 700px;
    }

    /* Sample links card */
    .sample-card {
        background: #1a1d27;
        border: 1px solid #2d2f3e;
        border-radius: 12px;
        padding: 1.2rem 1.5rem;
        margin: 0.5rem 0;
        transition: border-color 0.2s;
    }
    .sample-card:hover { border-color: #667eea; }

    /* Result card */
    .result-card {
        background: linear-gradient(135deg, #1a1d27, #12151f);
        border: 1px solid #667eea;
        border-radius: 16px;
        padding: 2rem;
        text-align: center;
        margin-top: 1.5rem;
    }
    .result-card a {
        display: inline-block;
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white !important;
        padding: 0.8rem 2rem;
        border-radius: 50px;
        text-decoration: none;
        font-weight: 600;
        font-size: 1.1rem;
        margin-top: 1rem;
    }

    /* Stats bar */
    .stat-box {
        background: #12151f;
        border: 1px solid #2d2f3e;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
    }
    .stat-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #667eea;
    }
    .stat-label {
        font-size: 0.75rem;
        color: #6b7280;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #12151f;
        border-right: 1px solid #2d2f3e;
    }
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stTextInput label,
    [data-testid="stSidebar"] .stCheckbox label {
        color: #9ca3af !important;
        font-size: 0.85rem;
    }

    /* Generate button */
    .stButton > button {
        background: linear-gradient(135deg, #667eea, #764ba2) !important;
        color: white !important;
        border: none !important;
        border-radius: 50px !important;
        padding: 0.75rem 2rem !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
        width: 100% !important;
        transition: opacity 0.2s !important;
    }
    .stButton > button:hover { opacity: 0.9 !important; }

    /* Text input */
    .stTextInput input {
        background: #12151f !important;
        border: 1px solid #2d2f3e !important;
        border-radius: 10px !important;
        color: white !important;
        font-size: 1rem !important;
        padding: 0.75rem !important;
    }
    .stTextInput input:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 2px rgba(102,126,234,0.2) !important;
    }

    /* Feature pills */
    .feature-pill {
        display: inline-block;
        background: #1a1d27;
        border: 1px solid #2d2f3e;
        border-radius: 50px;
        padding: 0.3rem 0.9rem;
        font-size: 0.8rem;
        color: #9ca3af;
        margin: 0.2rem;
    }

    /* Divider */
    hr { border-color: #2d2f3e !important; }
</style>
""", unsafe_allow_html=True)

# ── Hero Section ──────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <h1>📊 AI PPT Maker</h1>
    <p>Enter any topic — AI researches it and builds a complete Google Slides presentation for you.</p>
    <div style="margin-top: 1rem;">
        <span class="feature-pill">🤖 Gemini AI</span>
        <span class="feature-pill">🖼️ Auto Images</span>
        <span class="feature-pill">🎨 4 Themes</span>
        <span class="feature-pill">📝 Speaker Notes</span>
        <span class="feature-pill">⚡ ~30s</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    st.markdown("---")

    theme = st.selectbox(
        "🎨 Slide Theme",
        ["Default (No Theme)", "Minimal", "Dark", "Corporate"],
        index=3,
    )

    st.markdown("")

    image_url = st.text_input(
        "🖼️ Title Hero Image URL",
        placeholder="https://example.com/image.jpg",
        help="Optional: Custom image shown on the title slide"
    )

    st.markdown("")

    use_images = st.checkbox("✅ Auto-fetch slide images", value=True,
                              help="Fetches a relevant image per slide from Pexels")

    st.markdown("---")
    st.markdown("### 📂 Sample Presentations")

    samples = [
        ("🤖 Artificial Intelligence", "https://docs.google.com/presentation/d/1xyuyFPyGRLGeHjKMBxVCGg-oebCIjdjyqhgaf6kHa8M/edit"),
        ("🐯 Tigers & Their Breeds",   "https://docs.google.com/presentation/d/1NAG9e-MIddYbDHAZqUwpipotgtgeZiUwsvGD7L-uWfk/edit"),
        ("📱 Mobile Phones",            "https://docs.google.com/presentation/d/15C2QzbSTK1JD6sGBsWT1-B_KSIhJyFSXErszC6EeH3Q/edit"),
    ]
    for label, link in samples:
        st.markdown(f"[{label}]({link})")

    st.markdown("---")
    st.caption("Built with Gemini · Google Slides API · Pexels")

# ── Main Input ────────────────────────────────────────────────────────────────
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    topic = st.text_input(
        "",
        placeholder="✏️  Enter a topic  (e.g. Climate Change, Machine Learning...)",
        label_visibility="collapsed"
    )
    st.markdown("")
    generate_btn = st.button("🚀  Generate Presentation", use_container_width=True)

st.markdown("---")

# ── Generation Logic ──────────────────────────────────────────────────────────
if generate_btn:
    if not topic.strip():
        st.warning("⚠️ Please enter a topic before generating.")
    else:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            # Phase 1
            with st.status("🔍 Phase 1: Researching topic with Gemini...", expanded=True) as status:
                research_start = time.time()
                try:
                    outline = build_outline(topic.strip())
                    research_elapsed = time.time() - research_start
                    status.update(
                        label=f"✅ Research complete — {len(outline.slides)} slides planned  ({research_elapsed:.1f}s)",
                        state="complete",
                    )
                except Exception as e:
                    status.update(label="❌ Research failed", state="error")
                    st.error(f"Research error: {e}")
                    st.stop()

            # Phase 2
            with st.status("🛠️ Phase 2: Building Google Slides...", expanded=True) as status:
                gen_start = time.time()
                try:
                    link = create_presentation(
                        outline,
                        theme=theme,
                        image_url=image_url,
                        use_images=use_images,
                    )
                    gen_elapsed = time.time() - gen_start
                    status.update(
                        label=f"✅ Slides built  ({gen_elapsed:.1f}s)",
                        state="complete",
                    )
                except Exception as e:
                    status.update(label="❌ Slide generation failed", state="error")
                    st.error(f"Slide generation error: {e}")
                    st.stop()

            total_elapsed = research_elapsed + gen_elapsed

            # ── Stats ─────────────────────────────────────────────────────────
            st.markdown("")
            s1, s2, s3 = st.columns(3)
            with s1:
                st.markdown(f"""
                <div class="stat-box">
                    <div class="stat-value">{len(outline.slides)}</div>
                    <div class="stat-label">Slides</div>
                </div>""", unsafe_allow_html=True)
            with s2:
                st.markdown(f"""
                <div class="stat-box">
                    <div class="stat-value">{total_elapsed:.1f}s</div>
                    <div class="stat-label">Total Time</div>
                </div>""", unsafe_allow_html=True)
            with s3:
                st.markdown(f"""
                <div class="stat-box">
                    <div class="stat-value">{research_elapsed:.1f}s</div>
                    <div class="stat-label">Research</div>
                </div>""", unsafe_allow_html=True)

            # ── Result Card ───────────────────────────────────────────────────
            st.markdown(f"""
            <div class="result-card">
                <div style="font-size: 2.5rem;">🎉</div>
                <div style="color: white; font-size: 1.3rem; font-weight: 700; margin-top: 0.5rem;">
                    Your Presentation is Ready!
                </div>
                <div style="color: #9ca3af; font-size: 0.9rem; margin-top: 0.3rem;">
                    Topic: {topic.strip()}  ·  Theme: {theme}
                </div>
                <a href="{link}" target="_blank">📂 Open in Google Slides →</a>
            </div>
            """, unsafe_allow_html=True)

            # ── Slide Outline ─────────────────────────────────────────────────
            st.markdown("")
            st.markdown("### 📋 Generated Outline")
            for j, slide in enumerate(outline.slides, start=1):
                with st.expander(f"Slide {j} — {slide.title}"):
                    for bullet in slide.bullets:
                        st.markdown(f"- {bullet}")
                    if slide.notes:
                        st.caption(f"📝 {slide.notes}")
