import time
import streamlit as st
from research_agent import build_outline
from slides_generator import create_presentation

st.set_page_config(page_title="AI PPT Maker", page_icon="📊", layout="wide")

st.title("🤖 AI-Powered PPT Maker")
st.markdown("Generate professional Google Slides presentations on any topic using AI")

st.divider()

# Main input section
col1, col2 = st.columns([2, 1])

with col1:
    topic = st.text_input("Enter a topic:", placeholder="e.g., Quantum Computing, Space Exploration")

with col2:
    st.markdown("")
    st.markdown("")
    generate_btn = st.button("🚀 Generate Presentation", type="primary", use_container_width=True)

if generate_btn:
    if not topic.strip():
        st.error("⚠️ Please enter a topic")
    else:
        # Research Phase
        with st.spinner("🔍 Phase 1: Researching topic with AI..."):
            research_start = time.time()
            try:
                outline = build_outline(topic)
                research_time = round(time.time() - research_start, 2)
            except Exception as e:
                st.error(f"❌ Research failed: {str(e)}")
                st.stop()

        st.success(f"✅ Research complete in **{research_time}s** — {len(outline.slides)} slides generated")

        # Preview
        with st.expander("📋 Preview Slide Titles"):
            for i, slide in enumerate(outline.slides, 1):
                st.write(f"{i}. {slide.title}")

        # Generation Phase
        with st.spinner("🎨 Phase 2: Building Google Slides presentation..."):
            generation_start = time.time()
            try:
                link = create_presentation(outline)
                generation_time = round(time.time() - generation_start, 2)
            except Exception as e:
                st.error(f"❌ Slide generation failed: {str(e)}")
                st.stop()

        st.success(f"✅ Slides created in **{generation_time}s**")

        # Timing Summary
        st.info(f"⏱️ Total time: **{round(research_time + generation_time, 2)}s** | Research: **{research_time}s** | Generation: **{generation_time}s**")

        # Result
        st.success("🎉 Presentation created successfully!")
        st.markdown(f"### [🔗 Open in Google Slides]({link})")
        st.code(link, language="text")

st.divider()

# Sample presentations showcase
st.subheader("📚 Sample Presentations")
st.markdown("Check out these AI-generated presentations:")

sample_col1, sample_col2, sample_col3 = st.columns(3)

with sample_col1:
    st.markdown("""
    <div style="padding: 20px; border-radius: 10px; background-color: #f0f2f6; text-align: center;">
        <h4 style="color: #1a1a1a; margin: 0;">📱 iPhone 14</h4>
        <p style="font-size: 14px; color: #1a1a1a; margin-top: 8px;">Comprehensive product overview</p>
    </div>
    """, unsafe_allow_html=True)
    st.link_button("View Presentation", "https://docs.google.com/presentation/d/1SzMPuvTtVGt0Dn7ASVIniBsNRgi4fVgzcXx_IoTAQWk/edit", use_container_width=True)

with sample_col2:
    st.markdown("""
    <div style="padding: 20px; border-radius: 10px; background-color: #f0f2f6; text-align: center;">
        <h4 style="color: #1a1a1a; margin: 0;">🐅 Tiger Breeds</h4>
        <p style="font-size: 14px; color: #1a1a1a; margin-top: 8px;">Breeds and their differences</p>
    </div>
    """, unsafe_allow_html=True)
    st.link_button("View Presentation", "https://docs.google.com/presentation/d/1_sI-HtEzBEZDVpeRFiiGWuJRDaD12vsUNi-A9hfzLBw/edit", use_container_width=True)

with sample_col3:
    st.markdown("""
    <div style="padding: 20px; border-radius: 10px; background-color: #f0f2f6; text-align: center;">
        <h4 style="color: #1a1a1a; margin: 0;">🤖 ML vs Deep Learning</h4>
        <p style="font-size: 14px; color: #1a1a1a; margin-top: 8px;">Technical comparison</p>
    </div>
    """, unsafe_allow_html=True)
    st.link_button("View Presentation", "https://docs.google.com/presentation/d/16k2I4BDgu5fG0FfshFbDWZko0SfXatkAcEhMXFzmhzo/edit", use_container_width=True)

st.divider()
st.caption("Powered by Groq LLaMA 3.1 8B + Google Slides API")
