import streamlit as st
from groq import Groq
from gtts import gTTS
import os
import time

# Page configuration
st.set_page_config(
    page_title="Fact Engine",
    page_icon="🤖",
    layout="centered"
)

# Fetch key securely from Streamlit Settings
api_key = st.secrets.get("GROQ_API_KEY")

if not api_key:
    st.error("GROQ_API_KEY is not configured in Streamlit Secrets.")
    st.stop()

client = Groq(api_key=api_key)

st.title("🌐 Direct Answer Engine")
st.write("---")

# Simple, manual click-to-talk widget
audio_value = st.audio_input("Tap microphone to ask your question")

if audio_value:
    audio_filename = "user_input.wav"

    with open(audio_filename, "wb") as f:
        f.write(audio_value.read())

    with st.spinner("Searching..."):
        try:
            # 1. Speech → Text
            with open(audio_filename, "rb") as audio_file:
                transcription = client.audio.transcriptions.create(
                    file=audio_file,
                    model="whisper-large-v3",
                    response_format="text"
                )

            st.markdown(f'**Question:** {transcription}')

            # 2. Fact-Only AI Response (No conversational talk or thinking blocks)
            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a precise, direct data engine. "
                            "Provide ONLY the direct factual answer to the question asked. "
                            "Do not include conversational greetings, introductions, thoughts, "
                            "or extra fluff. Keep your output under 2 sentences max."
                        )
                    },
                    {
                        "role": "user",
                        "content": transcription
                    }
                ],
                model="qwen/qwen3.6-27b",
                max_tokens=100
            )

            answer = chat_completion.choices[0].message.content

            # Clean and filter out any hidden thinking tags instantly
            if "</think>" in answer:
                answer = answer.split("</think>")[-1].strip()
            elif "<think>" in answer:
                answer = answer.split("<think>")[0].strip()

            st.success(f"**Answer:** {answer}")

            # 3. Text → Speech
            tts = gTTS(
                text=answer,
                lang="en"
            )

            # Generates a clear fresh audio file per request
            unique_time = int(time.time())
            speech_filename = f"reply_{unique_time}.mp3"
            tts.save(speech_filename)

            # Play fresh voice reply out loud automatically
            st.audio(
                speech_filename,
                format="audio/mp3",
                autoplay=True
            )

            # File cleanup
            if os.path.exists(audio_filename):
                os.remove(audio_filename)

        except Exception as e:
            st.error(f"Error processing question: {e}")
            
