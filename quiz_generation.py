import re
import os
from apiclient import discovery
from oauth2client import client, file, tools
import bardapi
import streamlit as st

SCOPES = "https://www.googleapis.com/auth/forms.body"
DISCOVERY_DOC = "https://forms.googleapis.com/$discovery/rest?version=v1"

NEW_FORM = {
    "info": {
        "title": "Quiz"
    }
}

# Function to generate quiz questions based on a given prompt
def generate_quiz_questions(prompt):
    '''Generates quiz questions based on a given prompt using the Bard API.
    
    Args:
        prompt (str): The prompt for generating quiz questions.
    
    Returns:
        str: The generated quiz questions in a formatted text.
    '''
    # Visit https://bard.google.com/
    # F12 for console
    # Session: Application → Cookies → Copy the value of __Secure-1PSID cookie.
    # Set your __Secure-1PSID value to key
    os.environ['_BARD_API_KEY'] = st.secrets["bard_api_key"]
    
    prompt_suffix = ". Each generated question has to begin with '🔹', each choice has to begin with '🔸', and each correct answer has to begin with '✔️'."

    # Send API requests and get responses
    response = bardapi.core.Bard().get_answer(prompt + prompt_suffix)

    quiz = response["content"]

    return quiz

# Function to generate the quiz URL based on the transcribed text
def generate_quiz_url(prompt_text, form_service):
    '''Generates the quiz URL based on the transcribed text and form service.
    
    Args:
        prompt_text (str): The transcribed text used for generating quiz questions.
        form_service (googleapiclient.discovery.Resource): The form service object for creating the form.
    
    Returns:
        str: The URL of the generated quiz form.
    '''
    # Generate quiz questions based on the transcribed text
    text = generate_quiz_questions(prompt_text)

    # Questions, choices, and correct answers
    questions = re.findall(r"🔹 (.*?)\n", text)
    choices = re.findall(r"🔸 (.*?)\n", text)
    answers = re.findall(r"✔️ (.*?)\n", text)

    # Remove the '**' from the questions list (they are not part of the question), choices, and correct answers
    questions = [question.replace('**', '') for question in questions]
    answers = [answer.replace('**', '') for answer in answers]

    questions_list = []

    # Fill the questions_list variable
    for i, question in enumerate(questions):
        choices_for_question = choices[i * 4:(i + 1) * 4]
        correct_answer = answers[i] if i < len(answers) else ""

        question_dict = {
            "question": question,
            "choices": choices_for_question,
            "correct_answer": correct_answer
        }

        questions_list.append(question_dict)

    # Create the initial form
    result = form_service.forms().create(body=NEW_FORM).execute()

    # Add the questions to the form
    question_requests = []
    for index, question in enumerate(questions_list):
        new_question = {
            "createItem": {
                "item": {
                    "title": question["question"],
                    "questionItem": {
                        "question": {
                            "required": True,
                            "choiceQuestion": {
                                "type": "RADIO",
                                "options": [
                                    {"value": choice} for choice in question["choices"]
                                ],
                                "shuffle": True
                            }
                        }
                    }
                },
                "location": {
                    "index": index
                }
            }
        }
        question_requests.append(new_question)

    NEW_QUESTIONS = {
        "requests": question_requests
    }

    question_setting = form_service.forms().batchUpdate(formId=result["formId"], body=NEW_QUESTIONS).execute()

    # Retrieve the updated form result
    get_result = form_service.forms().get(formId=result["formId"]).execute()

    # Get the form ID
    form_id = get_result["formId"]

    # Construct the quiz link using the form ID
    form_url = result["responderUri"]

    return form_url