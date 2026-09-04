import streamlit as st
from groq import Groq
from gtts import gTTS
import os

# Page configurations
st.set_page_config(page_title="JARVIS Assistant", page_icon="🤖", layout="centered")

# Retrieve the hidden API key safely from Streamlit Settings
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
    st.error("Please add your GROQ_API_KEY in the Streamlit App Secret settings.")
    st.stop()

st.title("🤖 Project J.A.R.V.I.S.")
st.write("---")
st.subheader("Welcome, Boss. Tap the mic below to issue a command.")

# 1. Voice input widget for phone and web browsers
from audio_recorder_streamlit import audio_recorder
audio_bytes = audio_recorder(
    text="Tap to talk to JARVIS",
    recording_color="#e74c3c",
    neutral_color="#1abc9c",
    icon_size="2x"
)

if audio_bytes:
    # Temporarily save audio file on the hosting platform
    audio_filename = "user_input.wav"
    with open(audio_filename, "wb") as f:
        f.write(audio_bytes)
        
    with st.spinner("Processing your audio, boss..."):
        try:
            # 2. Transcribe voice to text using free Whisper API
            with open(audio_filename, "rb") as audio_file:
                transcription = client.audio.transcriptions.create(
                    file=audio_file,
                    model="whisper-large-v3",
                    response_format="text"
                )
            
            st.markdown(f"**You said:** *\"{transcription}\"*")
            
            # 3. Prompt the AI Brain (Llama 3 70B) acting as JARVIS
            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "system", 
                        "content": "You are JARVIS, an advanced artificial intelligence system. You speak with a highly sophisticated, British, polite, and elite demeanor reminiscent of the Iron Man movies. Keep responses direct, helpful, and concise."
                    },
                    {"role": "user", "content": transcription}
                ],
                model="llama-3.3-70b-specdec",
            )
            jarvis_reply = chat_completion.choices.message.content
            
            st.markdown(f"**JARVIS:** {jarvis_reply}")
            
            # 4. Synthesize text response back into clear audio speech
            tts = gTTS(text=jarvis_reply, lang='en', tld='co.uk')
            speech_filename = "jarvis_response.mp3"
            tts.save(speech_filename)
            
            # Autoplay audio directly on your friends' mobile browser
            st.audio(speech_filename, format="audio/mp3", autoplay=True)
            
            # Clean up local temporary files
            os.remove(audio_filename)
            os.remove(speech_filename)
            
        except Exception as e:
            st.error(f"System error encountered: {e}")
          
