import streamlit as st
import plotly.graph_objects as go
from resume_parser import extract_text_from_pdf
from comparator import compare_resume_with_jd

st.set_page_config(page_title="Resume Radar Pro", page_icon="🎯", layout="wide")

if 'light_theme' not in st.session_state:
    st.session_state.light_theme = False

def load_css():
    if st.session_state.light_theme:
        theme_css = """
        <style>
        .stApp { background-color: #ffffff; color: #000000; }
        .main-header { text-align: center; padding: 2rem 0; background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 10px; margin-bottom: 2rem; }
        .metric-card { background: #f8f9fa; color: #000000; padding: 1.5rem; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); text-align: center; margin: 1rem 0; border: 1px solid #dee2e6; }
        .upload-card { background: #f8f9fa; color: #000000; padding: 2rem; border-radius: 10px; border: 2px dashed #dee2e6; text-align: center; margin: 1rem 0; min-height: 200px; }
        .upload-card h3, .upload-card p { color: #000000 !important; }
        .stFileUploader label, .stTextArea label { color: #000000 !important; }
        .stFileUploader div[data-testid="stFileUploadDropzone"] { background-color: #ffffff !important; border: 2px dashed #007bff !important; color: #000000 !important; }
        .stTextArea textarea { background-color: #ffffff !important; color: #000000 !important; border: 1px solid #dee2e6 !important; }
        .matched-skill { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .missing-skill { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        .stButton > button { background: linear-gradient(90deg, #667eea 0%, #764ba2 100%) !important; color: white !important; border: none !important; border-radius: 25px !important; padding: 0.75rem 2rem !important; font-weight: 600 !important; font-size: 16px !important; }
        </style>
        """
    else:
        theme_css = """
        <style>
        .stApp { background-color: #0e1117; color: #ffffff; }
        .main-header { text-align: center; padding: 2rem 0; background: linear-gradient(90deg, #1f4e79 0%, #2d1b69 100%); color: white; border-radius: 10px; margin-bottom: 2rem; }
        .metric-card { background: #262730; color: #ffffff; padding: 1.5rem; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.3); text-align: center; margin: 1rem 0; border: 1px solid #404040; }
        .upload-card { background: #262730; color: #ffffff; padding: 2rem; border-radius: 10px; border: 2px dashed #404040; text-align: center; margin: 1rem 0; min-height: 200px; }
        .upload-card h3, .upload-card p { color: #ffffff !important; }
        .stFileUploader label, .stTextArea label { color: #ffffff !important; }
        .stFileUploader div[data-testid="stFileUploadDropzone"] { background-color: #1e1e1e !important; border: 2px dashed #ffc107 !important; color: #ffffff !important; }
        .stTextArea textarea { background-color: #1e1e1e !important; color: #ffffff !important; border: 1px solid #404040 !important; }
        .matched-skill { background: #1e4620; color: #4caf50; border: 1px solid #2e7d32; }
        .missing-skill { background: #4a1e1e; color: #f44336; border: 1px solid #d32f2f; }
        .stButton > button { background: linear-gradient(90deg, #1f4e79 0%, #2d1b69 100%) !important; color: white !important; border: none !important; border-radius: 25px !important; padding: 0.75rem 2rem !important; font-weight: 600 !important; font-size: 16px !important; }
        </style>
        """
    
    st.markdown(theme_css + """
    <style>
    .skill-tag { display: inline-block; padding: 0.3rem 0.8rem; margin: 0.2rem; border-radius: 20px; font-size: 0.85rem; font-weight: 500; }
    .block-container { padding-top: 2rem !important; }
    .main > div { padding-top: 1rem !important; }
    </style>
    """, unsafe_allow_html=True)

def render_header():
    theme_text = "🌙" if not st.session_state.light_theme else "☀️"

    st.markdown(f'''
    <div class="main-header" style="position: relative; margin-top: 1rem;">
        <div style="position: absolute; top: 20px; right: 25px; font-size: 20px; cursor: pointer; z-index: 10; background: rgba(255,255,255,0.2); padding: 8px; border-radius: 50%; backdrop-filter: blur(10px);">
            {theme_text}
        </div>
        <h1> Resume Radar Pro</h1>
        <p>AI-Powered Resume Analysis & Job Matching Platform</p>
    </div>
    ''', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 6, 1])
    with col3:
        if st.button("🔄", help="Toggle Theme", key="theme_btn"):
            st.session_state.light_theme = not st.session_state.light_theme
            st.rerun()

