import base64
import requests
from nacl.secret import SecretBox
from operator import itemgetter
from colorama import Fore, Style, init
import itertools
import threading
import time
import sys

# Initialize colorama
init(autoreset=True)

# Function to animate loading
def animate_loading(message, stop_event):
    loading_symbols = itertools.cycle(['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'])
    while not stop_event.is_set():
        sys.stdout.write(f'\r{message} {next(loading_symbols)}')
        sys.stdout.flush()
        time.sleep(0.1)
    sys.stdout.write('\r')

# Function to print boxed text aligned to the left with specified color
def print_boxed_text(title, text, border_color=Fore.YELLOW, text_color=Fore.YELLOW):
    lines = text.split('\n')
    width = max(len(line) for line in lines) + 2
    print(f"{border_color}╔{'═' * width}╗")
    print(f"{border_color}║ {Fore.CYAN}{title.ljust(width - 1)}║")
    print(f"{border_color}╠{'═' * width}╣")
    for line in lines:
        print(f"{border_color}║ {text_color}{line.ljust(width - 2)}{border_color} ║")
    print(f"{border_color}╚{'═' * width}╝")

# Base URL for the decryption challenge
DECRYPT_API_URL = "https://g5qrhxi4ni.execute-api.eu-west-1.amazonaws.com/Prod/decrypt"

def fetch_decrypt_challenge():
    response = requests.post(DECRYPT_API_URL)
    challenge_data = response.json()
    return itemgetter("challengeId", "key", "ciphertext", "nonce")(challenge_data)

def decode_base64(data):
    return base64.b64decode(data)

def decrypt_data(ciphertext, key, nonce):
    secret_box = SecretBox(key)
    decrypted = secret_box.decrypt(ciphertext, nonce)
    return base64.b64encode(decrypted).decode()

def submit_decrypt_solution(challenge_id, plaintext):
    payload = {"plaintext": plaintext}
    response = requests.delete(f"{DECRYPT_API_URL}/{challenge_id}", json=payload)
    return response.status_code

if __name__ == "__main__":
    # Start loading animation
    stop_event = threading.Event()
    loading_thread = threading.Thread(target=animate_loading, args=("Loading", stop_event))
    loading_thread.start()

    # Fetch challenge details
    challenge_id, encoded_key, encoded_ciphertext, encoded_nonce = fetch_decrypt_challenge()
    
    # Stop loading animation
    stop_event.set()
    loading_thread.join()

    print(f"{Fore.CYAN}Challenge Details:")
    print_boxed_text("Challenge ID", challenge_id)
    print_boxed_text("Key", encoded_key)
    print_boxed_text("Ciphertext", encoded_ciphertext)
    print_boxed_text("Nonce", encoded_nonce)

    time.sleep(2)
    print(f"{Fore.CYAN}\nDecoding the challenge parameters...")
    key = decode_base64(encoded_key)
    nonce = decode_base64(encoded_nonce)
    ciphertext = decode_base64(encoded_ciphertext)

    time.sleep(2)
    print(f"{Fore.CYAN}\nDecrypting the ciphertext...")
    plaintext = decrypt_data(ciphertext, key, nonce)

    time.sleep(2)
    print(f"\n{Fore.GREEN}Successfully decrypted.")
    print_boxed_text("Payload", plaintext, border_color=Fore.GREEN, text_color=Fore.GREEN)

    time.sleep(2)
    print(f"{Fore.CYAN}Submitting the decrypted payload to complete the challenge...")
    status_code = submit_decrypt_solution(challenge_id, plaintext)
    if status_code == 204:
        print(f"{Fore.GREEN}✓ Challenge completed and deleted successfully.")
    else:
        print(f"{Fore.RED}Failed to delete the challenge. Received status code: {status_code}")
