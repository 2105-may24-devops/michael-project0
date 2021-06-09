import sys
import pathlib
from frontend import Frontend

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
    args = sys.argv[1:].copy()
    bless = True
    if ("-b" in args):
        bless = False
        args.remove("-b")

    my_frontend = Frontend()
    my_frontend.init_settings()
    my_frontend.init_terminal(bless)

    if len(args) > 0:
        script_path = pathlib.Path(args[0])
        if script_path.exists():
            my_frontend.script_mode(script_path)
        else: 
            my_frontend.interpret_command(" ".join(args))
    else:
        my_frontend.console_mode()

if __name__ == "__main__":
    main()