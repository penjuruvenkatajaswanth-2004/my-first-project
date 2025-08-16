import streamlit as st
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class SkillMatcher:
    """Class to match resume skills with job requirements and rank candidates"""
    
    def __init__(self):
        # Common technical skills with categories
        self.skill_categories = {
            'programming_languages': [
                'python', 'java', 'javascript', 'c++', 'c#', 'php', 'ruby', 'go', 'rust', 'swift',
                'kotlin', 'scala', 'r', 'matlab', 'perl', 'shell', 'bash', 'powershell'
            ],
            'web_technologies': [
                'html', 'css', 'react', 'angular', 'vue', 'node.js', 'express', 'django', 'flask',
                'spring', 'laravel', 'asp.net', 'jsp', 'servlets', 'jquery', 'bootstrap', 'sass'
            ],
            'databases': [
                'sql', 'mysql', 'postgresql', 'mongodb', 'oracle', 'sql server', 'sqlite', 'redis',
                'cassandra', 'dynamodb', 'firebase', 'elasticsearch', 'neo4j'
            ],
            'cloud_platforms': [
                'aws', 'azure', 'google cloud', 'gcp', 'heroku', 'digitalocean', 'linode', 'vultr'
            ],
            'devops_tools': [
                'docker', 'kubernetes', 'jenkins', 'git', 'github', 'gitlab', 'bitbucket', 'jira',
                'confluence', 'terraform', 'ansible', 'chef', 'puppet'
            ],
            'ai_ml_tools': [
                'machine learning', 'ai', 'artificial intelligence', 'tensorflow', 'pytorch', 'scikit-learn',
                'keras', 'opencv', 'nltk', 'spacy', 'pandas', 'numpy', 'matplotlib', 'seaborn'
            ],
            'data_analysis': [
                'data analysis', 'data visualization', 'excel', 'powerbi', 'tableau', 'qlik', 'looker',
                'apache spark', 'hadoop', 'kafka', 'airflow', 'dbt'
            ],
            'soft_skills': [
                'leadership', 'communication', 'teamwork', 'problem solving', 'critical thinking',
                'project management', 'agile', 'scrum', 'kanban', 'customer service', 'sales'
            ]
        }
        
        # Flatten all skills into one list
        self.all_skills = []
        for category_skills in self.skill_categories.values():
            self.all_skills.extend(category_skills)
    
    def extract_job_skills(self, job_description: str) -> Dict[str, List[str]]:
        """Extract required skills from job description"""
        job_lower = job_description.lower()
        found_skills = {}
        
        for category, skills in self.skill_categories.items():
            category_found = []
            for skill in skills:
                if skill in job_lower:
                    category_found.append(skill.title())
            if category_found:
                found_skills[category] = category_found
        
        # If no skills found, try to extract some basic ones
        if not found_skills:
            basic_skills = ['python', 'java', 'javascript', 'html', 'css', 'sql', 'react', 'node.js']
            basic_found = []
            for skill in basic_skills:
                if skill in job_lower:
                    basic_found.append(skill.title())
            if basic_found:
                found_skills['general_skills'] = basic_found
        
        return found_skills
    
    def calculate_skill_match_score(self, resume_skills: List[str], job_skills: List[str]) -> float:
        """Calculate how well resume skills match job requirements"""
        if not job_skills:
            return 0.0
        
        if not resume_skills:
            return 0.0
        
        # Convert to lowercase for comparison
        resume_lower = [skill.lower() for skill in resume_skills]
        job_lower = [skill.lower() for skill in job_skills]
        
        # Count matching skills
        matches = sum(1 for skill in job_lower if skill in resume_lower)
        
        # Calculate percentage match
        match_percentage = (matches / len(job_lower)) * 100
        
        # Add variation based on skill count to differentiate resumes
        skill_count_bonus = min(5, len(resume_skills) * 0.5)  # Bonus for having more skills
        
        # Add variation based on how many job skills are covered
        coverage_bonus = min(10, (matches / len(job_lower)) * 20)  # Bonus for covering more job requirements
        
        final_score = min(100, match_percentage + skill_count_bonus + coverage_bonus)
        
        return round(final_score, 2)
    
    def calculate_overall_score(self, resume_data: Dict, job_skills: Dict[str, List[str]]) -> Dict:
        """Calculate overall matching score for a candidate"""
        resume_skills = resume_data.get('skills', [])
        
        # Calculate skill match scores for each category
        category_scores = {}
        total_score = 0
        category_count = 0
        
        for category, skills in job_skills.items():
            if skills:  # Only calculate if category has skills
                score = self.calculate_skill_match_score(resume_skills, skills)
                category_scores[category] = score
                total_score += score
                category_count += 1
        
        # Calculate overall score
        overall_score = round(total_score / category_count, 2) if category_count > 0 else 0
        
        # Experience bonus (up to 15 points) - More differentiation
        experience_bonus = 0
        experience_text = resume_data.get('experience', '')
        if 'years' in experience_text.lower():
            try:
                years = int(re.search(r'(\d+)', experience_text).group(1))
                if years >= 8:
                    experience_bonus = 15
                elif years >= 5:
                    experience_bonus = 12
                elif years >= 3:
                    experience_bonus = 8
                elif years >= 1:
                    experience_bonus = 5
            except:
                pass
        
        # Education bonus (up to 10 points) - More differentiation
        education_bonus = 0
        education = resume_data.get('education', [])
        for edu in education:
            if any(degree in edu.lower() for degree in ['phd', 'doctorate']):
                education_bonus = 10
                break
            elif any(degree in edu.lower() for degree in ['master', 'mba', 'ms']):
                education_bonus = 7
                break
            elif any(degree in edu.lower() for degree in ['bachelor', 'b.tech', 'b.e', 'bs']):
                education_bonus = 4
                break
            elif any(degree in edu.lower() for degree in ['diploma', 'associate']):
                education_bonus = 2
                break
        
        # Skills diversity bonus (up to 10 points) - New bonus for having diverse skills
        skills_diversity_bonus = 0
        if resume_skills:
            # Bonus for having skills from multiple categories
            skill_categories_covered = 0
            for category_skills in self.skill_categories.values():
                if any(skill.lower() in [s.lower() for s in resume_skills] for skill in category_skills):
                    skill_categories_covered += 1
            
            skills_diversity_bonus = min(10, skill_categories_covered * 2)
        
        # Final score with all bonuses
        final_score = min(100, overall_score + experience_bonus + education_bonus + skills_diversity_bonus)
        
        return {
            'overall_score': final_score,
            'skill_score': overall_score,
            'experience_bonus': experience_bonus,
            'education_bonus': education_bonus,
            'skills_diversity_bonus': skills_diversity_bonus,
            'category_scores': category_scores
        }
    
    def rank_candidates(self, resumes_data: List[Dict], job_description: str) -> List[Dict]:
        """Rank candidates based on job requirements"""
        # Extract job skills
        job_skills = self.extract_job_skills(job_description)
        
        # Calculate scores for each candidate
        ranked_candidates = []
        
        for resume_data in resumes_data:
            if 'error' not in resume_data:
                score_data = self.calculate_overall_score(resume_data, job_skills)
                
                candidate_info = {
                    'resume_data': resume_data,
                    'score_data': score_data,
                    'rank': 0  # Will be set after sorting
                }
                
                ranked_candidates.append(candidate_info)
        
        # Sort by overall score (highest first)
        ranked_candidates.sort(key=lambda x: x['score_data']['overall_score'], reverse=True)
        
        # Assign ranks
        for i, candidate in enumerate(ranked_candidates):
            candidate['rank'] = i + 1
        
        return ranked_candidates
    
    def debug_skill_matching(self, resume_data: Dict, job_skills: Dict[str, List[str]]):
        """Debug function to show why scores are calculated the way they are"""
        resume_skills = resume_data.get('skills', [])
        
        st.markdown("**🔍 Debug Information:**")
        st.write(f"**Resume Skills:** {resume_skills}")
        st.write(f"**Job Skills by Category:** {job_skills}")
        
        for category, skills in job_skills.items():
            if skills:
                score = self.calculate_skill_match_score(resume_skills, skills)
                st.write(f"**{category}:** Required: {skills}, Score: {score}%")
        
        # Show experience and education analysis
        experience_text = resume_data.get('experience', '')
        education = resume_data.get('education', [])
        
        st.write(f"**Experience Text:** {experience_text}")
        st.write(f"**Education:** {education}")
        
        # Show score calculation details
        st.markdown("**📊 Score Calculation Details:**")
        st.write(f"**Filename:** {resume_data.get('filename', '')}")
        st.write(f"**Skills Count:** {len(resume_skills)}")
        st.write(f"**Skills Count Bonus:** min(3, {len(resume_skills)} * 0.3) = {min(3, len(resume_skills) * 0.3):.1f}")
        
        # Show new scoring details
        st.write(f"**Skills Count Bonus:** min(5, {len(resume_skills)} * 0.5) = {min(5, len(resume_skills) * 0.5):.1f}")
        
        # Calculate skills diversity bonus
        skill_categories_covered = 0
        for category_skills in self.skill_categories.values():
            if any(skill.lower() in [s.lower() for s in resume_skills] for skill in category_skills):
                skill_categories_covered += 1
        
        skills_diversity_bonus = min(10, skill_categories_covered * 2)
        st.write(f"**Skills Diversity Bonus:** {skill_categories_covered} categories × 2 = +{skills_diversity_bonus} points")

