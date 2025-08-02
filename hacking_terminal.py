import os
import sys
import msvcrt
from colorama import Fore, Style
from scan import scan
from ports import portscan

# ========= Hacking Terminal =========
def loadHackingTerminal():

    # initialise colour mapping
    colour_map = {
        'red': Fore.RED,
        'orange': Fore.LIGHTRED_EX,
        'yellow': Fore.YELLOW,
        'green': Fore.GREEN,
        'blue': Fore.BLUE,
        'purple': Fore.MAGENTA,
        'pink': Fore.LIGHTMAGENTA_EX,
        'white': Fore.WHITE,
        'black': Fore.BLACK,
        'grey': Fore.LIGHTBLACK_EX,
        'default': Style.RESET_ALL
    }
    # use mutable dict to allow wrapper access to current colour
    colour_state = {'code': Style.RESET_ALL}

    class ColourWriter:
        def __init__(self, orig):
            self.orig = orig
        def write(self, text):
            # prefix and reset to ensure all text is coloured
            self.orig.write(colour_state['code'] + text + Style.RESET_ALL)
        def flush(self):
            self.orig.flush()
        def isatty(self):
            return getattr(self.orig, 'isatty', lambda: False)()

    # wrap stdout and stderr
    sys.stdout = ColourWriter(sys.stdout)
    sys.stderr = ColourWriter(sys.stderr)

    def coloured_input(prompt):
        # write prompt & flush so it actually appears
        sys.stdout.write(colour_state['code'] + prompt)
        sys.stdout.flush()

        buffer = ''
        while True:
            ch = msvcrt.getwch()  # gets a str
            if ch == '\r':  # Enter
                sys.stdout.write('\n')
                sys.stdout.flush()
                break

            elif ch == '\x08':  # Backspace
                if buffer:
                    buffer = buffer[:-1]
                    # move cursor back, overwrite with space, move back
                    sys.stdout.write('\b \b')
                    sys.stdout.flush()

            else:
                buffer += ch
                # echo the character in the current colour, then flush
                sys.stdout.write(colour_state['code'] + ch)
                sys.stdout.flush()

        return buffer.strip()

    def ensure_home():
        home = os.path.join(
            os.environ.get('USERPROFILE', os.path.expanduser('~')),
            'hacking-terminal'
        )
        os.makedirs(home, exist_ok=True)
        return home

    os.system('cls' if os.name == 'nt' else 'clear')
    home = ensure_home()
    cwd = home

    while True:
        # build Windows-style prompt with backslashes only
        rel = os.path.relpath(cwd, home)
        if rel == '.':
            display = "~\\"
        else:
            display = "~\\" + rel.replace("/", "\\") + "\\"
        # get coloured input including echo
        try:
            line = coloured_input(f"{display}> ")
        except (EOFError, KeyboardInterrupt):
            sys.stdout.write('\n')
            break

        if not line:
            continue

        parts = line.split(None, 1)
        cmd = parts[0].lower()

        # colour command
        if cmd in ('colour', 'color'):
            if len(parts) < 2:
                sys.stdout.write("Usage: colour <colorname>\n")
            else:
                choice = parts[1].strip().lower()
                if choice in colour_map:
                    colour_state['code'] = colour_map[choice]
                else:
                    sys.stdout.write(f"Unknown colour '{choice}'. Available: {', '.join(colour_map.keys())}\n")
            continue

        # exit or quit
        if cmd in ('exit', 'quit'):
            # === RESET terminal state after exit ===
            sys.stdout = sys.__stdout__
            sys.stderr = sys.__stderr__
            colour_state['code'] = Style.RESET_ALL
            print(Style.RESET_ALL, end='')  # ensure it visually resets the terminal
            break

        # cd command
        if cmd == 'cd':
            target = parts[1] if len(parts) > 1 else ''
            if target in ('', '~', '~/'):
                cwd = home
            else:
                if target.startswith('~/') or target.startswith('~\\'):
                    path = os.path.join(home, target[2:].lstrip("\\/"))
                else:
                    path = os.path.join(cwd, target)
                real = os.path.abspath(path)
                if os.path.isdir(real) and real.startswith(home):
                    cwd = real
                else:
                    sys.stdout.write(f"cd: no such file or directory: {target}\n")
            continue

        # mkdir command
        if cmd == 'mkdir':
            if len(parts) < 2 or not parts[1].strip():
                sys.stdout.write("mkdir: missing operand\n")
                continue
            target = parts[1].strip()
            if target.startswith('~/') or target.startswith('~\\'):
                path = os.path.join(home, target[2:].lstrip("\\/"))
            else:
                path = os.path.join(cwd, target)
            try:
                os.makedirs(path)
            except FileExistsError:
                sys.stdout.write(f"mkdir: cannot create directory '{target}': File exists\n")
            except Exception as e:
                sys.stdout.write(f"mkdir: cannot create directory '{target}': {e}\n")
            continue

        # scan command
        if cmd == 'scan':
            if len(parts) < 2:
                sys.stdout.write("Usage: scan <code>\n")
                continue
            code = parts[1].strip()
            result = scan(code)
            if result:
                ip, name = result
                sys.stdout.write(f"🎉 Success! {ip} → {name}!\n")
            else:
                sys.stdout.write(f"😅 '{code}' was not found!\n")
            continue

        # portscan command
        if cmd == 'portscan':
            if len(parts) < 2:
                sys.stdout.write("Usage: portscan <ip>\n")
                continue
            theIP = parts[1].strip()
            portscan(theIP)
            continue

        # unknown command
        sys.stdout.write(f"{cmd}: command not found\n")