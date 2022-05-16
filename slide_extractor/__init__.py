from .main import extract_slides, cli_args

def trigger():
    options = cli_args()
    # print(options.diff,options.skip)
    extract_slides(options.path, int(options.diff), int(options.skip))