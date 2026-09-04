import streamlit as st
from groq import Groq
from gtts import gTTS
import os

# Page configuration
st.set_page_config(
    page_title="JARVIS Assistant",
    page_icon="🤖",
    layout="centered"
)

# Get API key securely from Streamlit Secrets
api_key = st.secrets.get("GROQ_API_KEY")

if not api_key:
    st.error("GROQ_API_KEY is not configured in Streamlit Secrets.")
    st.stop()

# Create Groq client
client = Groq(api_key=api_key)

st.title("🤖 Project J.A.R.V.I.S.")
st.write("---")
st.subheader("Welcome, Boss. Record your voice command below.")

# Voice input
audio_value = st.audio_input("Record a voice message")

if audio_value:

    audio_filename = "user_input.wav"

    with open(audio_filename, "wb") as f:
        f.write(audio_value.read())

    with st.spinner("Processing your audio, boss..."):

        try:
            # -------------------------------
            # 1. Speech → Text
            # -------------------------------
            with open(audio_filename, "rb") as audio_file:

                transcription = client.audio.transcriptions.create(
                    file=audio_file,
                    model="whisper-large-v3",
                    response_format="text"
                )

            st.markdown(
                f'**You said:** "{transcription}"'
            )

            # -------------------------------
            # 2. JARVIS AI Response
            # -------------------------------
            chat_completion = client.chat.completions.create(

                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are JARVIS, an advanced artificial "
                            "intelligence system. Speak with a highly "
                            "sophisticated, British, polite and elite "
                            "demeanor. Keep responses direct, helpful "
                            "and concise."
                        )
                    },
                    {
                        "role": "user",
                        "content": transcription
                    }
                ],

                model="llama-3.3-70b-versatile"
            )

            # IMPORTANT: [0]
            jarvis_reply = chat_completion.choices[0].message.content

            st.markdown(
                f"**JARVIS:** {jarvis_reply}"
            )

            # -------------------------------
            # 3. Text → Speech
            # -------------------------------
            tts = gTTS(
                text=jarvis_reply,
                lang="en",
                tld="co.uk"
            )

            speech_filename = "jarvis_response.mp3"

            tts.save(speech_filename)

            # Play response
            st.audio(
                speech_filename,
                format="audio/mp3"
            )

            # Cleanup
            if os.path.exists(audio_filename):
                os.remove(audio_filename)

            # Don't immediately delete the MP3 before
            # Streamlit has a chance to serve it.

        except Exception as e:

            st.error(
                f"System error encountered: {e}"
            )
