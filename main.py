import os
import re
import speech_recognition as sr
import google.generativeai as genai
import pyttsx3

genai.configure(api_key="AIzaSyDy59cCQyu38wVj55e92kafXawRA_ZoAbM")
# Configuration
CHARACTER_NAME = "Cheetos"  
MATCH_THRESHOLD = 0.4  
SCRIPT_TEXT = """

MIA: Oh relax it is just wait is that a cheetah
Cheetos: HELLO EVERYONE! Don’t be scared of me ! And Leo to make you happy, Peppa finds back her stuffed toy.

Trainer: What do you mean cheetos
Cheetos: Oh no! The myths are coming true. 

Anne: I have given up guys. i can not do this
Cheetos: Cheer up Anne! I know how I can put you in a good mood right now. Well, it’s your day, and I’m here to say,I’m the reason you’re laughing today!I’m the one who made you snort,Laughed so loud, you missed the port!But when life’s a mess and you’re feeling low,Find a journal, that spills the tea,But don’t tell anyone that it was me

"""


recognizer = sr.Recognizer()
engine = pyttsx3.init()
model = genai.GenerativeModel('gemini-1.5-flash')


def parse_script(script_text):
    script = []
    for line in script_text.strip().split("\n"):
        if line.strip() and not line.startswith("["):  
            character, dialogue = line.split(":", 1)
            script.append((character.strip(), dialogue.strip()))
    return script


SCRIPT = parse_script(SCRIPT_TEXT)

def listen():
    with sr.Microphone() as source:
        print("Listening...")
        audio = recognizer.listen(source)
        try:
            return recognizer.recognize_google(audio).lower()
        except sr.UnknownValueError:
            print("Could not understand audio")
            return ""
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")
            return ""
        except Exception as e: # Catching other potential errors
            print(f"An unexpected error occurred: {e}")
            return ""


def respond(text):
    print(f"Responding: {text}")
    engine.say(text)
    engine.runAndWait()

def keyword_match(user_input, script_lines):
    best_match = None
    best_score = 0
    user_words = user_input.split()
    for character, line in script_lines:
        line_words = line.lower().split()
        
        common_words = set(user_words).intersection(set(line_words))
        score = len(common_words) / len(user_words) if user_words else 0 
        if score > best_score and score >= MATCH_THRESHOLD:
            best_match = (character, line)
            best_score = score
    return best_match


def handle_input(user_input):
 
    if "this is a question" in user_input:
        
        script_context = "\n".join([f"{char}: {line}" for char, line in SCRIPT])
        try:
            response = model.generate_content(
                f"You are {CHARACTER_NAME}, a character in a play. Here is the script:\n{script_context}\n\n"
                f"Answer this question in character: {user_input}"
            )
            return response.text
        except Exception as e:
            print(f"Error with Gemini API: {e}")
            return ""

  
    match = keyword_match(user_input, SCRIPT)
    if match:
        character, line = match
        if character == CHARACTER_NAME:
            return line  
        else:
          
            for i in range(SCRIPT.index(match) + 1, len(SCRIPT)):
                next_char, next_line = SCRIPT[i]
                if next_char == CHARACTER_NAME:
                    return next_line
           
            return "What a great question! *Cheetos thinks deeply*" 

    return ""


def main():
    print(f"{CHARACTER_NAME} is ready! Start speaking.")
    while True:
        user_input = listen()
        if not user_input:
            continue

        if "exit" in user_input:
            respond("Farewell, until our next performance!")
            break

        response = handle_input(user_input)
        respond(response)


if __name__ == "__main__":
    main()
