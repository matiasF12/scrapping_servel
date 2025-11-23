import sys
from datetime import datetime



def prepare_sys_argv_for_interactive():
    """
    Prepares sys.argv for interactive environments.

    In interactive environments (e.g., VS Code interactive window), sys.argv
    is often empty or contains different information than when running a script.
    This function sets sys.argv to [''] if running interactively.

    This function should be called at the beginning of your script if you need
    to ensure sys.argv is consistent across interactive and script execution.
    """
    if hasattr(sys, 'ps1'):
        # Running in an interactive environment
        sys.argv = ['']
    else:
        # Running as a normal script
        pass