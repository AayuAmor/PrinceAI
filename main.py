from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.core.window import Window
import speech_recognition as sr
import pyttsx3  # Corrected from pytssx3
import pywhatkit
import datetime
import wikipedia
import pyjokes
import re

class PrinceAssistantApp(App):
    def build(self):
        # Initialize speech recognition & TTS
        self.recognizer = sr.Recognizer()
        self.engine = pyttsx3.init()
        self.setup_voice()
        
        # UI Layout
        Window.clearcolor = (0.9, 0.9, 0.95, 1)  # Light gray background
        layout = BoxLayout(orientation='vertical', padding=15, spacing=15)
        
        # Title Label
        self.title_label = Label(
            text="🤖 Prince Assistant", 
            font_size='24sp',
            bold=True,
            color=(0.2, 0.4, 0.8, 1)  # Blue text
        )
        
        # Scrollable response area
        scroll = ScrollView(size_hint=(1, 0.7))
        self.response_label = Label(
            text="👋 Say 'Hello Prince' or press the mic button", 
            font_size='18sp',
            halign='left',
            valign='top',
            size_hint_y=None,
            text_size=(Window.width - 30, None),
            markup=True,
            color=(0, 0, 0, 1)  # Black text
        )
        self.response_label.bind(size=self.response_label.setter('text_size'))
        scroll.add_widget(self.response_label)
        
        # Status label
        self.status_label = Label(
            text="🔴 Ready", 
            font_size='16sp',
            italic=True,
            color=(0.5, 0.5, 0.5, 1)  # Gray text
        )
        
        # Mic button
        self.mic_button = Button(
            text="🎤 Hold to Speak",
            size_hint=(1, 0.15),
            background_normal='',
            background_color=(0.2, 0.6, 1, 1),  # Blue button
            color=(1, 1, 1, 1),  # White text
            font_size='20sp'
        )
        self.mic_button.bind(on_press=self.start_listening)
        self.mic_button.bind(on_release=self.process_command)
        
        # Add all widgets
        layout.add_widget(self.title_label)
        layout.add_widget(scroll)
        layout.add_widget(self.status_label)
        layout.add_widget(self.mic_button)
        
        return layout

    def setup_voice(self):
        voices = self.engine.getProperty('voices')
        female_voice = next((v for v in voices if "female" in v.name.lower()), voices[1])
        self.engine.setProperty('voice', female_voice.id)
        self.engine.setProperty('rate', 150)

    def speak(self, text):
        self.response_label.text += f"\n[color=3333ff]🤖 {text}[/color]"  # Blue text for assistant
        self.engine.say(text)
        self.engine.runAndWait()

    def start_listening(self, instance):
        self.status_label.text = "🟢 Listening..."
        self.status_label.color = (0, 0.7, 0, 1)  # Green when listening
        Clock.schedule_once(self.listen_command, 0.1)

    def listen_command(self, dt):
        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source)
                audio = self.recognizer.listen(
                    source,
                    timeout=5,
                    phrase_time_limit=5
                )
                command = self.recognizer.recognize_google(audio).lower()
                self.response_label.text += f"\n[color=ff3333]🎤 You: {command}[/color]"  # Red text for user
                return command
        except sr.UnknownValueError:
            self.response_label.text += "\n[color=ff3333]❌ Could not understand audio[/color]"
            return None
        except Exception as e:
            self.response_label.text += f"\n[color=ff3333]❌ Error: {str(e)}[/color]"
            return None
        finally:
            self.status_label.text = "🔴 Ready"
            self.status_label.color = (0.5, 0.5, 0.5, 1)

    def process_command(self, instance):
        command = self.listen_command(None)
        if not command:
            return

        # Exit command
        if any(word in command for word in ["exit", "quit", "goodbye"]):
            self.speak("Goodbye, sir!")
            App.get_running_app().stop()
            return

        # Activation phrase
        if "hello prince" in command:
            self.speak("Yes sir, how can I help?")
        
        # Music playback
        elif "play" in command:
            song = re.sub(r"play|song|music|by", "", command).strip()
            if song:
                self.speak(f"Playing {song}...")
                pywhatkit.playonyt(song)
            else:
                self.speak("What song would you like me to play?")
        
        # Time query
        elif "time" in command:
            current_time = datetime.datetime.now().strftime("%I:%M %p")
            self.speak(f"⏰ Current time is {current_time}")
        
        # Date query
        elif "date" in command:
            current_date = datetime.datetime.now().strftime("%A, %B %d, %Y")
            self.speak(f"📅 Today is {current_date}")
        
        # Jokes
        elif "joke" in command:
            self.speak(pyjokes.get_joke())
        
        # Wikipedia lookups
        elif any(phrase in command for phrase in ["who is", "what is", "tell me about", "wikipedia"]):
            query = re.sub(r"who is|what is|tell me about|wikipedia", "", command).strip()
            if query:
                try:
                    self.speak(f"Searching Wikipedia for {query}...")
                    # Get summary and clean it up
                    summary = wikipedia.summary(query, sentences=3, auto_suggest=False)
                    summary = re.sub(r'\([^)]*\)', '', summary)  # Remove parentheses
                    self.speak(f"According to Wikipedia:\n{summary}")
                except wikipedia.DisambiguationError as e:
                    options = '\n'.join(e.options[:3])  # Show first 3 options
                    self.speak(f"Multiple options found. Be more specific:\n{options}")
                except wikipedia.PageError:
                    self.speak("Sorry, I couldn't find information about that.")
            else:
                self.speak("What would you like me to look up?")
        
        # Default response
        else:
            self.speak("Sorry, I didn't understand that. Try:\n• 'Play [song]'\n• 'What is AI?'\n• 'Tell me a joke'")

if __name__ == "__main__":
    PrinceAssistantApp().run()