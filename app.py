import streamlit as st
from groq import Groq
from gtts import gTTS
import os

# 1. Page configurations
st.set_page_config(page_title="JARVIS Assistant", page_icon="🤖", layout="centered")

# Securely references the key from your Streamlit Settings vault
api_key_from_secrets = st.secrets.get("GROQ_API_KEY")
client = Groq(api_key=api_key_from_secrets)

st.title("🤖 Project J.A.R.V.I.S.")
st.write("---")
st.subheader("Welcome, Boss. Record your voice command below.")

# 2. Uses Streamlit's stable native audio input microphone component
audio_value = st.audio_input("Record a voice message")

if audio_value:
    audio_filename = "user_input.wav"
    with open(audio_filename, "wb") as f:
        f.write(audio_value.read())
        
    with st.spinner("Processing your audio, boss..."):
        try:
            # 3. Transcribes voice to text using free Whisper API
            with open(audio_filename, "rb") as audio_file:
                transcription = client.audio.transcriptions.create(
                    file=audio_file,
                    model="whisper-large-v3",
                    response_format="text"
                )
            
            st.markdown(f"**You said:** *\"{transcription}\"*")
            
            # 4. Prompts the AI Brain (Llama 3 70B) acting as JARVIS
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
            
            # 5. Synthesizes text response back into clear audio speech
            tts = gTTS(text=jarvis_reply, lang='en', tld='co.uk')
            speech_filename = "jarvis_response.mp3"
            tts.save(speech_filename)
            
            # Plays audio back to your phone automatically
            st.audio(speech_filename, format="audio/mp3", autoplay=True)
            
            # Clean up local temporary files
            os.remove(audio_filename)
            os.remove(speech_filename)
            
        except Exception as e:
            st.error(f"System error encountered: {e}")