def render_upload_section():
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="upload-card"><h3>Upload Resume</h3><p>Drag and drop your PDF file or click to browse</p>', unsafe_allow_html=True)
        uploaded_file = st.file_uploader("Choose PDF file", type="pdf", key="resume", help="Drag and drop your resume PDF file here", label_visibility="collapsed")
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="upload-card"><h3>Job Description</h3><p>Paste or type the job description below</p>', unsafe_allow_html=True)
        job_description = st.text_area("Job Description", height=120, placeholder="Paste job description here...", key="jd", label_visibility="collapsed")
        st.markdown("</div>", unsafe_allow_html=True)

    return uploaded_file, job_description

def render_results(results):
    col1, col2, col3, col4 = st.columns(4)

    metrics = [
        (results.get('match_score', 0), "Overall Match", "#667eea"),
        (results.get('skill_match_percentage', 0), "Skill Match", "#28a745"),
        (len(results.get('matched_skills', [])), "Matched Skills", "#17a2b8"),
        (len(results.get('missing_skills', [])), "Missing Skills", "#dc3545")
    ]

    for i, (value, label, color) in enumerate(metrics):
        with [col1, col2, col3, col4][i]:
            st.markdown(f'<div class="metric-card"><h2 style="color: {color}; margin: 0;">{value}{"%" if i < 2 else ""}</h2><p style="margin: 0;">{label}</p></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.markdown("### 🔍 Skills Analysis")

        if results.get('matched_skills'):
            st.markdown("**✅ Skills You Have:**")
            skills_html = "".join([f'<span class="skill-tag matched-skill">{skill.title()}</span>' for skill in results['matched_skills']])
            st.markdown(skills_html, unsafe_allow_html=True)
        else:
            st.warning("⚠️ No matching skills found between your resume and this job description.")

        st.markdown("<br>", unsafe_allow_html=True)

        if results.get('missing_skills'):
            st.markdown("**❌ Skills to Develop:**")
            skills_html = "".join([f'<span class="skill-tag missing-skill">{skill.title()}</span>' for skill in results['missing_skills'][:10]])
            st.markdown(skills_html, unsafe_allow_html=True)
        else:
            st.success("🎉 Amazing! You have all the required skills for this position!")

        st.markdown("<br><br>", unsafe_allow_html=True)

        st.markdown("### 📋 Job Requirements Summary")
        for req in results.get("jd_summary", {}).get("requirements", []):
            st.markdown(f"• {req}")

        st.markdown("### 💡 Improvement Suggestions")
        for suggestion in results.get("suggestions", []):
            st.info(suggestion)

    with col_right:
        st.markdown("### 📊 Match Visualization")
        skill_match_pct = results.get('skill_match_percentage', 0)

        fig = go.Figure(data=[go.Pie(labels=['Skills Match', 'Skills Gap'], values=[skill_match_pct, 100 - skill_match_pct], hole=0.6, marker_colors=['#28a745', '#dc3545'], textinfo='none')])
        fig.add_annotation(text=f"<b>{skill_match_pct:.0f}%</b><br><span style='font-size:14px'>Match Rate</span>", x=0.5, y=0.5, font_size=28, showarrow=False)
        fig.update_layout(height=300, showlegend=True, legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5), margin=dict(t=20, b=20, l=20, r=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("### 📈 Quick Stats")
        rating = 'Excellent' if skill_match_pct >= 80 else 'Good' if skill_match_pct >= 60 else 'Needs Improvement'
        st.markdown(f"- **Total JD Skills:** {results.get('total_jd_skills', 0)}\n- **Skills You Have:** {len(results.get('matched_skills', []))}\n- **Skills to Learn:** {len(results.get('missing_skills', []))}\n- **Match Rating:** {rating}")

def main():
    load_css()
    render_header()

    uploaded_file, job_description = render_upload_section()

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        submit_clicked = st.button("Analyze Resume", type="primary", use_container_width=True, disabled=not (uploaded_file and job_description))

    if (uploaded_file and job_description) and submit_clicked:
        with st.spinner("🔍 Analyzing your resume..."):
            resume_text = extract_text_from_pdf(uploaded_file)
            results = compare_resume_with_jd(resume_text, job_description)
        st.markdown("---")
        render_results(results)
    else:
        text_color = "#333333" if st.session_state.light_theme else "#ffffff"
        subtitle_color = "#666666" if st.session_state.light_theme else "#cccccc"
        st.markdown(f'<div style="text-align: center; padding: 3rem; color: {text_color};"><h3 style="color: {text_color};">Get Started</h3><p style="color: {subtitle_color};">Upload your resume and paste a job description to begin the analysis</p></div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
