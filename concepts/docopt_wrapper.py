def parse_argv(program_name: str, docstring: str):
    argv = __import__("sys").argv
    real_docstring = docstring.strip("\n").replace(program_name, argv[0])
    docopt = __import__("docopt")
    docopt.DocoptExit = lambda: exit(real_docstring)
    args = docopt.docopt(docstring, argv[1:], help=False)
    if args["--help"] | args["-h"]:
        print(real_docstring)
        exit(0)
    return args


docstring = """
Usage:
    xyz.py hello there --abcd
    xyz.py -h | --help

Examples:
    xyz.py hello there
"""
parse_argv("xyz.py", docstring)
