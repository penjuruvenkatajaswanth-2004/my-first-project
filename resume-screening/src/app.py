

import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import os
from resume_parser import ResumeParser, display_parsed_resume
from skill_matcher import SkillMatcher, display_job_skills, display_candidate_ranking, display_comparison_table  




# Set page configuration
st.set_page_config(
    page_title="AI Resume Screening System",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #ff7f0e;
        margin-bottom: 1rem;
    }
    .info-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Main header
    st.markdown('<h1 class="main-header"> AI Resume Screening System</h1>', unsafe_allow_html=True)
    
    # Subtitle
    st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666;">Intelligent candidate shortlisting powered by AI</p>', unsafe_allow_html=True)
    
    # Main content area
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<h2 class="sub-header">Welcome to Your AI Recruiting Assistant</h2>', unsafe_allow_html=True)
        
        # Info box
        st.markdown("""
        <div class="info-box">
            <h3>What this system can do:</h3>
            <ul>
                <li>📊 Analyze and parse resumes (PDF, DOCX)</li>
                <li>🎯 Extract skills, experience, and qualifications</li>
                <li>⚡ Rank candidates based on job requirements</li>
                <li>📈 Reduce manual screening time by 80%</li>
                <li>🎯 Improve hiring accuracy with AI insights</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        # Upload section
        st.markdown('<h3 class="sub-header">📁 Upload Job Description</h3>', unsafe_allow_html=True)
        
        job_description = st.text_area(
            "Paste the job description here:",
            height=150,
            placeholder="Enter the job requirements, skills needed, and job description..."
        )
        
        # File upload for resumes
        st.markdown('<h3 class="sub-header">📄 Upload Resumes</h3>', unsafe_allow_html=True)
        
        uploaded_files = st.file_uploader(
            "Choose resume files (PDF, DOCX)",
            type=['pdf', 'docx'],
            accept_multiple_files=True,
            help="Upload multiple resume files to screen against the job description"
        )
        
        # Action buttons
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            if st.button("🔍 Start Screening", type="primary", use_container_width=True):
                if job_description and uploaded_files:
                    st.success("✅ Processing resumes and analyzing matches...")
                    
                    # Initialize parsers
                    parser = ResumeParser()
                    skill_matcher = SkillMatcher()
                    
                    # Process each uploaded file
                    st.markdown("## 📊 Resume Analysis Results")
                    st.info(f"📁 Processing {len(uploaded_files)} resume file(s)...")
                    
                    all_parsed_resumes = []
                    for i, uploaded_file in enumerate(uploaded_files):
                        st.markdown(f"---")
                        st.markdown(f"**📄 Resume #{i+1}: {uploaded_file.name}**")
                        parsed_data = parser.parse_resume(uploaded_file)
                        display_parsed_resume(parsed_data)
                        all_parsed_resumes.append(parsed_data)
                    
                    st.success(f"✅ Successfully processed {len(uploaded_files)} resume(s)!")
                    
                    # Store results in session state for the View Results button
                    st.session_state.parsed_resumes = all_parsed_resumes
                    st.session_state.job_description = job_description
                    st.session_state.job_skills = skill_matcher.extract_job_skills(job_description)
                    st.session_state.ranked_candidates = skill_matcher.rank_candidates(all_parsed_resumes, job_description)
                    
                    # Debug information
                    st.markdown("---")
                    st.markdown("**🔍 Debug Information:**")
                    st.write(f"**Total resumes processed:** {len(all_parsed_resumes)}")
                    st.write(f"**Resume filenames:** {[r.get('filename', 'Unknown') for r in all_parsed_resumes]}")
                    st.write(f"**Total candidates ranked:** {len(st.session_state.ranked_candidates)}")
                    
                    st.success(f"🎯 Screening completed! {len(all_parsed_resumes)} resume(s) analyzed. Click 'View Results' to see detailed ranking.")
                    
                    # Note about score consistency
                    st.info("💡 **Note:** Scores are now based on: Skill Match + Experience Bonus (up to +15) + Education Bonus (up to +10) + Skills Diversity Bonus (up to +10). This ensures different resumes get different scores based on their actual qualifications.")
                    
                else:
                    st.error("❌ Please provide both job description and resume files.")
        
        with col_btn2:
            if st.button("📊 View Results", use_container_width=True):
                if hasattr(st.session_state, 'ranked_candidates') and st.session_state.ranked_candidates:
                    st.markdown("## 🏆 AI-Powered Candidate Ranking Results")
                    
                    # Display job skills analysis
                    display_job_skills(st.session_state.job_skills)
                    
                    # Display candidate ranking
                    display_candidate_ranking(st.session_state.ranked_candidates)
                    
                    # Show summary statistics
                    st.markdown("---")
                    st.markdown("## 📈 Summary Statistics")
                    
                    total_candidates = len(st.session_state.ranked_candidates)
                    avg_score = sum(c['score_data']['overall_score'] for c in st.session_state.ranked_candidates) / total_candidates
                    top_score = max(c['score_data']['overall_score'] for c in st.session_state.ranked_candidates)
                    
                    # Display metrics in a simple row format without columns
                    st.write(f"📊 **Total Candidates:** {total_candidates}")
                    st.write(f"📈 **Average Score:** {avg_score:.1f}/100")
                    st.write(f"🏆 **Top Score:** {top_score}/100")
                    
                else:
                    st.warning("⚠️ No results available. Please run the screening first.")
    
    # Add comparison table button
    st.markdown("---")
    if st.button("📊 Show Comparison Table", use_container_width=True, type="secondary"):
        if hasattr(st.session_state, 'ranked_candidates') and st.session_state.ranked_candidates:
            display_comparison_table(st.session_state.ranked_candidates)
        else:
            st.warning("⚠️ No results available. Please run the screening first.")
    
    # Sidebar
    with st.sidebar:
        st.markdown("## 📋 Project Info")
        st.markdown("**Project:** PB-NO-072")
        st.markdown("**Title:** AI-Based Resume Screening System")
        st.markdown("**Domain:** Artificial Intelligence")
        
        st.markdown("## 🎯 Current Status")
        st.markdown("✅ Project structure set up")
        st.markdown("✅ Dependencies configured")
        st.markdown("✅ Main app interface created")
        st.markdown("✅ Resume parsing & text extraction")
        st.markdown("✅ AI skill matching & ranking")
        st.markdown("✅ Results visualization & comparison table")
        st.markdown("🎉 Project Complete!")
        
        st.markdown("## 📁 Data Structure")
        st.markdown("• `data/jobs/` - Job descriptions")
        st.markdown("• `data/resumes/` - Resume files")
        st.markdown("• `src/` - Source code")

if __name__ == "__main__":
    main()
