from .main import extract_slides, cli_args
import numpy as np

def trigger():
    options = cli_args()
    #print("Got here")
    #print(options.diff,options.skip)
    extract_slides(options.path, float(options.diff), int(options.skip),np.array(list(options.coor)),options.url)
