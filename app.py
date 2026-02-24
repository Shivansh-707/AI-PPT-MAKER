import streamlit as st
import time
from research_agent import build_outline
from slides_generator import create_presentation, THEME_STYLES

st.set_page_config(
    page_title="AI PPT Maker",
    page_icon="📊",
    layout="wide"
)

# ── Header ────────────────────────────────────────────────────────────────────
st.title("📊 AI-Powered PPT Maker")
st.markdown("Generate a complete Google Slides presentation on any topic using AI.")

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Settings")

    theme = st.selectbox(
        "🎨 Theme",
        options=list(THEME_STYLES.keys()),
        index=0,
    )

    num_slides = st.slider(
        "📄 Number of Slides",
        min_value=5,
        max_value=15,
        value=8,
        step=1,
        help="How many content slides to generate (excluding title slide)"
    )

    use_images = st.toggle("🖼️ Include Images", value=True)

    image_url = st.text_input(
        "🖼️ Hero Image URL (optional)",
        placeholder="https://example.com/image.jpg",
        help="Custom image for the title slide"
    )

    st.divider()

    st.markdown("### 📂 Sample Presentations")
    samples = [
        ("💹 Finance and Trading",  "https://docs.google.com/presentation/d/1fFEAcrLw1er6roRHJp8_efrHwij42nekzlpzzhebYcw/edit"),
        ("🎲 Probability and Luck", "https://docs.google.com/presentation/d/12vE_Ljbli4W9PZBmCNEs9OfxuX_akbUpkZhiT2CfYAY/edit"),
        ("🤖 AI and Robotics",      "https://docs.google.com/presentation/d/1CqzqQX1IcbGzTQRPj4RdTRmBiJRAY3C8kqOH47C6QwA/edit"),
    ]
    for label, url in samples:
        st.markdown(f"[{label}]({url})")

# ── Main Input ────────────────────────────────────────────────────────────────
topic = st.text_input(
    "🔍 Enter a Topic",
    placeholder="e.g. Quantum Computing, Climate Change, Blockchain...",
)

generate_btn = st.button("🚀 Generate Presentation", type="primary", use_container_width=True)

# ── Generation ────────────────────────────────────────────────────────────────
if generate_btn:
    if not topic.strip():
        st.warning("⚠️ Please enter a topic first.")
    else:
        # Phase 1 — Research
        with st.status("🧠 Researching topic with AI...", expanded=True) as status:
            try:
                t1 = time.time()
                outline = build_outline(topic.strip(), num_slides=num_slides)
                t2 = time.time()
                research_time = round(t2 - t1, 1)
                status.update(
                    label=f"✅ Research complete — {len(outline.slides)} slides planned ({research_time}s)",
                    state="complete"
                )
            except Exception as e:
                status.update(label="❌ Research failed", state="error")
                st.error(f"Research error: {e}")
                st.stop()

        # Phase 2 — Slide Generation
        with st.status("🎨 Generating slides...", expanded=True) as status:
            try:
                t3 = time.time()
                link = create_presentation(
                    outline,
                    theme=theme,
                    image_url=image_url,
                    use_images=use_images,
                )
                t4 = time.time()
                generation_time = round(t4 - t3, 1)
                status.update(
                    label=f"✅ Slides generated ({generation_time}s)",
                    state="complete"
                )
            except Exception as e:
                status.update(label="❌ Slide generation failed", state="error")
                st.error(f"Slide generation error: {e}")
                st.stop()

        # ── Result ────────────────────────────────────────────────────────────
        st.success("🎉 Your presentation is ready!")
        st.markdown(f"### 🔗 [Open in Google Slides]({link})")

        col1, col2, col3 = st.columns(3)
        col1.metric("📄 Slides",          len(outline.slides))
        col2.metric("⏱️ Research Time",   f"{research_time}s")
        col3.metric("⏱️ Generation Time", f"{generation_time}s")

        st.markdown("---")
        st.markdown("**Slide Outline:**")
        for i, slide in enumerate(outline.slides, start=1):
            with st.expander(f"Slide {i}: {slide.title}"):
                if slide.table:
                    st.markdown("📊 **Table Slide**")
                    st.write(f"Headers: {slide.table.headers}")
                else:
                    for bullet in slide.bullets:
                        st.markdown(f"• {bullet}")
                if slide.notes:
                    st.caption(f"📝 Notes: {slide.notes}")
