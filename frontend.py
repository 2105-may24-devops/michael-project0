#!/usr/bin/env python3
#standard library imports
from typing import Generator
import sys
import os
from pathlib import Path

#module imports
from recipe import Recipe
from recipe import IngredientAmount

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
    COLOR_DICT["ACCENT"] = term.blue
except ModuleNotFoundError:
    print("blessed not found")

EXIT_COMMAND="exit"
CONFIG_REL_PATH="rcpconfig.txt"

my_recipe:Recipe=None
rcp_path:Path=None
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
                yield line[reg0:i]
        elif state == SQUOTE:
            if char == "'":
                state = WHITESPACE
                yield line[reg0:i]
        elif state == DQUOTE:
            if char == "\"":
                state = WHITESPACE
                yield line[reg0:i]
    yield line[reg0:]
    yield None

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
    #whether or not the loop should go on
    goon = True
    imp = input(prompt())
    #default mode is file-exploring mode
    while goon:
            goon=interpret_command(imp)
            if goon:
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
        try:
            manip_recipe(cmd)
        except TypeError as e:
            if e.__cause__ is None:
                print(f"{COLOR_DICT['WARN']} Expected argument but none was supplied.")
        except ValueError:
            print(f"{COLOR_DICT['WARN']} Expected numeric argument but string was given.")
        return
    
    tokens = tokenizer(cmd)
    root_cmd = next(tokens)
    # print(f"command was: {repr(root_cmd)}")
    if(root_cmd == "cd"):
        arg = next(tokens)
        if arg is not None:
            cd_path = Path(arg)
            if not cd_path.exists():
                print(f"{COLOR_DICT['WARN']} invalid path")
            os.chdir(cd_path)
        else:
            print(f"{COLOR_DICT['WARN']} Arguments expected. No arguments entered.")
    elif(root_cmd == "ls"):
        #TODO: dumb ls, only does current dir
        # print(os.getcwd())
        for child in cwd_path().iterdir():
            child_type = "D" if child.is_dir() else "F"
            print(f"  {child_type} - {child.name}")
    elif(root_cmd == "pwd"):
        print(os.getcwd())
    elif(root_cmd == "echo"):
        print(" ".join(list(tokens)[:-1]))
    elif(root_cmd == "help"):
        arg = next(tokens)
        if arg in COMMAND_DICT:
            print(f"\t{arg}\t{COMMAND_DICT[arg]}")
        else:
            for cmd_name, helptxt in COMMAND_DICT.items():
                print(f"\t{cmd_name}\t{helptxt}")
    elif(root_cmd == "open"):
        open_recipe(next(tokens))
    elif(root_cmd == "exit"):
        print("Bye!")
        return False
    else:
        print("what?") 
        #print(f"{COLOR_DICT['WARN']}Command not recognized. enter '{COLOR_DICT['NORM']}help{COLOR_DICT['WARN']}' to see available commands")
    return True

def open_recipe(rcp_path_str:str, name:str=None):
    """ opens a recipe and sets the appropriate flags in storage. 
    Returns false if file failed to open for some reason.
    """
    #name arg is currently unused, would allow for storing multiple recipes, 
    #which would require a different syntax
    if rcp_path_str is not None:
        rcp_path = cwd_path()/rcp_path_str
        RCPFLAG = True
        my_recipe = Recipe(rcp_path)
        return True
    return False

def close_recipe(name = None):
    """Closes recipe"""
    if my_recipe is not None and my_recipe.modified:
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

def manip_recipe(cmd:str):
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
        #TODO: may need to change cursor on terminal
        with term.fullscreen():
            print(str(my_recipe))
            input("press enter to quit")
    elif root == "add":
        what = next(tokens)
        if what == "step":
            my_step = " ".join(list(tokens[:-1]))
            i = len(my_recipe.steps) + 1
            print(f"{COLOR_DICT['ACCENT']}Added: {COLOR_DICT['NORM']} Step {i}. {my_step}")
            my_recipe.cli_add_step(my_step)
        elif what == "ingredient":
            munit = IngredientAmount.MASS_CONV
            vunit = IngredientAmount.VOLUME_CONV
            ingr = next(tokens)
            amount = float(next(tokens))
            unit = next(tokens)
            my_recipe.cli_add_ingredient(ingr, amount, unit)
            # if status == False and False:
            #     #not going to be strict about checking units
            #     print(f"{COLOR_DICT['WARN']}Invalid unit.")
            #     print("Valid mass units:")
            #     for mu in munit.keys():
            #         print(f"\t{mu}")
            #     print("Valid volume units:")
            #     for vu in vunit.keys():
            #         print(f"\t{vu}")
    elif root == "set":
        what = next(tokens)
        if what == "title":
            name = next(tokens)
            my_recipe.cli_set_title(name)
        elif what == "author":
            name = next(tokens)
            my_recipe.cli_set_author(name)
        elif what == "serves":
            num = int(next(tokens))
            my_recipe.cli_set_serves(num)
        elif what == "srcurl":
            url = next(tokens)
            my_recipe.cli_set_srcurl(url)
        elif what == "metadata":
            key = next(tokens)
            val = next(tokens)
            my_recipe.cli_custom_metadata(key, val)
        else:
            print(f"{COLOR_DICT['WARN']} invalid set argument.")
            print(f"Possible arguments for set: ")
            RECIPE_SET_DICT={
                "title":"set title of the recipe.\t 1 argument",
                "author":"set the author of the recipe.\t 1 argument",
                "serves":"number of people served by the recipe.\t 1 numeric argument",
                "srcurl":"the source url of the recipe.\t 1 argument",
                "metadata":"custom metadata.\t 2 arguments, key then value"
            }
            for set_cmd, help_txt in RECIPE_SET_DICT.items():
                print(f"{COLOR_DICT['ACCENT']}{set_cmd}\t{COLOR_DICT['NORM']}{help_txt}")
    elif root == "remove":
        what = next(tokens)
        if what == "metadata":
            key = next(tokens)
            my_recipe.cli_remove_metadata(key)
        elif what == "step":
            try:
                num = int(next(tokens)) - 1
                my_recipe.cli_remove_step(num)
            except IndexError, TypeError:
                print(f"{COLOR_DICT['WARN']} Invalid index. There are {len(my_recipe.steps)} steps in the recipe.")
        elif what == "ingredient":
            ingr = next(tokens)
            status = my_recipe.cli_remove_ingredient(ingr)
            if status == False:
                print("No matching ingredient found!")
    elif root == "get":
        what = next(tokens)
        if what == "metadata":
            keys = my_recipe.cli_get_metadata_keys()
        elif what == "step":
            num = int(next(tokens))
            
    elif root == "save":
        target = next(tokens)
        if target is not None:
            my_recipe.write_json(target)
        else:
            my_recipe.write_json(rcp_path)
    elif root == "close":
        close_recipe()
    else:
        if root == "metric":
            ingr = next(tokens)
            my_recipe.cli_to_metric(ingr)
        elif root == "scale":
            factor = float(next(tokens))
            my_recipe.cli_scale(factor)
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

if __name__ == "__main__":
    main()