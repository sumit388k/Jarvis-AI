
from AppOpener import close, open as appopen
from webbrowser import open as webopen
from pywhatkit import search, playonyt
from dotenv import dotenv_values
from bs4 import BeautifulSoup
from rich import print
from groq import Groq
import webbrowser
import subprocess
import requests
import keyboard
import asyncio
import os
import shutil
from pathlib import Path
import time
import pyautogui
from datetime import datetime
import re

# Load environment variables
env_vars = dotenv_values(".env")
GroqAPIKey = env_vars.get("GroqAPIKey")
useragent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36'

client = Groq(api_key=GroqAPIKey)

messages = []
SystemChatBot = [{
    "role": "system",
    "content": f"Hello, I am {os.environ['Username']}, You're a content writer. You can write letters, codes, applications, essays, notes, songs, poems etc."
}]

# === Utility Functions ===

def GoogleSearch(Topic):
    search(Topic)
    return True

def Content(Topic):
    def OpenNotepad(File):
        subprocess.Popen(['notepad.exe', File])

    def ContentWriterAI(prompt):
        messages.append({"role": "user", "content": f"{prompt}"})
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=SystemChatBot + messages,
            max_tokens=2048,
            temperature=0.7,
            top_p=1,
            stream=True,
            stop=None
        )
        Answer = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                Answer += chunk.choices[0].delta.content
        Answer = Answer.replace("</s>", "")
        messages.append({"role": "assistant", "content": Answer})
        return Answer

    Topic: str = Topic.replace("Content", "")
    ContentByAI = ContentWriterAI(Topic)

    # ✅ Safe file naming
    safe_topic = re.sub(r'[<>:"/\\|?*]', '', Topic.lower().replace(' ', ''))
    filepath = rf"Data\{safe_topic}.txt"

    with open(filepath, "w", encoding="utf-8") as file:
        file.write(ContentByAI)
    OpenNotepad(filepath)
    return True

def YouTubeSearch(Topic):
    Url4Search = f"https://www.youtube.com/results?search_query={Topic}"
    webbrowser.open(Url4Search)
    return True

def PlayYoutube(query):
    playonyt(query)
    return True

def ExtractFolderName(query: str) -> str:
    query = query.lower().strip()
    if "open" in query and "folder" in query:
        query = query.replace("open", "").replace("folder", "").strip()
    return query

def FindAndOpenFolder(folder_name: str):
    print(f"🔍 Searching for folder: {folder_name}")
    base_dirs = [Path("C:/Users/suren/OneDrive/Desktop"), Path.home(), Path("D:/"), Path("E:/")]

    search_name = folder_name.lower().replace("folder", "").replace(" ", "").strip()

    for base_dir in base_dirs:
        try:
            for root, dirs, files in os.walk(base_dir, topdown=True):
                dirs[:] = [d for d in dirs if not d.startswith("$") and not d.startswith(".")]
                for dir_name in dirs:
                    if search_name in dir_name.lower().replace(" ", ""):
                        full_path = os.path.join(root, dir_name)
                        print(f"✅ Folder Found: {full_path}")
                        os.startfile(full_path)
                        return f"✅ Opened folder: {full_path}"
        except Exception as e:
            print(f"⚠️ Skipping {base_dir}: {e}")
            continue

    print(f"❌ Folder '{folder_name}' not found.")
    return f"❌ Folder '{folder_name}' not found."

def FindFolderByName(folder_name, search_dir):
    folder_name = folder_name.lower().strip()
    for root, dirs, _ in os.walk(search_dir):
        for name in dirs:
            if folder_name in name.lower():
                return os.path.join(root, name)
    return None

def CopyFilesOrFolders(source_name, target_name):
    from Backend.TextToSpeech import TextToSpeech
    base_dirs = [Path("C:/Users/suren/OneDrive/Desktop"), Path.home(), Path("D:/"), Path("E:/")]

    source_path, target_path = None, None
    for base in base_dirs:
        if not source_path:
            source_path = FindFolderByName(source_name, base)
        if not target_path:
            target_path = FindFolderByName(target_name, base)

    if not source_path:
        TextToSpeech(f"Source folder {source_name} not found.")
        return False
    if not target_path:
        TextToSpeech(f"Target folder {target_name} not found.")
        return False

    try:
        for item in os.listdir(source_path):
            src_item = os.path.join(source_path, item)
            dst_item = os.path.join(target_path, item)

            if os.path.isdir(src_item):
                shutil.copytree(src_item, dst_item, dirs_exist_ok=True)
            else:
                shutil.copy2(src_item, dst_item)

        TextToSpeech(f"Copied all files from {source_name} to {target_name}")
        print(f"✅ Copied from {source_path} to {target_path}")
        return True
    except Exception as e:
        TextToSpeech("Failed to copy files.")
        print(f"❌ Copy error: {e}")
        return False

