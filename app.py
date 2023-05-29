import os
import streamlit as st
from audiorecorder import audiorecorder
from apiclient import discovery
from httplib2 import Http
from oauth2client import client, file, tools


import warnings

from transcription import transcribe
from quiz_generation import generate_quiz_url

SCOPES = "https://www.googleapis.com/auth/forms.body"


def main():
    warnings.filterwarnings("ignore")

    # Initialize Google Sheets and Forms API services
    store = file.Storage("credentials.json")
    creds = store.get()
    if not creds or creds.invalid:
        # If the credentials are invalid or not present, initiate the authentication flow
        flow = client.flow_from_clientsecrets("client_secret_535279977482-vc7fo2d86o7uq3qnl05epg9l6sv6a6s1.apps.googleusercontent.com.json", SCOPES)
        creds = tools.run_flow(flow, store)
    form_service = discovery.build("forms", "v1", http=creds.authorize(Http()))

    st.title("Quiz Generator")
    st.markdown("Record an audio clip and generate a quiz based on the transcribed text.")
    audio = audiorecorder("Click to record", "Stop recording")

    if len(audio) > 0:
        # To play audio in the frontend:
        st.audio(audio.tobytes(), format="audio/wav")

        # To save audio to a file:
        wav_file = open("audio.wav", "wb")
        wav_file.write(audio.tobytes())

    # Quiz generation section
    st.header("Quiz Generation")

    if st.button("Generate Quiz"):
        with st.spinner("Transcribing audio to generate the quiz..."):
            transcribed_text = transcribe("audio.wav")
            # Generate the quiz URL based on the transcribed text and form service
            quiz_url = generate_quiz_url(transcribed_text, form_service)
            st.success("Quiz generated successfully!")
            st.text("Quiz Link: " + quiz_url)
            st.text("Transcribed Text:\n" + transcribed_text)
            
            
if __name__ == '__main__':
    main()
