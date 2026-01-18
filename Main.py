from Frontend.GUI import (
    GraphicalUserInterface,
    SetAssistantStatus,
    ShowTextToScreen,
    TempDirectoryPath,
    SetMicrophoneStatus,
    AnswerModifier,
    QueryModifier,
    GetMicrophoneStatus,
    GetAssistantStatus)
from Backend.Model import FirstLayerDMM
from Backend.RealtimeSearchEngine import RealtimeSearchEngine
from Backend.Automation import Automation, WhatsAppAutomation, ShutdownSystem, RestartSystem
from Backend.SpeechToText import SpeechRecognition
from Backend.Chatbot import ChatBot
from Backend.TextToSpeech import TextToSpeech
from dotenv import dotenv_values
from asyncio import run
from time import sleep
import subprocess
import threading
import json
import os

subprocesses = []

env_vars = dotenv_values(".env")
Username = env_vars.get("Username", "User")
Assistantname = env_vars.get("Assistantname", "Assistant")
DefaultMessage = f'''{Username} : Hello {Assistantname}, How are you?
{Assistantname} : Welcome {Username}. I am doing well. How may I help you?'''

subprocess_list = []
Functions = ["open", "close", "play", "system", "content", "google search", "youtube search"]

def ShowDefaultChatIfNoChats():
    """Initialize chat files if they don't exist or are empty"""
    try:
        with open(r"Data\ChatLog.json", "r", encoding="utf-8") as file:
            content = file.read().strip()
            
        if not content or content == "[]":
            # Initialize with empty JSON array if needed
            with open(r"Data\ChatLog.json", "w", encoding="utf-8") as file:
                json.dump([], file)
            
            # Write default message to display
            with open(TempDirectoryPath('Responses.data'), 'w', encoding='utf-8') as file:
                file.write(DefaultMessage)
                
    except FileNotFoundError:
        # Create the file if it doesn't exist
        with open(r"Data\ChatLog.json", "w", encoding="utf-8") as file:
            json.dump([], file)
        
        with open(TempDirectoryPath('Responses.data'), 'w', encoding='utf-8') as file:
            file.write(DefaultMessage)

def ReadChatLogJson():
    """Read and return chat log data"""
    try:
        with open(r"Data\ChatLog.json", 'r', encoding='utf-8') as file:
            chatlog_data = json.load(file)
        return chatlog_data if chatlog_data else []
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def SaveChatToJson(role, content):
    """Save a new chat entry to the JSON file"""
    try:
        chatlog_data = ReadChatLogJson()
        chatlog_data.append({"role": role, "content": content})
        
        with open(r"Data\ChatLog.json", 'w', encoding='utf-8') as file:
            json.dump(chatlog_data, file, indent=2, ensure_ascii=False)
            
        # Update the display after saving
        ChatLogIntegration()
        ShowChatsOnGUI()
        
    except Exception as e:
        print(f"Error saving chat: {e}")

def ChatLogIntegration():
    """Convert JSON chat log to formatted text"""
    json_data = ReadChatLogJson()
    
    if not json_data:
        # If no chats, show default message
        with open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8') as file:
            file.write(DefaultMessage)
        return
    
    formatted_chatlog = ""
    for entry in json_data:
        if entry["role"] == "user":
            formatted_chatlog += f"{Username} : {entry['content']}\n"
        elif entry["role"] == "assistant":
            formatted_chatlog += f"{Assistantname} : {entry['content']}\n"

    with open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8') as file:
        file.write(formatted_chatlog.strip())

def ShowChatsOnGUI():
    """Display chats on the GUI"""
    try:
        with open(TempDirectoryPath('Database.data'), "r", encoding='utf-8') as file:
            data = file.read()
        
        if data:
            with open(TempDirectoryPath('Responses.data'), "w", encoding='utf-8') as file:
                file.write(data)
        else:
            # If no data, show default message
            with open(TempDirectoryPath('Responses.data'), "w", encoding='utf-8') as file:
                file.write(DefaultMessage)
                
    except Exception as e:
        print(f"Error showing chats: {e}")

