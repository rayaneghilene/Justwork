import streamlit as st
import requests
import json
from pathlib import Path
import time

# Configure page
st.set_page_config(
    page_title="JustWork - CV Matcher",
    page_icon="💼",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #667eea;
        font-size: 3rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        text-align: center;
        color: #666;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    .upload-section {
        border: 2px dashed #667eea;
        border-radius: 10px;
        padding: 2rem;
        text-align: center;
        background: #f8f9ff;
        margin: 1rem 0;
    }
    .results-section {
        background: #f8f9ff;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 4px solid #667eea;
    }
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 25px;
        font-weight: 600;
        padding: 0.5rem 2rem;
        font-size: 1.1rem;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #5a67d8 0%, #6b46c1 100%);
        border: none;
    }
</style>
""", unsafe_allow_html=True)

# API Configuration - use environment variable for Docker compatibility
import os
API_BASE_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

def check_backend_status():
    """Check if backend is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/status", timeout=5)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def upload_cv_to_backend(uploaded_file):
    """Upload CV file to backend"""
    try:
        files = {"files": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
        response = requests.post(f"{API_BASE_URL}/upload-resumes", files=files, timeout=30)
        
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, f"Upload failed: {response.text}"
    except requests.exceptions.RequestException as e:
        return False, f"Connection error: {str(e)}"

def analyze_cv():
    """Analyze uploaded CV"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/analyze-resumes",
            headers={"Content-Type": "application/json"},
            json={},
            timeout=300  # Increased timeout to 5 minutes for AI processing
        )
        
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, f"Analysis failed: {response.text}"
    except requests.exceptions.RequestException as e:
        return False, f"Connection error: {str(e)}"

def main():
    # Header
    st.markdown('<div class="main-header">💼 JustWork</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Upload your CV and find the perfect job matches</div>', unsafe_allow_html=True)
    
    # Display connection info in sidebar for debugging
    with st.sidebar:
        st.markdown("### 🔧 Debug Info")
        st.code(f"Backend URL: {API_BASE_URL}")
        if os.getenv("BACKEND_URL"):
            st.code(f"Docker Mode: ✅")
        else:
            st.code(f"Local Mode: ✅")
    
    # Check backend status
    with st.spinner("🔍 Checking backend connection..."):
        backend_status = check_backend_status()
    
    if not backend_status:
        st.error(f"⚠️ Backend server is not running at {API_BASE_URL}")
        
        with st.expander("🔧 Troubleshooting Help"):
            if "localhost" in API_BASE_URL:
                st.markdown("""
                **Local Development:**
                1. Run: `cd backend && python main.py` to start the backend
                2. Make sure port 8000 is not blocked
                3. Check if backend is running: `curl http://localhost:8000`
                """)
            else:
                st.markdown("""
                **Docker Mode:**
                1. Make sure Docker containers are running: `docker-compose ps`
                2. Check container logs: `docker-compose logs justwork-backend`
                3. Verify network connectivity: `docker-compose exec justwork-frontend curl http://justwork-backend:8000`
                4. Restart services: `docker-compose restart`
                """)
            
            st.markdown(f"""
            **Current Configuration:**
            - Backend URL: `{API_BASE_URL}`
            - Environment: `{'Docker' if os.getenv('BACKEND_URL') else 'Local'}`
            - User Agent: `Streamlit Frontend`
            """)
        
        return
    
    st.success(f"✅ Backend server is running at {API_BASE_URL}")
    
    # File upload section
    st.markdown("### 📤 Upload Your CV")
    
    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type=['pdf'],
        help="Upload your CV in PDF format (max 10MB)"
    )
    
    if uploaded_file is not None:
        # Display file info
        st.info(f"📄 **File:** {uploaded_file.name} ({uploaded_file.size / 1024:.1f} KB)")
        
        # Analyze button
        if st.button("🚀 Analyze CV & Find Matches", type="primary"):
            
            # Progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Step 1: Upload CV
            status_text.text("⬆️ Uploading CV to backend...")
            progress_bar.progress(25)
            
            success, result = upload_cv_to_backend(uploaded_file)
            if not success:
                st.error(f"❌ Upload failed: {result}")
                return
            
            st.success(f"✅ {result['message']}")
            
            # Step 2: Analyze CV
            status_text.text("🔍 Analyzing CV with AI (this may take up to 5 minutes)...")
            progress_bar.progress(75)
            
            success, analysis_result = analyze_cv()
            if not success:
                st.error(f"❌ Analysis failed: {analysis_result}")
                return
            
            # Complete
            progress_bar.progress(100)
            status_text.text("✅ Analysis complete!")
            time.sleep(1)  # Brief pause for user experience
            status_text.empty()
            progress_bar.empty()
            
            # Display results
            st.markdown("---")
            st.markdown("## 🎯 Analysis Results")
            
            # Keywords section
            with st.expander("📊 Extracted Skills & Keywords", expanded=True):
                st.markdown('<div class="results-section">', unsafe_allow_html=True)
                if analysis_result.get('keywords'):
                    # Try to parse as JSON for better formatting
                    try:
                        keywords_data = json.loads(analysis_result['keywords'])
                        st.json(keywords_data)
                    except json.JSONDecodeError:
                        st.text(analysis_result['keywords'])
                else:
                    st.warning("No keywords extracted")
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Assessment section
            with st.expander("💼 Job Match Assessment", expanded=True):
                st.markdown('<div class="results-section">', unsafe_allow_html=True)
                if analysis_result.get('assessment'):
                    st.markdown(analysis_result['assessment'])
                else:
                    st.warning("No assessment available")
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Success message
            st.success("🎉 CV analysis completed successfully! The results show your skills and potential job matches.")
    
    else:
        st.markdown('<div class="upload-section">', unsafe_allow_html=True)
        st.markdown("**👆 Please upload a PDF file to get started**")
        st.markdown("*Drag and drop your CV or click to browse*")
        st.markdown('</div>', unsafe_allow_html=True)
    

if __name__ == "__main__":
    main()
