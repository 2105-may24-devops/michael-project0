#standard library imports
from typing import Generator
import sys
import os
from pathlib import Path

#module imports
from recipe import Recipe

#handling dependencies
COLOR_DICT={
    "WARN":"",
    "NORM":"",
    "PROMPT":"",
    "OS_PATH":"",
    "RCP_PATH":""
}

try:
    from blessed import Terminal
    term = Terminal()
    COLOR_DICT["WARN"] = term.red
    COLOR_DICT["NORM"] = term.normal
    COLOR_DICT["PROMPT"] = term.yellow
    COLOR_DICT["OS_PATH"] = term.green
    COLOR_DICT["RCP_PATH"] = term.blue
except ModuleNotFoundError:
    print("blessed not found")

EXIT_COMMAND="exit"
CONFIG_REL_PATH="rcpconfig.txt"


my_recipe:Recipe
rcp_path:Path
RCPFLAG = False

def cwd_path():
    """Returns a Path object of the current working directory."""
    return Path(os.getcwd())

def init_settings():
    """Searches for a settings file at `./rcpconfig.txt`
    Currently does nothing with that file.
    """
    config_path = cwd_path()/CONFIG_REL_PATH
    if config_path.exists():
        print( f"Found a settings file at {str(config_path)}!" )

def tokenizer(line:str):
    """Generator, returns None upon ending"""
    WHITESPACE=0
    TOKEN=1
    DQUOTE=2
    SQUOTE=3
    state = WHITESPACE
    reg0 = 0
    for i in range(len(line)):
        char = line[i]
        if state == WHITESPACE:
            if char == "\"":
                state = DQUOTE
                reg0 = i+1
            elif char == "'":
                state = SQUOTE
                reg0 = i+1
            elif not char.isspace():
                state = TOKEN
                reg0 = i
        elif state == TOKEN:
            if char.isspace():
                state = WHITESPACE
                yield line[reg0:i+1]
        elif state == SQUOTE:
            if char == "'":
                state = WHITESPACE
                yield line[reg0:i]
        elif state == DQUOTE:
            if char == "\"":
                state = WHITESPACE
                yield line[reg0:i]
    yield line[reg0:]
    return None

def script_mode(script:Path):
    """Handles scripts being input into the program"""
    with script.open("r") as infile:
        for line in infile:
            interpret_command(line)

def console_mode():
    """Handles interactive mode loop"""
    def prompt():
        if RCPFLAG:
            return f"Current Recipe:{COLOR_DICT['RCP_PATH']}{rcp_path.name} {COLOR_DICT['PROMPT']}#{COLOR_DICT['NORM']}"
        else:
            return f"{COLOR_DICT['RCP_PATH']}{os.getcwd()} {COLOR_DICT['PROMPT']}${COLOR_DICT['NORM']} "
    
    goon = True
    imp = input(prompt())
    #default mode is file-exploring mode
    while goon:
        if imp.startswith(EXIT_COMMAND):
            goon=False
        else: 
            interpret_command(imp)
            imp = input(prompt())

COMMAND_DICT={
    "help":"prints all the available commands",
    "cd":"change current directory",
    "ls":"list the contents of the current directory",
    "pwd":"prints the current directory",
    "echo":"miscellaneous output function",
    "open":"change current directory",
    "exit":"exits the program"
}
    
def interpret_command(cmd:str):
    """Parses and interprets file-explorer mode commands, can enter recipe mode when open command is called"""
    if cmd == "":
        return

    #allows scripts to access recipe mode commands
    if RCPFLAG:
        manip_recipe(cmd)
        return
    
    tokens = tokenizer(cmd)
    root_cmd = next(tokens)
    if(root_cmd == "cd"):
        os.chdir(Path(next(tokens)))
    elif(root_cmd == "ls"):
        #TODO: dumb ls, only does current dir
        # print(os.getcwd())
        for child in cwd_path().iterdir():
            child_type = "D" if child.is_dir() else "F"
            print(f"  {child_type} - {child.name}")
    elif(root_cmd == "pwd"):
        print(os.getcwd())
    elif(root_cmd == "echo"):
        print(" ".join(list(tokens)))
    elif(root_cmd == "help"):
        arg = next(tokens)
        if arg in COMMAND_DICT:
            print(f"\t{arg}\t{COMMAND_DICT[arg]}")
        else:
            for cmd_name, helptxt in COMMAND_DICT.items:
                print(f"\t{cmd_name}\t{helptxt}")
    elif(root_cmd == "open"):
        open_recipe(next(tokens))
    else: 
        print(f"{COLOR_DICT['WARN']}Command not recognized. enter '{COLOR_DICT['NORM']}help{COLOR_DICT['WARN']}' to see available commands")

def open_recipe(rcp_path_str:str, name:str=None):
    """ opens a recipe and sets the appropriate flags in storage"""
    #name arg is currently unused, would allow for storing multiple recipes, 
    #which would require a different syntax
    RCPFLAG = True
    rcp_path = cwd_path()/rcp_path_str
    my_recipe = Recipe(rcp_path)

def close_recipe(name = None):
    if my_recipe.modified:
        yes = input(f"{COLOR_DICT['WARN']}Your recipe has unsaved changes. Close anyways? (must type '{COLOR_DICT['NORM']}yes{COLOR_DICT['WARN']}')")
        if yes != "yes":
            return
    my_recipe = None
    RCPFLAG=False
    rcp_path=None

RCP_COMMANDS={
    "help":"prints all available commands",
    "display":"prints all available commands",
    "close":"closes the recipe mode, returning to file explorer"
}

def manip_recipe(cmd:str, rcp:Recipe = my_recipe):
    """handles recipe manipulation, parses commands"""
    #let's copy kubectl-style commands
    #format is: 
    tokens = tokenzier(cmd)
    root = next(tokenizer)

    if root == "help":
        arg = next(tokens)
        if arg in RCP_COMMANDS:
            print(f"\t{arg}\t{RCP_COMMANDS[arg]}")
        else:
            for cmd_name, helptxt in RCP_COMMANDS.items:
                print(f"\t{cmd_name}\t{helptxt}")
    elif root == "display":
        #TODO: may need to change cursor
        with term.fullscreen():
            print(str(rcp))
    elif root == "save":
        target = next(tokens)
        if target is not None:
            my_recipe.write_json(target)
        else:
            my_recipe.write_json(rcp_path)
    elif root == "close":
        close_recipe()
    else:
        print(f"{COLOR_DICT['WARN']}Command not recognized. enter '{COLOR_DICT['NORM']}help{COLOR_DICT['WARN']}' to see available commands")
   
    return True

# main function commented just for exercise
def main():
    """
    env vars (home, mode/state) (local settings file?)
    file navigation mode (cd ls pwd)
    help
    recipe editing mode
        create recipe
        edit steps
        scale recipe
        optional feature: tab autocomplete?
        stretch feature: treeNode-based recipes
    """
    init_settings()
    if len(sys.argv) > 1:
        script_path = Path(sys.argv[1])
        if script_path.exists():
            script_mode(script_path)
        else: 
            pass
    else:
        console_mode()
