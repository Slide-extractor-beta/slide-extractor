import optparse #to get cli arguments
import os
import sys
import cv2
import json
from cv2 import CAP_PROP_FRAME_COUNT
import numpy as np
import pafy
from PIL import Image, ImageOps
from statistics import mean
import ntpath
from tqdm import tqdm

def cli_args():

    parser = optparse.OptionParser()
    parser.add_option("-p", "--path", dest="path", help="Path of the video")
    parser.add_option("-u", "--url", dest="url", help="Url of the video youtube video", default="")
    parser.add_option("-s", "--skip", dest="skip", help="Skip seconds for the video. Default is 1 sec",default=1)
    parser.add_option("-d", "--diff", dest="diff", help="""Threshold Difference level with previous slide beyond which
                      the current slide gets captured. Default value id 0.008""",default=0.008)
    parser.add_option("-c", "--coor", dest="coor", help="""cordinates you want to capture, diagonally opposite start and end cords""", default=str([[0,0],[sys.maxsize,sys.maxsize]]))

    (options, arguments) = parser.parse_args()
    if not options.path and not options.url:
        parser.error("[-] please specify the video path use --help for help")

    try:
        type_check = json.loads(options.coor)
        type_check = [[int(value) for value in row] for row in type_check]
        type_check = np.array(type_check)
        if type_check.shape != (2,2):
            parser.error("[-] coordinates need to be a list of list of shape 2x2, diagonally opposite start and end cords --help for help")
        elif np.any(type_check<0):
            parser.error("[-] coordinates need to be positive values --help for help")
        options.coor = type_check
    except json.JSONDecodeError as e:
        parser.error("[-] coordinates need to be a list of list of shape 2x2, diagonally opposite start and end cords --help for help")


    # except Exception:
    #     parser.error("[-] coordinates need to be a list of list of coordinates --help for help")
    return options

def rgb2gray(rgb):

    r, g, b = rgb[:,:,0], rgb[:,:,1], rgb[:,:,2]
    gray = 0.2989 * r + 0.5870 * g + 0.1140 * b

    return gray

def arrange_coords(coor,frame_shape):
    if coor[0][0]>coor[1][0]:
        coor[0],coor[1] = coor[1],coor[0]
    coor[1] = [min(coor[1][0],frame_shape[0]),min(coor[1][1],frame_shape[1])]
    if coor[0][0]>frame_shape[0] or coor[0][1]>frame_shape[1]:
        raise Exception
    return coor


class extract_slides:
    def __init__(self, path, confidence, skip, coor, url):
        self.path = path
        self.destination = os.getcwd()
        self.pdf_name = "slides"
        if self.path:
            self.destination = os.path.dirname(path)
            self.pdf_name = (self.path_leaf(self.path)).split('.')[0]
        if not self.path:
            video = pafy.new(url)
            best = video.getbest(preftype="mp4")
            self.path = best.url

        self.conf = confidence
        self.skip = skip
        self.first_img = 0
        self.images = []
        self.coor = coor

        self.processVideo()
        

    def path_leaf(self, path):
        head, tail = ntpath.split(path)
        return tail or ntpath.basename(head)

    def processVideo(self):  # ,path,confidence=0.02,skip = 10
        cam = cv2.VideoCapture(self.path)
        fps = cam.get(cv2.CAP_PROP_FPS)
        total_frame_count = int(cam.get(cv2.CAP_PROP_FRAME_COUNT))
        length = total_frame_count / fps
        # pbar = tqdm(total = 100)
        currentframe = 0
        ret, frame = cam.read()
        prev = np.zeros(frame.shape)
        print("Frame shape", frame.shape)
        self.coor = arrange_coords(self.coor,frame.shape)
        print("Finding difference is frame coords: ",self.coor)
        # images = []
        first = True

        diff = 41
        slide = 1
        count = 0
        with tqdm(total=total_frame_count) as pbar:
            while (True):

                # reading from frame
                ret, frame = cam.read()

                if ret:

                    # if first:
                    #     prev = np.zeros(frame.shape)
                    #     print(frame.shape)
                    #frame_to_differentiate = frame[self.coor[0][1]:self.coor[1][1], self.coor[0][0]:self.coor[1][0]] # ROI = frame[y1:y2, x1:x2]
                    currg = rgb2gray(frame)[self.coor[0][0]:self.coor[1][0],self.coor[0][1]:self.coor[1][1]] # ROI = frmae[y1:y2,x1:x2]
                    prevg = rgb2gray(prev)[self.coor[0][0]:self.coor[1][0],self.coor[0][1]:self.coor[1][1]]
                    currgSum = np.sum(np.array(currg))
                    diff3 = abs(np.sum(np.array(currg- prevg)))
                    if currgSum>0:
                        diff3/=currgSum
                    if diff3 > self.conf:

                        if first:
                            self.first_img = Image.fromarray(np.uint8(frame)).convert('RGB')
                            print("\nPlease check the preview image for the area you want to be compared")
                            cv2.imshow('image', currg)
                            cv2.waitKey(0)
                        prev = frame
                        frame = Image.fromarray(np.uint8(frame)).convert('RGB')
                        if not first:
                            self.images.append(frame)
                        else:
                            first = False

                        slide += 1
                    #print(type(fps), type(self.skip))
                    count += fps * self.skip

                    # print(total_frame_count, count)
                    cam.set(cv2.CAP_PROP_POS_FRAMES, count)

                    duration = count / fps
                    pbar.update(fps * self.skip)
                    dicti = {"Found Slide": slide, "Difference Level": diff3}
                    #pbar.set_description_str(desc=f"\rFound {slide} slide   Differnce level: {diff3}")
                    pbar.set_postfix(ordered_dict=dicti)
                    #print(f"\rFound {slide} slide   Differnce level: {diff3}", end='')#, flush=True
                    # print("Processed : ",duration ," secs ",100*duration/length," %", end="\r", flush=True)

                    currentframe += 1

                else:
                    break
        cam.release()
        pbar.close()
        cv2.destroyAllWindows()

        self.save_pdf()

    def save_pdf(self):
        if self.first_img == 0:
            print("No slides found, nothing to save")
        else:
            self.first_img.save(os.path.join(self.destination,f"{self.pdf_name}.pdf"), save_all=True, append_images=list(self.images))
