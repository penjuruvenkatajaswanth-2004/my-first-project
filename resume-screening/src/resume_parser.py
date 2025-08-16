import streamlit as st
import pandas as pd
from pathlib import Path
import io
import re
from typing import Dict, List, Tuple

# Import document processing libraries
try:
    from pypdf import PdfReader
    from docx import Document
except ImportError:
    st.error("Required libraries not found. Please install: pip install pypdf python-docx")

class ResumeParser:
    """Class to parse and extract text from resume files"""
    
    def __init__(self):
        self.supported_formats = ['.pdf', '.docx']
    
    def extract_text_from_pdf(self, pdf_file) -> str:
        """Extract text from PDF file"""
        try:
            pdf_reader = PdfReader(pdf_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            st.error(f"Error reading PDF: {str(e)}")
            return ""
    
    def extract_text_from_docx(self, docx_file) -> str:
        """Extract text from DOCX file"""
        try:
            doc = Document(docx_file)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text.strip()
        except Exception as e:
            st.error(f"Error reading DOCX: {str(e)}")
            return ""
    
    def extract_skills(self, text: str) -> List[str]:
        """Extract skills from resume text"""
        # Common technical skills
        common_skills = [
            'python', 'java', 'javascript', 'html', 'css', 'sql', 'mongodb', 'mysql',
            'react', 'angular', 'vue', 'node.js', 'django', 'flask', 'spring',
            'machine learning', 'ai', 'artificial intelligence', 'data analysis',
            'excel', 'powerbi', 'tableau', 'aws', 'azure', 'docker', 'kubernetes',
            'git', 'agile', 'scrum', 'project management', 'leadership'
        ]
        
        # Convert text to lowercase for matching
        text_lower = text.lower()
        found_skills = []
        
        for skill in common_skills:
            if skill in text_lower:
                found_skills.append(skill.title())
        
        return found_skills
    
    def extract_experience(self, text: str) -> str:
        """Extract years of experience from resume text"""
        # Look for experience patterns
        experience_patterns = [
            r'(\d+)\+?\s*years?\s*of?\s*experience',
            r'experience:\s*(\d+)\+?\s*years?',
            r'(\d+)\+?\s*years?\s*in\s*the\s*field'
        ]
        
        for pattern in experience_patterns:
            match = re.search(pattern, text.lower())
            if match:
                return match.group(1) + " years"
        
        return "Experience not specified"
    
    def extract_education(self, text: str) -> List[str]:
        """Extract education information from resume text"""
        education_keywords = [
            'bachelor', 'master', 'phd', 'degree', 'university', 'college',
            'diploma', 'certification', 'certificate'
        ]
        
        lines = text.split('\n')
        education_lines = []
        
        for line in lines:
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in education_keywords):
                education_lines.append(line.strip())
        
        return education_lines[:3]  # Return top 3 education entries
    
    def parse_resume(self, file) -> Dict:
        """Main method to parse a resume file and extract information"""
        file_extension = Path(file.name).suffix.lower()
        
        if file_extension not in self.supported_formats:
            return {"error": f"Unsupported file format: {file_extension}"}
        
        # Extract text based on file type
        if file_extension == '.pdf':
            text = self.extract_text_from_pdf(file)
        else:  # .docx
            text = self.extract_text_from_docx(file)
        
        if not text:
            return {"error": "Could not extract text from file"}
        
        # Extract information
        parsed_data = {
            "filename": file.name,
            "file_type": file_extension,
            "raw_text": text,
            "skills": self.extract_skills(text),
            "experience": self.extract_experience(text),
            "education": self.extract_education(text),
            "text_length": len(text),
            "word_count": len(text.split())
        }
        
        return parsed_data

def display_parsed_resume(parsed_data: Dict):
    """Display parsed resume information in a nice format"""
    if "error" in parsed_data:
        st.error(parsed_data["error"])
        return
    
    # Display resume information in simple format - NO COLUMNS
    st.subheader(f"📄 {parsed_data['filename']}")
    
    # Skills section
    if parsed_data['skills']:
        st.markdown("**�� Skills Found:**")
        skills_text = ", ".join(parsed_data['skills'])
        st.info(skills_text)
    else:
        st.warning("No specific skills detected")
    
    # Experience section
    st.markdown(f"**⏰ Experience:** {parsed_data['experience']}")
    
    # Education section
    if parsed_data['education']:
        st.markdown("**🎓 Education:**")
        for edu in parsed_data['education']:
            st.write(f"• {edu}")
    
    # File statistics - SIMPLE DISPLAY, NO COLUMNS
    st.markdown("**�� File Statistics:**")
    
    # Display as simple text - NO st.columns() calls
    st.write(f"�� **Text Length:** {parsed_data['text_length']:,} characters")
    st.write(f"📝 **Word Count:** {parsed_data['word_count']:,} words")
    st.write(f"🔧 **Skills Found:** {len(parsed_data['skills'])} skills")
    
    # File type indicator
    file_type_emoji = "📄" if parsed_data['file_type'] == '.pdf' else "��"
    st.write(f"📁 **File Type:** {file_type_emoji} {parsed_data['file_type'].upper()}")
    
    # Raw text preview (collapsible)
    with st.expander("📖 View Raw Text"):
        st.text_area("Extracted Text:", parsed_data['raw_text'], height=200, disabled=True)
