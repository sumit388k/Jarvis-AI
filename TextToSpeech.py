import pygame
import random
import asyncio
import edge_tts
import os
from dotenv import dotenv_values
import sys

# Load environment variables from a .env file
env_vars = dotenv_values(".env")
AssistantVoice = env_vars.get("AssistantVoice", "en-IN-NeerjaNeural")

# Asynchronous function to convert text to an audio file
async def TextToAudioFile(text) -> bool:
    file_path = r"Data\speech.mp3"
    
    # Create Data directory if it doesn't exist
    os.makedirs("Data", exist_ok=True)
    
    # Check if the file already exists and remove it
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except Exception as e:
            print(f"⚠️  Error removing old file: {e}")
    
    # List of voices to try if the primary one fails
    voices_to_try = [
        AssistantVoice,
        "en-US-GuyNeural",
        "en-US-AriaNeural",
        "en-GB-RyanNeural",
        "en-CA-LiamNeural"
    ]
    
    # Remove duplicates while maintaining order
    voices_to_try = list(dict.fromkeys(voices_to_try))
    
    for voice in voices_to_try:
        try:
            print(f"🎤 Trying voice: {voice}")
            
            # Create the communicate object to generate speech
            communicate = edge_tts.Communicate(
                text, 
                voice,
                rate='+20%',
                pitch='-3Hz'
            )
            
            await communicate.save(file_path)
            
            # Verify the file was created and has content
            if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                print(f"✅ Audio generated successfully with {voice}")
                return True
            else:
                print(f"⚠️  Audio file empty with {voice}, trying next...")
                
        except Exception as e:
            print(f"❌ Failed with {voice}: {e}")
            continue
    
    # If we get here, all voices failed
    print("❌ All voice options failed")
    return False

# Function to manage Text-to-Speech (TTS) functionality
def TTS(Text, func=lambda r=None: True):
    mixer_initialized = False
    
    try:
        # Validate input
        if not Text or not str(Text).strip():
            print("❌ Error: Empty text provided")
            return False
        
        # Generate the audio file
        print("🔄 Generating audio...")
        success = asyncio.run(TextToAudioFile(Text))
        
        if not success:
            print("❌ Failed to generate audio file")
            return False
        
        # Check if file exists before trying to play
        if not os.path.exists(r"Data\speech.mp3"):
            print("❌ Audio file not found after generation")
            return False
        
        print("🎵 Initializing audio player...")
        
        # Initialize pygame mixer with specific parameters
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            mixer_initialized = True
        except Exception as e:
            print(f"❌ Failed to initialize mixer: {e}")
            return False
        
        # Load and play the audio
        try:
            pygame.mixer.music.load(r"Data\speech.mp3")
            pygame.mixer.music.play()
            print("▶️  Playing audio...")
        except Exception as e:
            print(f"❌ Failed to play audio: {e}")
            return False
        
        # Loop until the audio is done playing or the function stops
        while pygame.mixer.music.get_busy():
            if func() == False:
                print("⏹️  Playback stopped by function")
                break
            pygame.time.Clock().tick(10)
        
        print("✅ Playback completed")
        return True
        
    except FileNotFoundError:
        print("❌ Audio file not found")
        return False
        
    except pygame.error as e:
        print(f"❌ Pygame error: {e}")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error in TTS: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        try:
            # Call the provided function with False to signal the end of TTS
            func(False)
            
            # Stop and quit mixer only if it was initialized
            if mixer_initialized:
                try:
                    if pygame.mixer.get_init() is not None:
                        if pygame.mixer.music.get_busy():
                            pygame.mixer.music.stop()
                        pygame.mixer.quit()
                except:
                    pass
                
        except Exception as e:
            print(f"⚠️  Error in cleanup: {e}")

# Function to manage Text-to-Speech with additional responses for long text
def TextToSpeech(Text, func=lambda r=None: True):
    if not Text or not str(Text).strip():
        print("❌ No text provided for TTS")
        return False
    
    Data = str(Text).split(".")
    
    # List of predefined responses for cases where the text is too long
    responses = [
        "The rest of the result has been printed to the chat screen, kindly check it out sir.",
        "The rest of the text is now on the chat screen, sir, please check it.",
        "You can see the rest of the text on the chat screen, sir.",
        "The remaining part of the text is now on the chat screen, sir.",
        "Sir, you'll find more text on the chat screen for you to see.",
        "The rest of the answer is now on the chat screen, sir.",
        "Sir, please look at the chat screen, the rest of the answer is there.",
        "You'll find the complete answer on the chat screen, sir.",
        "The next part of the text is on the chat screen, sir.",
        "Sir, please check the chat screen for more information.",
    ]
    
    # If the text is very long, add a response message
    if len(Data) > 4 and len(Text) >= 250:
        first_sentences = ". ".join([s.strip() for s in Data[0:2] if s.strip()])
        if first_sentences:
            first_sentences += ". " + random.choice(responses)
            return TTS(first_sentences, func)
    
    return TTS(Text, func)

# Function to test internet connectivity
async def test_connection():
    print("🌐 Testing edge-tts connection...")
    try:
        voices = await edge_tts.list_voices()
        print(f"✅ Connection successful! Found {len(voices)} voices")
        return True
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🤖 JARVIS TTS System - Enhanced Version")
    print("=" * 60)
    
    # Test connection first
    try:
        connection_ok = asyncio.run(test_connection())
        if not connection_ok:
            print("\n⚠️  Warning: Could not connect to edge-tts service.")
            print("Please check your internet connection and try again.")
            response = input("\nDo you want to continue anyway? (y/n): ")
            if response.lower() != 'y':
                sys.exit(0)
    except Exception as e:
        print(f"⚠️  Could not test connection: {e}")
    
    print("\n💡 Commands: Type 'exit', 'quit', or 'bye' to exit")
    print("=" * 60)
    
    try:
        while True:
            user_input = input("\n📝 Enter the text: ").strip()
            
            if not user_input:
                print("⚠️  No text entered. Please try again.")
                continue
            
            # Exit commands
            if user_input.lower() in ['exit', 'quit', 'bye']:
                print("\n👋 Exiting Jarvis TTS gracefully. Goodbye, sir.")
                break
            
            print(f"\n🔊 Speaking: {user_input}")
            print("-" * 60)
            success = TextToSpeech(user_input)
            print("-" * 60)
            
            if success:
                print("✅ Speech completed successfully")
            else:
                print("❌ Speech failed - Please check the errors above")
                
    except KeyboardInterrupt:
        print("\n\n👋 Exiting Jarvis TTS gracefully. Goodbye, sir.")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()