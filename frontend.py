#!/usr/bin/env python3
#standard library imports
from typing import Generator
import sys
import os
from pathlib import Path

#module imports
from recipe import Recipe
from recipe import IngredientAmount

class Frontend:

    BLEST = True
    #handling dependencies
    COLORS={
        "WARN":"",
        "NORM":"",
        "PROMPT":"",
        "OS_PATH":"",
        "RCP_PATH":""
    }
    def init_terminal(self):
        try:
            from blessed import Terminal
            term = Terminal()
            self.COLORS["WARN"] = term.red
            self.COLORS["NORM"] = term.normal
            self.COLORS["PROMPT"] = term.yellow
            self.COLORS["OS_PATH"] = term.green
            self.COLORS["RCP_PATH"] = term.blue
            self.COLORS["ACCENT"] = term.blue
            return True
        except ModuleNotFoundError:
            print("blessed not found")
            self.BLEST=False
            return False

    CONFIG_REL_PATH="rcpconfig.txt"

    my_recipe:Recipe=None
    rcp_path:Path=None
    RCPFLAG = False

    def cwd_path(self):
        """Returns a Path object of the current working directory."""
        return Path(os.getcwd())

    def init_settings(self):
        """Searches for a settings file at `./rcpconfig.txt`
        Currently does nothing with that file.
        """
        config_path = self.cwd_path()/self.CONFIG_REL_PATH
        if config_path.exists():
            print( f"Found a settings file at {str(config_path)}!" )

    def tokenizer(self, line:str):
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

    def script_mode(self, script:Path):
        """Handles scripts being input into the program"""
        with script.open("r") as infile:
            for line in infile:
                self.interpret_command(line)

    def console_mode(self):
        """Handles interactive mode loop"""
        def prompt(self):
            if self.RCPFLAG:
                return f"Current Recipe:{self.COLORS['RCP_PATH']}{self.rcp_path.name} {self.COLORS['PROMPT']}#{self.COLORS['NORM']}"
            else:
                return f"{self.COLORS['RCP_PATH']}{os.getcwd()} {self.COLORS['PROMPT']}${self.COLORS['NORM']} "
        #whether or not the loop should go on
        goon = True
        imp = input(prompt())
        #default mode is file-exploring mode
        while goon:
                goon = self.interpret_command(imp)
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
        
    def interpret_command(self, cmd:str):
        """Parses and interprets file-explorer mode commands, can enter recipe mode when open command is called"""
        COLORS = self.COLORS
        if cmd == "":
            return

        #allows scripts to access recipe mode commands
        if self.RCPFLAG:
            try:
                self.manip_recipe(cmd)
            except TypeError as e:
                if e.__cause__ is None:
                    print(f"{COLORS['WARN']} Expected argument but none was supplied.")
            except ValueError:
                print(f"{COLORS['WARN']} Expected numeric argument but string was given.")
            return
        
        tokens = self.tokenizer(cmd)
        root_cmd = next(tokens)
        # print(f"command was: {repr(root_cmd)}")
        if(root_cmd == "cd"):
            arg = next(tokens)
            if arg is not None:
                cd_path = Path(arg)
                if not cd_path.exists():
                    print(f"{COLORS['WARN']} invalid path")
                os.chdir(cd_path)
            else:
                print(f"{COLORS['WARN']} Arguments expected. No arguments entered.")
        elif(root_cmd == "ls"):
            #TODO: dumb ls, only does current dir
            # print(os.getcwd())
            for child in self.cwd_path().iterdir():
                child_type = "D" if child.is_dir() else "F"
                print(f"  {child_type} - {child.name}")
        elif(root_cmd == "pwd"):
            print(os.getcwd())
        elif(root_cmd == "echo"):
            print(" ".join(list(tokens)[:-1]))
        elif(root_cmd == "help"):
            arg = next(tokens)
            if arg in self.COMMAND_DICT:
                print(f"\t{arg}\t{self.COMMAND_DICT[arg]}")
            else:
                for cmd_name, helptxt in self.COMMAND_DICT.items():
                    print(f"\t{cmd_name}\t{helptxt}")
        elif(root_cmd == "open"):
            self.open_recipe(next(tokens))
            print(self.RCPFLAG)
        elif(root_cmd == "exit"):
            print("Bye!")
            return False
        else: 
            print(f"{COLORS['WARN']}Command not recognized. enter \
                '{COLORS['NORM']}help{COLORS['WARN']}' to see available commands")
        return True

    def open_recipe(self, rcp_path_str:str, name:str=None):
        """ opens a recipe and sets the appropriate flags in storage. 
        Returns false if file failed to open for some reason.
        """
        #name arg is currently unused, would allow for storing multiple recipes, 
        #which would require a different syntax
        if rcp_path_str is not None:
            rcp_path = self.cwd_path()/rcp_path_str
            print(f"Opening {str(rcp_path)}")
            RCPFLAG = True
            my_recipe = Recipe(rcp_path)
            return True
        return False

    def close_recipe(self, name = None):
        """Closes recipe. name parameter is unused"""
        if self.my_recipe is not None and self.my_recipe.modified:
            yes = input(f"{self.COLORS['WARN']}Your recipe has unsaved changes. \
                    Close anyways? (must type '{self.COLORS['NORM']}yes{self.COLORS['WARN']}')")
            if yes != "yes":
                return
        self.my_recipe = None
        self.RCPFLAG=False
        self.rcp_path=None

    RCP_COMMANDS={
        "help":"prints all available commands",
        "display":"prints all available commands",
        "close":"closes the recipe mode, returning to file explorer"
    }

    def manip_recipe(self, cmd:str):
        """handles recipe manipulation, parses commands"""
        #let's copy kubectl-style commands
        #format is: action target *arguments...
        my_recipe = self.my_recipe
        RCP_COMMANDS = self.RCP_COMMANDS
        tokens = self.tokenzier(cmd)
        root = next(tokens)
        if root == "help":
            arg = next(tokens)
            if arg in RCP_COMMANDS:
                print(f"\t{arg}\t{RCP_COMMANDS[arg]}")
            else:
                for cmd_name, helptxt in RCP_COMMANDS.items:
                    print(f"\t{cmd_name}\t{helptxt}")
        elif root == "display":
            #TODO: may need to change cursor on terminal
            if self.BLEST:
                with self.term.fullscreen():
                    print(str(my_recipe))
                    input("press enter to quit")
            else:
                print(str(self.my_recipe))
        elif root == "add":
            what = next(tokens)
            if what == "step":
                my_step = " ".join(list(tokens[:-1]))
                i = len(my_recipe.steps) + 1
                print(f"{self.COLORS['ACCENT']}Added: {self.COLORS['NORM']} Step {i}. {my_step}")
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
                #     print(f"{self.COLORS['WARN']}Invalid unit.")
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
                print(f"{self.COLORS['WARN']} invalid set argument.")
                print(f"Possible arguments for set: ")
                RECIPE_SET_DICT={
                    "title":"set title of the recipe.\t 1 argument",
                    "author":"set the author of the recipe.\t 1 argument",
                    "serves":"number of people served by the recipe.\t 1 numeric argument",
                    "srcurl":"the source url of the recipe.\t 1 argument",
                    "metadata":"custom metadata.\t 2 arguments, key then value"
                }
                for set_cmd, help_txt in RECIPE_SET_DICT.items():
                    print(f"{self.COLORS['ACCENT']}{set_cmd}\t{self.COLORS['NORM']}{help_txt}")
        elif root == "remove":
            what = next(tokens)
            if what == "metadata":
                key = next(tokens)
                my_recipe.cli_remove_metadata(key)
            elif what == "step":
                try:
                    num = int(next(tokens)) - 1
                    my_recipe.cli_remove_step(num)
                except (IndexError, TypeError):
                    print(f"{self.COLORS['WARN']} Invalid index. \
                        There are {len(my_recipe.steps)} steps in the recipe.")
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
                my_recipe.write_json(self.rcp_path)
        elif root == "close":
            self.close_recipe()
        else:
            if root == "metric":
                ingr = next(tokens)
                my_recipe.cli_to_metric(ingr)
            elif root == "scale":
                factor = float(next(tokens))
                my_recipe.cli_scale(factor)
            else:
                print(f"{self.COLORS['WARN']}Command not recognized. enter \
                    '{self.COLORS['NORM']}help{self.COLORS['WARN']}' to see available commands")
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
    my_frontend = Frontend()
    my_frontend.init_settings()
    my_frontend.init_terminal()
    if len(sys.argv) > 1:
        script_path = Path(sys.argv[1])
        if script_path.exists():
            my_frontend.script_mode(script_path)
        else: 
            pass
    else:
        my_frontend.console_mode()

if __name__ == "__main__":
    main()