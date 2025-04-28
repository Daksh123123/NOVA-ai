import google.generativeai as genai
import pyttsx3
import speech_recognition as sr
import subprocess
import re
import threading
import time
from apikey import api_data

# Global control flags
is_paused = False
lock = threading.Lock()

# Configure Gemini API
genai.configure(api_key=api_data)

# Text-to-Speech setup
engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)
engine.setProperty('rate', 150)

# Speak with pause support
def speak(text):
    global is_paused
    print(f"\nNOVA: {text}")
    chunks = re.split(r'(?<=[.?!])\s+', text)

    for chunk in chunks:
        with lock:
            if is_paused:
                print("🟡 Speech paused...")
                break
        engine.say(chunk)
        engine.runAndWait()
        time.sleep(0.2)

# Pause/resume functions
def pause():
    global is_paused
    with lock:
        is_paused = True
    print("\n🟡 STATUS: Paused (Not Listening)")
    speak("Pausing. Say 'resume' to continue.")

def resume():
    global is_paused
    with lock:
        is_paused = False
    print("\n🟢 STATUS: Active (Listening)")
    speak("Resuming NOVA.")

# Wake word listener
def listen_for_wake_word():
    recognizer = sr.Recognizer()
    mic_index = 1
    with sr.Microphone(device_index=mic_index) as source:
        print("\nListening for wake word...")
        recognizer.pause_threshold = 0.5
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        recognizer.energy_threshold = 150
        try:
            audio = recognizer.listen(source, timeout=6, phrase_time_limit=5)
            query = recognizer.recognize_google(audio, language='en-IN').lower()
            print(f"You: {query}")
            return query
        except:
            return "none"

# Command listener
def listen_to_command():
    recognizer = sr.Recognizer()
    mic_index = 1
    with sr.Microphone(device_index=mic_index) as source:
        print("\nListening for command...")
        recognizer.pause_threshold = 0.5
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        recognizer.energy_threshold = 150
        try:
            audio = recognizer.listen(source, timeout=6, phrase_time_limit=8)
            query = recognizer.recognize_google(audio, language='en-IN').lower()
            print(f"You: {query}")
            return query
        except:
            speak("Sorry, I didn't catch that.")
            return "none"

# Generate Gemini AI response
def generate_response(query):
    identity_questions = [
        "who created you", "who made you", "who is your creator", "what are you", "who developed you"
    ]
    if any(phrase in query for phrase in identity_questions):
        return "I am NOVA, the Neural Operated Virtual Assistant. I was developed by Daksh and Vivaan, using advanced AI technologies provided by Google."

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(
            query,
            generation_config=genai.GenerationConfig(
                max_output_tokens=150,
                temperature=0.1,
            )
        )
        return response.text
    except Exception as e:
        return f"Sorry, I encountered an error: {e}"

# Launch common apps
def launch_application(command):
    apps = {
        "notepad": "notepad.exe",
        "calculator": "calc.exe",
        "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        "command prompt": "cmd.exe",
        "paint": "mspaint.exe",
        "explorer": "explorer.exe",
    }
    for key in apps:
        if key in command:
            try:
                subprocess.Popen(apps[key])
                speak(f"Opening {key}")
                return True
            except:
                speak(f"Failed to open {key}")
                return True
    return False

# Main loop
def main():
    global is_paused
    print("\n🟢 STATUS: Active (Listening)")
    speak("NOVA, the Neural Operated Virtual Assistant created by Daksh and Vivaan, is now active and listening.")

    while True:
        if is_paused:
            query = listen_for_wake_word()
            if "resume" in query:
                resume()
            continue

        query = listen_for_wake_word()
        if query == "none":
            continue

        if "pause" in query:
            pause()
            continue

        if "resume" in query:
            resume()
            continue

        if any(x in query for x in ["nova", "hey nova"]):
            speak("Yes, how can I assist?")
            command = listen_to_command()

            if command == "none":
                continue

            if any(x in command for x in ["exit", "quit", "bye", "stop"]):
                speak("Goodbye! NOVA signing off.")
                break

            if "pause" in command:
                pause()
                continue

            if "resume" in command:
                resume()
                continue

            if launch_application(command):
                continue

            response = generate_response(command)
            speak(response)

# Entry point
if __name__ == "__main__":
    main()
