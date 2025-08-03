# N0vaTools


import os
import sys
import time
import subprocess
import json
from colorama import init, Fore, Style
import msvcrt
from java_installer import install_java
from hacking_terminal import loadHackingTerminal
from auto_updater import auto_update
init()

def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')

def input_password(prompt="Please enter the password: "):
    print(prompt, end='', flush=True)
    password = ""
    while True:
        char = msvcrt.getch()
        if char in [b'\r', b'\n']:  # Enter key
            print('')
            break
        elif char == b'\x08':  # Backspace
            if len(password) > 0:
                password = password[:-1]
                print('\b \b', end='', flush=True)
        elif char == b'\x03':  # Ctrl+C
            raise KeyboardInterrupt
        else:
            password += char.decode('utf-8')
            print('*', end='', flush=True)
    return password

def print_main():
    clear_terminal()
    print(Fore.GREEN + r""" _   _  ___            _____           _     
| \ | |/ _ \__   ____ |_   _|__   ___ | |___ 
|  \| | | | \ \ / / _` || |/ _ \ / _ \| / __|
| |\  | |_| |\ V / (_| || | (_) | (_) | \__ \
|_| \_|\___/  \_/ \__,_||_|\___/ \___/|_|___/
    """ + Style.RESET_ALL)

def arrow_menu(options):
    # Hide the cursor
    sys.stdout.write("\x1b[?25l")
    sys.stdout.flush()

    # Print the header and the initial menu
    print_main()
    for i, option in enumerate(options):
        prefix = "➤ " if i == 0 else "  "
        colour = Fore.YELLOW if i == 0 else Fore.WHITE
        print(f"{Fore.GREEN if i == 0 else ''}{prefix}{colour}{option}{Style.RESET_ALL}")

    index = 0
    # How many lines we need to move up to overwrite our menu:
    menu_height = len(options)

    try:
        while True:
            key = msvcrt.getch()
            if key == b'\xe0':        # Arrow keys prefix
                key2 = msvcrt.getch()
                if key2 == b'H':       # Up
                    index = (index - 1) % len(options)
                elif key2 == b'P':     # Down
                    index = (index + 1) % len(options)
                else:
                    continue
            elif key == b'\r':        # Enter
                break
            else:
                continue

            # Move cursor up to the first menu line
            sys.stdout.write(f"\x1b[{menu_height}A")
            # Re‑print the menu with the new selection
            for i, option in enumerate(options):
                prefix = "➤ " if i == index else "  "
                colour = Fore.YELLOW if i == index else Fore.WHITE
                sys.stdout.write(f"\r")  # return to start of line
                sys.stdout.write(" " * 80)  # clear old text (assumes max width <80)
                sys.stdout.write("\r")  # back again
                sys.stdout.write(f"{Fore.GREEN if i == index else ''}{prefix}{colour}{option}{Style.RESET_ALL}\n")
            sys.stdout.flush()
    finally:
        # Show the cursor again
        sys.stdout.write("\x1b[?25h")
        sys.stdout.flush()

    return index

# === Program start ===
clear_terminal()
passw = input_password()

if passw == "hack1ng":
    updates = input("Do you want to check for updates? Y/n ")
    if updates.lower() == "y":
        auto_update()
else:
    sys.exit()

# === Main menu ===
while True:
    choice = arrow_menu([
        "Install apps",
        "UEN v1",
        "Hacking Terminal",
        "Quit"
    ])

    if choice == 0:
        sub = arrow_menu(["Install Java 21", "Back"] )
        if sub == 0:
            print_main()
            install_java()

    elif choice == 1:
        print_main()
        print("UEN is coming soon...")
        time.sleep(3)

    elif choice == 2:
        print_main()
        print("Loading Hacking Terminal...")
        time.sleep(2)
        loadHackingTerminal()
        time.sleep(3)

    elif choice == 3:
        print_main()
        print("Closing N0vaTools...")
        time.sleep(2)
        clear_terminal()
        sys.exit()