def display_job_skills(job_skills: Dict[str, List[str]]):
    """Display extracted job skills in a clean format"""
    st.markdown("## 🎯 Job Requirements Analysis")
    
    if not job_skills:
        st.warning("No specific skills detected in job description")
        return
    
    # Display skills by category
    for category, skills in job_skills.items():
        if skills:
            # Convert category name to readable format
            category_name = category.replace('_', ' ').title()
            st.markdown(f"**{category_name}:**")
            
            # Display skills with nice formatting
            skills_text = ", ".join(skills)
            st.info(skills_text)

def display_candidate_ranking(ranked_candidates: List[Dict]):
    """Display candidate ranking results"""
    st.markdown("## 🏆 Candidate Ranking Results")
    
    if not ranked_candidates:
        st.warning("No candidates to rank")
        return
    
    # Display ALL candidates
    for i, candidate in enumerate(ranked_candidates):
        resume_data = candidate['resume_data']
        score_data = candidate['score_data']
        
        # Create expandable section for each candidate
        with st.expander(f"🥇 Rank #{candidate['rank']}: {resume_data['filename']} - Score: {score_data['overall_score']}/100"):
            
            # Score breakdown
            st.markdown("**📊 Score Breakdown:**")
            st.write(f"• **Overall Score:** {score_data['overall_score']}/100")
            st.write(f"• **Skill Match:** {score_data['skill_score']}/100")
            st.write(f"• **Experience Bonus:** +{score_data['experience_bonus']} points")
            st.write(f"• **Education Bonus:** +{score_data['education_bonus']} points")
            st.write(f"• **Skills Diversity Bonus:** +{score_data.get('skills_diversity_bonus', 0)} points")
            
            # Category scores
            if score_data['category_scores']:
                st.markdown("**📈 Category Scores:**")
                for category, score in score_data['category_scores'].items():
                    category_name = category.replace('_', ' ').title()
                    st.write(f"• {category_name}: {score}%")
            
            # Resume details
            st.markdown("**📄 Resume Details:**")
            if resume_data.get('skills'):
                st.write(f"• **Skills:** {', '.join(resume_data['skills'])}")
            st.write(f"• **Experience:** {resume_data.get('experience', 'Not specified')}")
            if resume_data.get('education'):
                st.write(f"• **Education:** {resume_data['education'][0] if resume_data['education'] else 'Not specified'}")
            
            # Debug information (simple display, no nested expanders)
            st.markdown("**🔍 Debug Score Calculation:**")
            # We need to recreate the skill matcher to access debug function
            skill_matcher = SkillMatcher()
            job_skills = skill_matcher.extract_job_skills(st.session_state.job_description)
            skill_matcher.debug_skill_matching(resume_data, job_skills)
    
    # Summary statistics
    st.markdown("---")
    st.markdown(f"**📋 Total Candidates Ranked:** {len(ranked_candidates)}")
    
    # Show selection recommendation
    if ranked_candidates:
        top_candidate = ranked_candidates[0]
        st.success(f"🏆 **RECOMMENDED CANDIDATE:** {top_candidate['resume_data']['filename']} with score {top_candidate['score_data']['overall_score']}/100")
        
        if len(ranked_candidates) > 1:
            second_candidate = ranked_candidates[1]
            st.info(f"🥈 **SECOND CHOICE:** {second_candidate['resume_data']['filename']} with score {second_candidate['score_data']['overall_score']}/100")

