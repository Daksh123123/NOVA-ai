import google.generativeai as genai
import pyttsx3
import speech_recognition as sr
import subprocess
from apikey import api_data

# Configure Gemini API
genai.configure(api_key=api_data)

# Text-to-Speech setup with robotic voice
engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)
engine.setProperty('rate', 150)

def speak(text):
    print(f"Bumblebee: {text}")
    engine.say(text)
    engine.runAndWait()

def listen_for_wake_word():
    recognizer = sr.Recognizer()
    mic_index = 1  # Update if needed
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

def listen_to_command():
    recognizer = sr.Recognizer()
    mic_index = 1  # Update if needed
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

def generate_response(query):
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

def main():
    speak("Bumblebee is now listening for your command.")
    while True:
        query = listen_for_wake_word()
        if query == "none":
            continue

        if "bumblebee" in query or "hey bumblebee" in query:
            speak("Yes, how can I assist?")
            command = listen_to_command()

            if command == "none":
                continue

            if any(x in command for x in ["exit", "quit", "bye", "goodbye"]):
                speak("Goodbye! Shutting down.")
                break

            if launch_application(command):
                continue

            response = generate_response(command)
            speak(response)

if __name__ == "__main__":
    main()