def InitialExecution():
    """Initialize the application"""
    SetMicrophoneStatus("False")
    ShowTextToScreen("--")
    ShowDefaultChatIfNoChats()
    ChatLogIntegration()
    ShowChatsOnGUI()

InitialExecution()

def MainExecution():
    """Main execution loop for processing queries"""
    global subprocess_list

    TaskExecution = False
    ImageExecution = False
    ImageGenerationQuery = "--"

    SetAssistantStatus("Listening...")
    Query = SpeechRecognition()
    
    # Save user query to chat log
    SaveChatToJson("user", Query)
    ShowTextToScreen(f"{Username} : {Query}")
    
    SetAssistantStatus("Thinking...")
    Decision = FirstLayerDMM(Query)

    print(f"\nDecision : {Decision}\n")

    G = any([i for i in Decision if i.startswith("general")])
    R = any([i for i in Decision if i.startswith("realtime")])

    Mearged_query = " and ".join(
        [" ".join(i.split()[1:]) for i in Decision 
         if i.startswith("general") or i.startswith("realtime")])

    # Check for image generation
    for queries in Decision:
        if "generate " in queries:
            ImageGenerationQuery = str(queries)
            ImageExecution = True

    # Check for automation tasks
    for queries in Decision:
        if not TaskExecution:
            if any(queries.startswith(func) for func in Functions):
                run(Automation(list(Decision)))
                TaskExecution = True

    # Handle image generation
    if ImageExecution:
        try:
            with open(r"Frontend\Files\ImageGeneration.data", "w") as file:
                file.write(f"{ImageGenerationQuery},True")

            p1 = subprocess.Popen(
                ['python', r'Backend\ImageGeneration.py'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
                shell=False
            )
            subprocesses.append(p1)
        except Exception as e:
            print(f"Error starting ImageGeneration.py: {e}")

    # Handle realtime search
    if (G and R) or R:
        SetAssistantStatus("Searching...")
        Answer = RealtimeSearchEngine(QueryModifier(Mearged_query))
        
        # Save assistant response to chat log
        SaveChatToJson("assistant", Answer)
        ShowTextToScreen(f"{Assistantname} : {Answer}")
        
        SetAssistantStatus("Answering...")
        TextToSpeech(Answer)
        return True

    # Handle general and other queries
    for Queries in Decision:
        if "general" in Queries:
            SetAssistantStatus("Thinking...")
            QueryFinal = Queries.replace("general ", "")
            Answer = ChatBot(QueryModifier(QueryFinal))
            
            # Save assistant response to chat log
            SaveChatToJson("assistant", Answer)
            ShowTextToScreen(f"{Assistantname} : {Answer}")
            
            SetAssistantStatus("Answering...")
            TextToSpeech(Answer)
            return True

        elif "realtime" in Queries:
            SetAssistantStatus("Searching...")
            QueryFinal = Queries.replace("realtime ", "")
            Answer = RealtimeSearchEngine(QueryModifier(QueryFinal))
            
            # Save assistant response to chat log
            SaveChatToJson("assistant", Answer)
            ShowTextToScreen(f"{Assistantname} : {Answer}")
            
            SetAssistantStatus("Answering...")
            TextToSpeech(Answer)
            return True

        elif "exit" in Queries:
            QueryFinal = "Okay, Bye!"
            Answer = ChatBot(QueryModifier(QueryFinal))
            
            # Save assistant response to chat log
            SaveChatToJson("assistant", Answer)
            ShowTextToScreen(f"{Assistantname} : {Answer}")
            
            SetAssistantStatus("Answering...")
            TextToSpeech(Answer)
            sleep(2)
            os._exit(0)

def FirstThread():
    """Background thread for handling voice commands"""
    while True:
        CurrentStatus = GetMicrophoneStatus()

        if CurrentStatus == "True":
            MainExecution()
        else:
            AIStatus = GetAssistantStatus()
            if "Available ..." not in AIStatus:
                SetAssistantStatus("Available ...")
            sleep(0.1)

def SecondThread():
    """Main GUI thread"""
    GraphicalUserInterface()

if __name__ == "__main__":
    thread2 = threading.Thread(target=FirstThread, daemon=True)
    thread2.start()
    SecondThread()