def display_comparison_table(ranked_candidates: List[Dict]):
    """Display a comparison table of all candidates"""
    st.markdown("## 📊 Resume Comparison Table")
    
    if not ranked_candidates:
        st.warning("No candidates to compare")
        return
    
    if len(ranked_candidates) < 2:
        st.info("Need at least 2 candidates to show comparison table")
        return
    
    # Create comparison data
    comparison_data = []
    
    for candidate in ranked_candidates:
        resume_data = candidate['resume_data']
        score_data = candidate['score_data']
        
        comparison_data.append({
            'Rank': candidate['rank'],
            'Filename': resume_data['filename'],
            'Overall Score': f"{score_data['overall_score']}/100",
            'Skill Match': f"{score_data['skill_score']}/100",
            'Experience Bonus': f"+{score_data['experience_bonus']}",
            'Education Bonus': f"+{score_data['education_bonus']}",
            'Skills Diversity Bonus': f"+{score_data.get('skills_diversity_bonus', 0)}",
            'Skills Count': len(resume_data.get('skills', [])),
            'Experience': resume_data.get('experience', 'Not specified'),
            'Education': resume_data.get('education', ['Not specified'])[0] if resume_data.get('education') else 'Not specified'
        })
    
    # Create DataFrame for better display
    import pandas as pd
    df = pd.DataFrame(comparison_data)
    
    # Display the comparison table
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Rank": st.column_config.NumberColumn("Rank", help="Candidate ranking"),
            "Filename": st.column_config.TextColumn("Filename", help="Resume file name"),
            "Overall Score": st.column_config.TextColumn("Overall Score", help="Total score out of 100"),
            "Skill Match": st.column_config.TextColumn("Skill Match", help="Skill matching percentage"),
            "Experience Bonus": st.column_config.TextColumn("Exp Bonus", help="Experience bonus points"),
            "Education Bonus": st.column_config.TextColumn("Edu Bonus", help="Education bonus points"),
            "Unique Bonus": st.column_config.TextColumn("Unique Bonus", help="Unique identifier bonus"),
            "Skills Count": st.column_config.NumberColumn("Skills Count", help="Number of skills detected"),
            "Experience": st.column_config.TextColumn("Experience", help="Years of experience"),
            "Education": st.column_config.TextColumn("Education", help="Highest education level")
        }
    )
    
    # Add download button for the comparison table
    csv = df.to_csv(index=False)
    st.download_button(
        label="📥 Download Comparison Table (CSV)",
        data=csv,
        file_name="resume_comparison_table.csv",
        mime="text/csv"
    )
    
    # Show key insights
    st.markdown("---")
    st.markdown("## 🔍 Key Insights")
    
    # Find best in each category
    if comparison_data:
        best_skill_match = max(comparison_data, key=lambda x: float(x['Skill Match'].split('/')[0]))
        most_skills = max(comparison_data, key=lambda x: x['Skills Count'])
        highest_exp_bonus = max(comparison_data, key=lambda x: int(x['Experience Bonus'].replace('+', '')))
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("🏆 Best Skill Match", best_skill_match['Filename'], best_skill_match['Skill Match'])
        with col2:
            st.metric("🔧 Most Skills", most_skills['Filename'], most_skills['Skills Count'])
        with col3:
            st.metric("⏰ Highest Experience", highest_exp_bonus['Filename'], highest_exp_bonus['Experience Bonus'])
