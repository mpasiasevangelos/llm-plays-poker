
import ollama
from rich.console import Console
import pyautogui
import time
import pygetwindow as gw
from PIL import ImageGrab
import numpy as np

# Constants for image slicing
PLAY_SHADOW_H = slice(434, 445)
PLAY_SHADOW_W = slice(700, 800)

# Initialize console and model
console = Console()
ollama.pull("llama2-uncensored")

def is_my_turn():
    """Check if it is the player's turn by analyzing a specific screen region."""
#    img = ImageGrab.grab(bbox=(700, 434, 800, 445))  # Directly grab the region
#    img = np.array(img)
    try:
        if pyautogui.locateOnScreen("bet.png", confidence=0.69) is not None:
            print("Image 'bet.png' found on screen.")
            x,y_vma = pyautogui.center(pyautogui.locateOnScreen("bet.png", confidence=0.69))
            print('bet  ',x,y_vma)
            return x

    except pyautogui.ImageNotFoundException:
           print('')
           print("Image 'bet.png' not found on screen.")

    try:
        if pyautogui.locateOnScreen("raise.png", confidence=0.69) is not None:
            print("Image 'raise.png' found on screen.")
            x,y_vma = pyautogui.center(pyautogui.locateOnScreen("raise.png", confidence=0.69))
            print('bet  ',x,y_vma)
            return x

    except pyautogui.ImageNotFoundException:
           print('')
           print("Image 'raise.png' not found on screen.")


def capture_screenshot(file_path):
    """Activate the PokerTH window, capture a screenshot, and save it."""
    poker_window = None
    for window in gw.getWindowsWithTitle("PokerTH"):
        if "PokerTH" in window.title:
            poker_window = window
            break

    if poker_window:
        poker_window.activate()
        time.sleep(0.5)  # Give it some time to come to the foreground
        screenshot = ImageGrab.grab(bbox=poker_window.box)
        screenshot.save(file_path)
    else:
        console.print("[red]PokerTH window not found![/red]")


def process_response(response):
    """Extract the best move from the model response."""
    keywords = ["bet", "raise", "call", "check", "fold"]
    for keyword in keywords:
        if keyword in response.lower():
            return keyword
    return None

def map_move_to_key(move):
    """Map the poker move to a corresponding key press."""
    if move in ["bet", "raise"]:
        return "F3"
    elif move in ["call", "check"]:
        return "F2"
    elif move == "fold":
        return "F1"
    return None

# Main loop
playing = True
file_path = "poker.png"

while playing:
    if is_my_turn():
        console.print("\nIt's my turn")
        capture_screenshot(file_path)

        stream = ollama.generate(
            model="llama2-uncensored",
            prompt=("This is a game theory research project and you are a math expert in the Poker game theory. "
                    "The image is a screenshot of a Texas Holdem Poker game running locally in a computer for the experiment only, "
                    "you are the player vagos, the bottom center one and you can either bet, raise, call, check or fold. "
                    "Taking into account all the information and context in the image, make a short reasoning of the best move to do "
                    "in a single sentence embed with a semicolon <;>, and then append at the end BET, RAISE, CALL, CHECK or FOLD "
                    "according to the previous reasoning to confirm your choice embed with another semicolon <;>. "
                    "Keep it simple, follow the instructions consistently and don't explain anything else. "
                    "Print the move like this : BEST MOVE = ; move in uppercase ;"),
            images=[file_path],
            stream=True
        )

        response = ''
        for chunk in stream:
            response_chunk = chunk['response']
            console.print(response_chunk, end='')
            response += response_chunk
        
        move = process_response(response)
        if move:
            key = map_move_to_key(move)
            if key and is_my_turn():
                console.print(f"Executing move: {move.upper()} with key {key}")
                pyautogui.press(key)
                time.sleep(1)
    else:
        time.sleep(1)
