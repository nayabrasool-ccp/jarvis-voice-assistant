import streamlit as st
from groq import Groq
from gtts import gTTS
import os
import time

# Page configuration
st.set_page_config(
    page_title="JARVIS Assistant",
    page_icon="🤖",
    layout="centered"
)

# Fetch key securely from Streamlit Settings
api_key = st.secrets.get("GROQ_API_KEY")

if not api_key:
    st.error("GROQ_API_KEY is not configured in Streamlit Secrets.")
    st.stop()

client = Groq(api_key=api_key)

st.title("🤖 Project J.A.R.V.I.S.")
st.write("---")
st.subheader("Welcome, Boss. Tap the mic below manually to speak.")

# EASY MANUAL MIC: Tap to turn on, tap again to turn off
audio_value = st.audio_input("Record your command")

if audio_value:
    audio_filename = "user_input.wav"

    with open(audio_filename, "wb") as f:
        f.write(audio_value.read())

    with st.spinner("Processing audio, boss..."):
        try:
            # 1. Speech → Text
            with open(audio_filename, "rb") as audio_file:
                transcription = client.audio.transcriptions.create(
                    file=audio_file,
                    model="whisper-large-v3",
                    response_format="text"
                )

            st.markdown(f'**You said:** "{transcription}"')

            # 2. Accurate JARVIS AI Response (Fixed limits to stop crashes)
            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are JARVIS, an advanced artificial intelligence system. "
                            "Speak with a highly sophisticated, British, polite demeanor. "
                            "Provide highly accurate factual answers, but keep your responses "
                            "under 3 sentences max to maintain optimal performance."
                        )
                    },
                    {
                        "role": "user",
                        "content": transcription
                    }
                ],
                model="qwen/qwen3.6-27b",
                max_tokens=150  # Fixed limit ensures it never hits a 429 crash again
            )

            jarvis_reply = chat_completion.choices[0].message.content

            # Clean up the output if reasoning markers show up
            if "</think>" in jarvis_reply:
                jarvis_reply = jarvis_reply.split("</think>")[-1].strip()

            st.markdown(f"**JARVIS:** {jarvis_reply}")

            # 3. Text → Speech
            tts = gTTS(
                text=jarvis_reply,
                lang="en",
                tld="co.uk"
            )

            # Generates a fresh audio path every loop to prevent browser sound bugs
            unique_time = int(time.time())
            speech_filename = f"jarvis_{unique_time}.mp3"
            tts.save(speech_filename)

            # Play fresh response back automatically out loud
            st.audio(
                speech_filename,
                format="audio/mp3",
                autoplay=True
            )

            # File cleanup
            if os.path.exists(audio_filename):
                os.remove(audio_filename)

        except Exception as e:
            st.error(f"System error encountered: {e}")
            
