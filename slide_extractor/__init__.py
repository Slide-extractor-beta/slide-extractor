from main import extract_slides, cli_args

def trigger():
    options = cli_args()
    print("Got here")
    print(options.diff,options.skip)
    extract_slides(options.path, float(options.diff), int(options.skip))
