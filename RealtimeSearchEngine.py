# RealtimeSearchEngine.py
from googlesearch import search
from groq import Groq
from json import load, dump
import datetime
from dotenv import dotenv_values
import sys

# Load environment variables
env_vars = dotenv_values(".env")
Username = env_vars.get("Username", "User")
Assistantname = env_vars.get("Assistantname", "Assistant")
GroqAPIKey = env_vars.get("GroqAPIKey")
# Put preferred model in .env as GroqModel, fallback to a common available model
GroqModel = env_vars.get("GroqModel", "llama-3.1-8b-instant")

if not GroqAPIKey:
    print("Error: GroqAPIKey not found in .env. Please add GroqAPIKey to .env file.")
    sys.exit(1)

client = Groq(api_key=GroqAPIKey)

System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which has real-time up-to-date information from the internet.
*** Provide Answers In a Professional Way, make sure to add full stops, commas, question marks, and use proper grammar.***
*** Just answer the question from the provided data in a professional way. ***"""

# Ensure chat log exists (try/except)
try:
    with open(r"Data\ChatLog.json", "r", encoding="utf-8") as f:
        messages = load(f)
except Exception:
    try:
        with open(r"Data\ChatLog.json", "w", encoding="utf-8") as f:
            dump([], f)
    except Exception as e:
        print("Error creating ChatLog.json:", e)
    messages = []

def GoogleSearch(query):
    try:
        results = list(search(query, advanced=True, num_results=5))
    except Exception as e:
        return f"[Search error: {e}]"

    Answer = f"The search results for '{query}' are:\n[start]\n"
    for i in results:
        # safe extraction for title/description for different result types
        title = None
        desc = None
        try:
            title = getattr(i, "title", None)
        except Exception:
            title = None
        try:
            desc = getattr(i, "description", None)
        except Exception:
            desc = None

        # if it's a dict-like (some googlesearch implementations)
        if (not title or title == None) and isinstance(i, dict):
            title = i.get("title") or title
            desc = i.get("description") or desc

        if not title and not desc:
            Answer += f"{str(i)}\n\n"
        else:
            if title:
                Answer += f"Title: {title}\n"
            if desc:
                Answer += f"Description: {desc}\n\n"
    Answer += "[end]"
    return Answer

def AnswerModifier(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    modified_answer = '\n'.join(non_empty_lines)
    return modified_answer

SystemChatBot = [
    {"role": "system", "content": System},
    {"role": "user", "content": "Hi"},
    {"role": "assistant", "content": "Hello, how can I help you?"}
]

def Information():
    data = ""
    current_date_time = datetime.datetime.now()
    day = current_date_time.strftime("%A")
    date = current_date_time.strftime("%d")
    month = current_date_time.strftime("%B")
    year = current_date_time.strftime("%Y")
    hour = current_date_time.strftime("%H")
    minute = current_date_time.strftime("%M")
    second = current_date_time.strftime("%S")
    data += "Use This Real-time Information if needed:\n"
    data += f"Day: {day}\n"
    data += f"Date: {date}\n"
    data += f"Month: {month}\n"
    data += f"Year: {year}\n"
    data += f"Time: {hour} hours, {minute} minutes, {second} seconds.\n"
    return data

def RealtimeSearchEngine(prompt):
    global SystemChatBot, messages

    # Reload chat log to avoid race conditions across runs
    try:
        with open(r"Data\ChatLog.json", "r", encoding="utf-8") as f:
            messages = load(f)
    except Exception:
        messages = []

    messages.append({"role": "user", "content": prompt})

    # Append Google search result temporarily
    search_result = GoogleSearch(prompt)
    SystemChatBot.append({"role": "system", "content": search_result})

    combined = SystemChatBot + [{"role": "system", "content": Information()}] + messages

    Answer = ""
    try:
        completion = client.chat.completions.create(
            model=GroqModel,
            messages=combined,
            temperature=0.7,
            max_tokens=1024,
            top_p=1,
            stream=True,
            stop=None
        )

        # Streamed response: extract content safely
        for chunk in completion:
            content = None
            try:
                # typical object attribute access
                content = chunk.choices[0].delta.content
            except Exception:
                try:
                    # dict-like fallback
                    content = chunk.get("choices", [])[0].get("delta", {}).get("content")
                except Exception:
                    content = None

            if content:
                Answer += content

    except Exception as e:
        # Print detailed error for debugging
        print("Groq API error:", e)
        # Remove temporary system message before returning
        try:
            SystemChatBot.pop()
        except Exception:
            pass
        return f"[Error from Groq API: {e}]"

    # Clean and save
    Answer = Answer.strip().replace("</s>", "")
    messages.append({"role": "assistant", "content": Answer})

    try:
        with open(r"Data\ChatLog.json", "w", encoding="utf-8") as f:
            dump(messages, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print("Error saving chat log:", e)

    # Remove the last temporary system search message
    try:
        SystemChatBot.pop()
    except Exception:
        pass

    return AnswerModifier(Answer)

if __name__ == "__main__":
    print("Realtime Search Engine started. Type your query and press Enter.")
    while True:
        try:
            prompt = input("Enter your query: ").strip()
            if not prompt:
                continue
            response = RealtimeSearchEngine(prompt)
            print("\n=== Response ===")
            print(response)
            print("================\n")
        except KeyboardInterrupt:
            print("\nExiting.")
            break
        except Exception as e:
            print("Runtime error:", e)
            break
