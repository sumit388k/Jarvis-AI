import cohere  # Import the Cohere library for AI services.
from rich import print  # Import the Rich library to enhance terminal outputs.
from dotenv import dotenv_values  # Import dotenv to load environment variables from a .env file.

# Optionally load key from .env
# config = dotenv_values(".env")
# api_key = config.get("COHERE_API_KEY")
# co = cohere.Client(api_key=api_key)

co = cohere.Client(api_key="2VD6L7CnFYP6AmxVGfH0AbHQdgj0MMcBlYHtu1o5")

funcs = [
    "exit", "general", "realtime", "open", "close", "play",
    "generate image", "system", "content", "google search",
    "youtube search", "reminder", "screenshot"
]

messages = []

preamble = """
You are a very accurate Decision-Making Model, which decides what kind of a query is given to you.
You will decide whether a query is a 'general' query, a 'realtime' query, or is asking to perform any task or automation like 'open facebook, instagram', 'can you write a application and open it in notepad'
*** Do not answer any query, just decide what kind of query is given to you. ***
... (rest of your preamble, unchanged)
"""

ChatHistory = [
    {"role": "User", "message": "how are you?"},
    {"role": "Chatbot", "message": "general how are you?"},
    {"role": "User", "message": "do you like pizza?"},
    {"role": "Chatbot", "message": "general do you like pizza?"},
    {"role": "User", "message": "open chrome and tell me about mahatma gandhi."},
    {"role": "Chatbot", "message": "open chrome, general tell me about mahatma gandhi."},
    {"role": "User", "message": "open chrome and firefox"},
    {"role": "Chatbot", "message": "open chrome, open firefox"},
    {"role": "User", "message": "what is today's date and by the way remind me that i have a dancing performance on"},
    {"role": "Chatbot", "message": "general what is today's date, reminder 11:00pm 5th aug dancing performance"},
    {"role": "User", "message": "chat with me."},
    {"role": "Chatbot", "message": "general chat with me."}
]

def FirstLayerDMM(prompt: str = "test"):
    messages.append({"role": "user", "content": f"{prompt}"})

    stream = co.chat_stream(
        model="command-a-03-2025",
        message=prompt,
        temperature=0.7,
        chat_history=ChatHistory,
        prompt_truncation="OFF",
        connectors=[],
        preamble=preamble
    )

    response = ""
    for event in stream:
        if event.event_type == "text-generation":
            response += event.text

    print("[DEBUG] Raw Cohere response:", response)  # Debug print


    import re
    response_items = [i.strip().lower() for i in response.replace("\n", "").split(",") if i.strip()]
    temp = []
    for task in response_items:
        # Remove known prefixes
        if task.startswith("task/automation "):
            task = task.replace("task/automation ", "")
        elif task.startswith("task/automation:"):
            task = task.replace("task/automation:", "")
        task = task.strip()
        # WhatsApp intent extraction (robust)
        whatsapp_patterns = [
            r"open (the )?whatsapp",
            r"send message to ([\w ,]+) saying ['\"](.+?)['\"]",
            r"read latest message from ([\w ]+)",
            r"reply to ([\w ]+) saying ['\"](.+?)['\"]",
            r"send (image|video|file) to ([\w ]+) from ['\"](.+?)['\"]",
            r"is whatsapp open",
            r"close whatsapp"
        ]
        # Refined WhatsApp intent mapping
        if re.search(r"close( the)? whatsapp", task) or re.search(r"close( it)?", task):
            temp.append("close whatsapp")
        elif re.search(r"open( the)? whatsapp", task):
            temp.append("open whatsapp")
        # Robust shutdown intent mapping
        elif re.search(r"shutdown( the)?( pc| laptop)?", task) or re.search(r"jarvis shutdown", task):
            temp.append("shutdown")
        else:
            for pat in whatsapp_patterns:
                if re.search(pat, task):
                    temp.append(task)
                    break
            else:
                # Image generation intent mapping
                if re.search(r"(generate|create|make) (an? )?image( of)?", task):
                    temp.append(f"generate image {task.split('image',1)[-1].strip()}")
                # Google search intent mapping
                elif re.search(r"go to (the )?google( and)? search (.+)", task):
                    search_term = re.search(r"go to (the )?google( and)? search (.+)", task).group(3)
                    temp.append(f"google search {search_term}")
                else:
                    for func in funcs:
                        if task.startswith(func):
                            temp.append(task)
    response = temp

    print("[DEBUG] Parsed Decision List:", response)  # Debug print

    if "(query)" in response:
        return FirstLayerDMM(prompt=prompt)
    else:
        return response


if __name__ == "__main__":
    while True:
        user_input = input(">>> ")
        print(FirstLayerDMM(user_input))
