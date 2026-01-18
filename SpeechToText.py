from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import dotenv_values
import os
import mtranslate as mt

# Load environment variables
env_vars = dotenv_values(".env")
InputLanguage = env_vars.get("InputLanguage", "en-US")  # Default fallback

# HTML code for speech recognition
HtmlCode = '''<!DOCTYPE html>
<html lang="en">
<head><title>Speech Recognition</title></head>
<body>
    <button id="start" onclick="startRecognition()">Start Recognition</button>
    <button id="end" onclick="stopRecognition()">Stop Recognition</button>
    <p id="output"></p>
    <script>
        const output = document.getElementById('output');
        let recognition;

        function startRecognition() {
            recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
            recognition.lang = '';
            recognition.continuous = true;

            recognition.onresult = function(event) {
                const transcript = event.results[event.results.length - 1][0].transcript;
                output.textContent += transcript;
            };

            recognition.onend = function() {
                recognition.start();
            };
            recognition.start();
        }

        function stopRecognition() {
            if (recognition) recognition.stop();
        }
    </script>
</body>
</html>'''

# Inject language setting
HtmlCode = HtmlCode.replace("recognition.lang = '';", f"recognition.lang = '{InputLanguage}';")

# Save HTML file
html_path = os.path.join("Data", "Voice.html")
os.makedirs("Data", exist_ok=True)
with open(html_path, "w", encoding="utf-8") as f:
    f.write(HtmlCode)

# Chrome driver setup
chrome_options = Options()
chrome_options.add_argument("--use-fake-ui-for-media-stream")
chrome_options.add_argument("--use-fake-device-for-media-stream")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument("--headless=new")

# Optional user-agent
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100 Safari/537.36"
chrome_options.add_argument(f"user-agent={user_agent}")

# Initialize driver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# Temp directory
TempDirPath = os.path.join("Frontend", "Files")
os.makedirs(TempDirPath, exist_ok=True)

# Set assistant status
def SetAssistantStatus(Status):
    with open(os.path.join(TempDirPath, "Status.data"), "w", encoding="utf-8") as file:
        file.write(Status)

# Clean and format query
def QueryModifier(Query):
    new_query = Query.lower().strip()
    question_words = ["how", "what", "who", "where", "when", "why", "which", "whose", "whom", "can you"]

    if any(new_query.startswith(qw) for qw in question_words):
        if not new_query.endswith("?"):
            new_query += "?"
    else:
        if not new_query.endswith("."):
            new_query += "."

    return new_query.capitalize()

# Translate to English
def UniversalTranslator(Text):
    translated = mt.translate(Text, "en", "auto")
    return translated.capitalize()

# Voice recognition logic
def SpeechRecognition():
    driver.get("file:///" + os.path.abspath(html_path))
    driver.find_element(By.ID, "start").click()

    while True:
        try:
            Text = driver.find_element(By.ID, "output").text.strip()
            if Text:
                driver.find_element(By.ID, "end").click()

                if InputLanguage.lower().startswith("en"):
                    return QueryModifier(Text)
                else:
                    SetAssistantStatus("Translating...")
                    return QueryModifier(UniversalTranslator(Text))
        except:
            continue

# Main
if __name__ == "__main__":
    while True:
        result = SpeechRecognition()
        print(f"🗣 Recognized: {result}")