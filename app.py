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
    my_frontend = Frontend()
    my_frontend.init_settings()
    my_frontend.init_terminal()
    if len(sys.argv) > 1:
        script_path = pathlib.Path(sys.argv[1])
        if script_path.exists():
            my_frontend.script_mode(script_path)
        else: 
            pass
    else:
        my_frontend.console_mode()

if __name__ == "__main__":
    main()