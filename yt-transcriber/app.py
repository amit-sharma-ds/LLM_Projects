import streamlit as st
from dotenv import load_dotenv
import os
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound, VideoUnavailable
from urllib.parse import urlparse, parse_qs

# Load environment variables
load_dotenv()

# Configure Google Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Updated Prompt
prompt = """You are a professional YouTube video summarizer. 
Create clean, structured, and easy-to-understand detailed notes from the transcript.

Rules:
- Use bullet points
- Add headings (##) for main sections
- Keep it concise yet informative
- Maximum 300-350 words
- Focus on key points and important takeaways

Transcript:
"""

# ================== Helper Functions ==================

def extract_video_id(youtube_video_url):
    if not youtube_video_url:
        raise ValueError("Please enter a valid YouTube URL")
    
    try:
        url = youtube_video_url.strip()
        parsed = urlparse(url)
        
        if parsed.hostname in ('youtu.be', 'www.youtu.be'):
            return parsed.path.lstrip('/')
        
        if parsed.hostname in ('youtube.com', 'www.youtube.com', 'm.youtube.com'):
            query = parse_qs(parsed.query)
            if 'v' in query:
                return query['v'][0]
        
        if '=' in url:
            return url.split('=')[-1].split('&')[0].split('?')[0]
        
        raise ValueError("Could not extract Video ID")
    
    except Exception:
        raise ValueError("Invalid YouTube URL. Please check the link.")


def extract_transcript_details(youtube_video_url):
    try:
        video_id = extract_video_id(youtube_video_url)
        
        ytt_api = YouTubeTranscriptApi()
        transcript_list = ytt_api.list(video_id)
        
        try:
            transcript = transcript_list.find_transcript(['en'])
        except:
            try:
                transcript = transcript_list.find_transcript(['hi'])
            except:
                try:
                    transcript = transcript_list.find_generated_transcript(['en'])
                except:
                    transcript = next(iter(transcript_list))
        
        fetched = transcript.fetch()
        full_transcript = " ".join([snippet.text for snippet in fetched])
        
        return full_transcript, video_id

    except TranscriptsDisabled:
        raise Exception("❌ Subtitles are disabled for this video.")
    except NoTranscriptFound:
        raise Exception("❌ No subtitles found for this video.")
    except VideoUnavailable:
        raise Exception("❌ This video is unavailable.")
    except Exception as e:
        raise Exception(f"❌ Failed to fetch transcript: {str(e)}")


def generate_gemini_content(transcript_text, prompt):
    """Generate summary - Updated for April 2026"""
    try:
        # Try these one by one if one fails
        model_name = "gemini-2.5-flash"       # Best choice right now
        # model_name = "gemini-2.5-flash-lite"
        # model_name = "gemini-3-flash"
        
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt + transcript_text)
        return response.text
    except Exception as e:
        raise Exception(f"❌ Error generating summary: {str(e)}")


# ===================== Streamlit UI =====================

st.set_page_config(page_title="YouTube Notes Converter", page_icon="📝", layout="centered")

st.title("📝 YouTube Transcript to Detailed Notes")
st.markdown("Convert any YouTube video into clean, structured notes using AI")

youtube_link = st.text_input("Enter YouTube Video Link:", placeholder="https://www.youtube.com/watch?v=example")

if youtube_link:
    try:
        video_id = extract_video_id(youtube_link)
        st.image(f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg", use_container_width=True)
    except:
        st.warning("Invalid YouTube link.")

if st.button("Get Detailed Notes", type="primary"):
    if not youtube_link:
        st.error("Please enter a YouTube video link")
    else:
        with st.spinner("Fetching transcript and generating notes..."):
            try:
                transcript_text, video_id = extract_transcript_details(youtube_link)
                summary = generate_gemini_content(transcript_text, prompt)
                
                st.success("✅ Notes generated successfully!")
                st.markdown("## 📋 Detailed Notes")
                st.markdown(summary)
                
                st.download_button(
                    label="📥 Download Notes as Text",
                    data=summary,
                    file_name=f"youtube_notes_{video_id}.txt",
                    mime="text/plain"
                )
            except Exception as e:
                st.error(str(e))

st.markdown("---")
st.caption("Made with ❤️ using Gemini + Streamlit")