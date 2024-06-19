import requests
import base64
import hashlib
from nacl.utils import random
from colorama import Fore, Style, init
import itertools
import threading
import time
import sys

# Initialize colorama
init(autoreset=True)

# Flag to control printing (set to False for unit tests)
verbose = True

# Function to animate loading
def animate_loading(message, stop_event):
    if not verbose:
        return
    for frame in itertools.cycle(['|', '/', '-', '\\']):
        if stop_event.is_set():
            break
        sys.stdout.write(f'\r{message} {frame}')
        sys.stdout.flush()
        time.sleep(0.1)
    sys.stdout.write('\r')

# Function to print boxed text aligned to the left with specified color
def print_boxed_text(title, text, border_color=Fore.YELLOW, text_color=Fore.YELLOW):
    if not verbose:
        return
    lines = text.split('\n')
    width = max(len(line) for line in lines) + 2
    print(f"{border_color}╔{'═' * width}╗")
    print(f"{border_color}║ {Fore.CYAN}{title.ljust(width - 1)}║")
    print(f"{border_color}╠{'═' * width}╣")
    for line in lines:
        print(f"{border_color}║ {text_color}{line.ljust(width - 2)} {border_color}║")
    print(f"{border_color}╚{'═' * width}╝")

# Function to retrieve challenge details
def get_challenge(path, challenge_id):
    url = f'https://g5qrhxi4ni.execute-api.eu-west-1.amazonaws.com/Prod/{path}/{challenge_id}'
    response = requests.get(url)
    return response.json()

# Function to create a new challenge
def create_challenge(path):
    url = f'https://g5qrhxi4ni.execute-api.eu-west-1.amazonaws.com/Prod/{path}'
    response = requests.post(url)
    return response.json()

# Function to solve the hash challenge
def solve_hash_challenge(challenge_id: str, stop_event):
    challenge = get_challenge("hash", challenge_id)
    message = base64.b64decode(challenge["message"])

    # Find a prefix that makes the hash of (prefix + message) start with two zero bytes
    attempts = 0
    stop_event.set()  # Stop the loading animation when starting attempts
    while True:
        prefix_candidate = random(1)  # Using 16 bytes for prefix
        candidate = prefix_candidate + message
        hash_result = hashlib.blake2b(candidate, digest_size=32).digest()
        attempts += 1
        if attempts % 50 == 0 and verbose:  # Print status every 50 attempts
            print(f"{Fore.YELLOW}⦙ Attempt {attempts}: Trying prefix {prefix_candidate.hex()} -> Hash {hash_result.hex()[:4]}")
        if hash_result[:2] == b"\x00\x00":
            boxed_text = f"Found valid prefix after {attempts} attempts: {prefix_candidate.hex()}"
            print_boxed_text("", boxed_text, border_color=Fore.GREEN, text_color=Fore.GREEN)
            prefix = prefix_candidate
            break

    # Return the solution
    return {'prefix': base64.b64encode(prefix).decode('utf-8')}

# Function to delete the challenge with the solution
def delete_challenge(path, challenge_id, solution):
    url = f'https://g5qrhxi4ni.execute-api.eu-west-1.amazonaws.com/Prod/{path}/{challenge_id}'
    response = requests.delete(url, json=solution)
    return response

# Main function to create and solve a challenge
def create_and_solve_challenge(path):
    stop_event = threading.Event()
    loading_thread = threading.Thread(target=animate_loading, args=("Creating and solving challenge...", stop_event))
    loading_thread.start()

    # Create a challenge
    challenge = create_challenge(path)
    challengeId = challenge['challengeId']
    if verbose:
        print(f"{Fore.CYAN}Created challenge ID: {challengeId}")

    # Solve the challenge
    if path == 'hash':
        solution = solve_hash_challenge(challengeId, stop_event)
    else:
        if verbose:
            print(f"{Fore.RED}Unknown challenge path: {path}")
        stop_event.set()
        loading_thread.join()
        return

    stop_event.set()
    loading_thread.join()

    # Delete the challenge with the solution
    response = delete_challenge(path, challengeId, solution)
    if response.status_code == 200:
        if verbose:
            print(f"{Fore.GREEN}✓ Challenge {challengeId} solved and successfully deleted.")
    else:
        if verbose:
            print(f"{Fore.RED}Failed to solve challenge {challengeId}. Status code: {response.status_code}")
            print(f"Response: {response.json()}")

if __name__ == "__main__":
    # Set verbose to True when running as a script
    verbose = True
    # Create and solve a hash challenge
    create_and_solve_challenge('hash')
