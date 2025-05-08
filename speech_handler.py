import pyttsx3
import speech_recognition as sr
import time
import os

class AudioConfig:
    """Audio configuration settings"""
    SPEECH_RATE = 150
    VOLUME = 1.0
    TIMEOUT = 60
    PHRASE_TIME_LIMIT = 60
    AMBIENT_DURATION = 3
    LANGUAGE = "en-US"

def init_speech_engine():
    """Initialize and configure the text-to-speech engine"""
    engine = pyttsx3.init()
    engine.setProperty('rate', AudioConfig.SPEECH_RATE)
    engine.setProperty('volume', AudioConfig.VOLUME)
    return engine

def recognize_speech():
    """
    Record and transcribe speech to text with improved error handling and feedback.
    """
    recognizer = sr.Recognizer()
    
    try:
        with sr.Microphone() as source:
            # Calibrate for ambient noise
            print("Calibrating for ambient noise...")
            recognizer.adjust_for_ambient_noise(source, duration=AudioConfig.AMBIENT_DURATION)
            
            print("Listening... Please speak clearly.")
            audio = recognizer.listen(
                source,
                timeout=AudioConfig.TIMEOUT,
                phrase_time_limit=AudioConfig.PHRASE_TIME_LIMIT
            )
            
            # First try Google's speech recognition
            try:
                text = recognizer.recognize_google(audio, language=AudioConfig.LANGUAGE)
                return text
            except sr.RequestError:
                # If Google fails, try offline recognition if available
                try:
                    text = recognizer.recognize_sphinx(audio)
                    return text
                except:
                    raise sr.RequestError("All speech recognition services failed")
                    
    except sr.WaitTimeoutError:
        return "No speech detected. Please try again."
    except sr.UnknownValueError:
        return "Speech was not understood. Please speak more clearly."
    except sr.RequestError as e:
        return f"Could not process speech: {str(e)}"
    except Exception as e:
        return f"An error occurred: {str(e)}"

def speak_text(text):
    """
    Convert text to speech with error handling and multiple engine support.
    """
    try:
        engine = init_speech_engine()
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"Error in text-to-speech: {str(e)}")
        # Fallback to alternative TTS if available
        try:
            os.system(f'say "{text}"')  # macOS fallback
        except:
            print("Text-to-speech failed. Displaying text only.")