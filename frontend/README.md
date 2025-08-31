# JustWork Frontend

A Streamlit-based frontend for the JustWork CV matching system - perfect for hackathons!

## Features

- **Streamlit UI**: Beautiful, responsive web interface with zero frontend code
- **Simple PDF Upload**: Drag & drop or click to upload CV files
- **Real-time Analysis**: Connects to FastAPI backend for CV analysis
- **Progress Tracking**: Visual progress bars and status updates
- **Error Handling**: User-friendly error messages and backend health checks
- **Interactive Results**: Expandable sections for keywords and assessments

## Quick Start

1. **Install dependencies:**
   ```bash
   cd ..
   pip install -r requirements.txt
   ```

2. **Start the backend:**
   ```bash
   cd backend
   python main.py
   ```
   The backend should be available at `http://localhost:8000`

3. **Run the Streamlit frontend:**
   ```bash
   cd frontend
   streamlit run app.py
   ```
   The frontend will open at `http://localhost:8501`

4. **Upload and analyze:**
   - Upload a PDF CV file
   - Click "Analyze CV & Find Matches"
   - View extracted keywords and job match assessment

## How It Works

1. **Upload**: User uploads their CV (PDF format)
2. **Process**: Frontend sends the file to the backend via POST request to `/upload-resumes`
3. **Analyze**: Backend processes the CV and extracts keywords using AI
4. **Match**: System analyzes the CV against stored job descriptions
5. **Display**: Results show extracted skills and job match assessment

## API Integration

The frontend communicates with these backend endpoints:

- `POST /upload-resumes` - Upload the candidate's CV
- `POST /analyze-resumes` - Get comprehensive analysis
- `GET /status` - Check backend health

## Streamlit Features

### Built-in Components
- **File Uploader**: Native drag & drop PDF upload
- **Progress Bars**: Visual feedback during processing
- **Expandable Sections**: Organized results display
- **Status Messages**: Real-time error handling and success notifications

### API Configuration
- Change `API_BASE_URL` in `app.py` to point to your backend
- Currently set to `http://localhost:8000`

### File Upload Limits
- Maximum file size: 200MB (Streamlit default)
- Accepted format: PDF only
- Configurable in the `st.file_uploader()` parameters

## Streamlit Advantages

- **Zero Frontend Code**: No HTML, CSS, or JavaScript needed
- **Rapid Development**: Perfect for hackathons and prototypes
- **Built-in Responsiveness**: Mobile-friendly by default
- **Interactive Components**: Rich UI elements out of the box
- **Python-Native**: Everything in one language

## Troubleshooting

**"Backend server is not running"**
- Make sure the backend is running on port 8000
- Check if CORS is properly configured in the backend
- The app automatically checks backend status

**"File upload failed"**
- Ensure the file is a valid PDF
- Check backend logs for detailed error messages
- Verify backend `/upload-resumes` endpoint is working

**"Analysis failed"**
- Make sure the backend has proper configuration
- Check API key and model availability
- Review backend logs for detailed error messages

**Streamlit not starting**
- Run `pip install streamlit` if not installed
- Use `streamlit run app.py` from the frontend directory
- Check port 8501 is not in use

## Development Notes

This Streamlit app is designed for rapid prototyping and hackathon use:

- **No build process** - Just run `streamlit run app.py`
- **Auto-reload** - Changes refresh automatically
- **Simple architecture** - Single Python file
- **Hackathon-ready** - Focus on functionality over complexity

## Next Steps

For production use, consider:

- Adding authentication with `st.session_state`
- Implementing file caching with `@st.cache_data`
- Adding multiple file upload support
- Creating custom themes
- Adding database integration
- Implementing user sessions
