pip install openai gtts streamlit pyPDF2

import streamlit as st
import openai
import os
from dotenv import load_dotenv
from gtts import gTTS
import PyPDF2
import pandas as pd
import io

# Load API Key
# load_dotenv()
openai.api_key = "OPENAI_API_KEY"

# Language options for translation
languages = {
    "French": "fr",
    "Spanish": "es",
    "German": "de",
    "Hindi": "hi",
    "Chinese": "zh",
    "Arabic": "ar",
    "Russian": "ru",
    "Japanese": "ja",
    "Korean": "ko",
    "English": "en"
}

# Title
st.title("🗣️ Multilingual Translator & Text-to-Speech App")

# Input: Choose input type
input_type = st.radio("Choose input method", ["Enter text", "Upload file"])

text = ""

# Option 1: Manual text input
if input_type == "Enter text":
    text = st.text_area("Enter the text to translate")

# Option 2: Upload file
elif input_type == "Upload file":
    uploaded_file = st.file_uploader("Upload a file (PDF, TXT, CSV, Excel)", type=["pdf", "txt", "csv", "xlsx"])
    if uploaded_file:
        if uploaded_file.type == "application/pdf":
            reader = PyPDF2.PdfReader(uploaded_file)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
        elif uploaded_file.type == "text/plain":
            text = uploaded_file.read().decode("utf-8")
        elif uploaded_file.type == "text/csv":
            df = pd.read_csv(uploaded_file)
            text = df.astype(str).apply(lambda x: ' '.join(x), axis=1).str.cat(sep=' ')
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
            df = pd.read_excel(uploaded_file)
            text = df.astype(str).apply(lambda x: ' '.join(x), axis=1).str.cat(sep=' ')

# Select Language
language = st.selectbox("Select target language", list(languages.keys()))

# Translate button
if st.button("Translate & Convert to Speech"):
    if text:
        try:
            # Translation using GPT-3.5-turbo
            system_prompt = f"Translate the following text to {language}:"
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text}
                ]
            )
            translated_text = response.choices[0].message["content"]

            # Display translated text
            st.subheader("Translated Text")
            st.write(translated_text)

            # Convert to speech
            tts = gTTS(text=translated_text, lang=languages[language])
            audio_file = f"translated_audio_{languages[language]}.mp3"
            tts.save(audio_file)

            # Play audio
            st.audio(audio_file, format="audio/mp3")

            # Download audio
            with open(audio_file, "rb") as f:
                st.download_button("Download Audio", f, file_name=audio_file)

        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.warning("Please provide some text or upload a valid file.")