def OpenApp(app, sess=requests.session()):
    from urllib.parse import quote_plus
    app = app.strip()
    app_name = app.upper()
    print(f"[OpenApp] Called with app: {app}")

    if "folder" in app.lower():
        folder_name = ExtractFolderName(app)
        return FindAndOpenFolder(folder_name)

    if "whatsapp" in app.lower():
        possible_paths = [
            r"C:\Users\suren\AppData\Local\WhatsApp\WhatsApp.exe",
            r"C:\Program Files\WindowsApps\5319275A.WhatsAppDesktop_2.2412.2.0_x64__cv1g1gvanyjgm\WhatsApp.exe",
            r"C:\Program Files\WhatsApp\WhatsApp.exe",
            r"C:\Program Files (x86)\WhatsApp\WhatsApp.exe"
        ]
        for whatsapp_path in possible_paths:
            if os.path.exists(whatsapp_path):
                try:
                    os.startfile(whatsapp_path)
                    from Backend.TextToSpeech import TextToSpeech
                    TextToSpeech("What can I help you with in WhatsApp?")
                    return True
                except Exception as e:
                    print(f"[OpenApp] os.startfile failed: {e}")

    try:
        appopen(app, match_closest=True, output=True, throw_error=True)
        if "whatsapp" in app.lower():
            from Backend.TextToSpeech import TextToSpeech
            TextToSpeech("What can I help you with in WhatsApp?")
        return True
    except Exception as e:
        print(f"❌ {app_name} not found: {e}")
        try:
            webopen(f"https://www.google.com/search?q={quote_plus(app)}")
            print(f"✅ Opened {app_name} via Google fallback")
            return True
        except Exception as e2:
            print(f"❌ Failed to open {app_name}: {e2}")
            return False

def CloseApp(app):
    if "chrome" in app:
        return False
    try:
        close(app, match_closest=True, output=True, throw_error=True)
        return True
    except Exception as e:
        if "whatsapp" in app.lower():
            try:
                result = os.system("taskkill /f /im WhatsApp.exe")
                return result == 0
            except:
                return False
        return False

def System(command):
    def mute(): keyboard.press_and_release("volume mute")
    def unmute(): keyboard.press_and_release("volume unmute")
    def volume_up(): keyboard.press_and_release("volume up")
    def volume_down(): keyboard.press_and_release("volume down")

    match command:
        case "mute": mute()
        case "unmute": unmute()
        case "volume up": volume_up()
        case "volume down": volume_down()
    return True

def LockSystem():
    import platform
    system_platform = platform.system()
    if system_platform == "Windows":
        os.system("rundll32.exe user32.dll,LockWorkStation")
    elif system_platform == "Linux":
        os.system("gnome-screensaver-command -l")
    elif system_platform == "Darwin":
        os.system("/System/Library/CoreServices/Menu\ Extras/User.menu/Contents/Resources/CGSession -suspend")
    else:
        print("[red]❌ Unsupported OS for lock.[/red]")

def ShutdownSystem():
    import platform
    if platform.system() == "Windows":
        os.system("shutdown /s /t 1")
    elif platform.system() == "Linux":
        os.system("shutdown now")
    elif platform.system() == "Darwin":
        os.system("sudo shutdown -h now")

def RestartSystem():
    import platform
    if platform.system() == "Windows":
        os.system("shutdown /r /t 1")
    elif platform.system() == "Linux":
        os.system("reboot")
    elif platform.system() == "Darwin":
        os.system("sudo shutdown -r now")

