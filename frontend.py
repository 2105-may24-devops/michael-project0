from typing import Generator
from blessed import Terminal
import sys
import os
import json
# import pathlib
from pathlib import Path

from recipe import Recipe

MDDEBUG=False

EXIT_COMMAND="exit"
CONFIG_REL_PATH="rcpconfig.txt"
term = Terminal()

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
    """Generator, returns true upon ending"""
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

def script_mode(script:Path):
    """Handles scripts being input into the program"""
    with script.open("r") as infile:
        for line in infile:
            interpret_command(line)

def console_mode():
    """Handles interactive mode loop"""
    def prompt():
        if RCPFLAG:
            return f"Current Recipe:{term.blue}{rcp_path.name} {term.yellow}$${term.normal}"
        else:
            return f"{term.green}{os.getcwd()} {term.yellow}${term.normal} "
    
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
}
def interpret_command(cmd:str):
    """Parses and interprets file-explorer mode commands, can enter recipe mode when open command is called"""
    
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
        open_recipe(next(token))
    else: 
        print(f"{term.red}Command not recognized. enter '{term.normal}help{term.red}' to see available commands")

def open_recipe(rcp_path_str:str, name:str=None):
    """ opens a recipe and sets the appropriate flags in storage"""
    #name arg is currently unused, would allow for storing multiple recipes, 
    #which would require a different syntax
    RCPFLAG = True
    rcp_path = cwd_path()/rcp_path_str
    my_recipe = Recipe(rcp_path)

def close_recipe(name = None):
    RCPFLAG=False
    rcp_path=None
    my_recipe = None #TODO: close/save recipe check?

def manip_recipe(cmd:str, rcp:Recipe = my_recipe):
    """handles recipe manipulation, parses commands"""
    #TODO: implement with reflection?
    #no exec()... let's copy kubectl-style commands
    #format is: 
    tokens = tokenzier(cmd)
    root = next(tokenizer)
    if root == "close":
        my_recipe = None
        RCPFLAG = False
        
    return True

# def display_file(filepath):
#     term=Terminal()
#     with term.fullscreen(), \
#         open(filepath, 'r') as file:
#         for line in file:
#             print(line)

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

if __name__ == '__main__' and not MDDEBUG:
    main()
    print()
else:
    tokens = tokenizer("abc 'def ghi' jkl")
    