def TakeScreenshot():
    try:
        filename = datetime.now().strftime("screenshot_%Y%m%d_%H%M%S.png")
        folder = "Data"
        os.makedirs(folder, exist_ok=True)
        filepath = os.path.join(folder, filename)

        screenshot = pyautogui.screenshot()
        screenshot.save(filepath)
        os.startfile(filepath)

        try:
            from Backend.TextToSpeech import TextToSpeech
            TextToSpeech("Screenshot taken successfully.")
        except:
            pass
        return True
    except Exception as e:
        print(f"[red]❌ Failed to take screenshot: {e}[/red]")
        return False

def WhatsAppAutomation(query):
    try:
        query = query.lower()
        print(f"[WhatsAppAutomation] Received query: {query}")

        if "status" in query:
            pyautogui.hotkey('ctrl', 'tab')
            pyautogui.hotkey('ctrl', 'tab')
            pyautogui.hotkey('ctrl', 'tab')
            pyautogui.press('enter')
            return "Opened WhatsApp status"

        elif "call" in query:
            pyautogui.hotkey('ctrl', 'tab')
            pyautogui.hotkey('ctrl', 'tab')
            pyautogui.press('enter')
            return "Opened WhatsApp calls"

        elif "chat" in query or "open chat" in query:
            name = query.split("chat with")[-1].strip()
            pyautogui.hotkey('ctrl', 'f')
            time.sleep(1)
            pyautogui.write(name)
            pyautogui.press('enter')
            return f"Opened chat with {name}"

        elif "send message" in query and "to" in query and "saying" in query:
            try:
                name = query.split("to")[1].split("saying")[0].strip()
                message = query.split("saying")[1].strip()
                pyautogui.hotkey('ctrl', 'f')
                time.sleep(1)
                pyautogui.write(name)
                pyautogui.press('enter')
                time.sleep(1)
                pyautogui.write(message)
                pyautogui.press('enter')
                return f"Message sent to {name}: {message}"
            except Exception as e:
                return f"Error sending message: {e}"

        else:
            return "WhatsApp command not recognized"

    except Exception as e:
        return f"WhatsApp automation error: {e}"


# === Core Automation Logic ===

async def TranslateAndExecute(commands: list[str]):
    funcs = []
    for command in commands:
        command = command.lower().strip()

        if ("open youtube" in command or "youtube" in command) and "play" in command:
            match = re.search(r'play (.+)', command)
            if match:
                song = match.group(1).strip()
                funcs.append(asyncio.to_thread(PlayYoutube, song))
                continue

        if command.startswith("open"):
            funcs.append(asyncio.to_thread(OpenApp, command.removeprefix("open").strip()))
        elif command.startswith("close"):
            funcs.append(asyncio.to_thread(CloseApp, command.removeprefix("close").strip()))
        elif command.startswith("play "):
            funcs.append(asyncio.to_thread(PlayYoutube, command.removeprefix("play").strip()))
        elif command.startswith("content"):
            funcs.append(asyncio.to_thread(Content, command.removeprefix("content").strip()))
        elif command.startswith("google search "):
            funcs.append(asyncio.to_thread(GoogleSearch, command.removeprefix("google search").strip()))
        elif command.startswith("youtube search"):
            funcs.append(asyncio.to_thread(YouTubeSearch, command.removeprefix("youtube search").strip()))
        elif command.startswith("system "):
            funcs.append(asyncio.to_thread(System, command.removeprefix("system").strip()))
        elif command.startswith("screenshot"):
            funcs.append(asyncio.to_thread(TakeScreenshot))
        elif "shutdown" in command:
            funcs.append(asyncio.to_thread(ShutdownSystem))
        elif "restart" in command:
            funcs.append(asyncio.to_thread(RestartSystem))
        elif "lock" in command:
            funcs.append(asyncio.to_thread(LockSystem))
        elif "whatsapp" in command:
            funcs.append(asyncio.to_thread(WhatsAppAutomation, command))
        else:
            print(f"[red]No Function Found for: ({command})[/red]")

    results = await asyncio.gather(*funcs)
    for result in results:
        if isinstance(result, str):
            yield result
        else:
            yield result

async def Automation(commands: list[str]):
    async for result in TranslateAndExecute(commands):
        print(result)
    return True

# === Manual Test Entry Point ===
if __name__ == "__main__":
    asyncio.run(Automation(["open whatsapp", "shutdown the pc"]))
