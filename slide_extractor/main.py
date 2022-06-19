import optparse #to get cli arguments
import os
import cv2
from cv2 import CAP_PROP_FRAME_COUNT
import numpy as np
from PIL import Image, ImageOps
from statistics import mean
import ntpath
from tqdm import tqdm

def cli_args():

    parser = optparse.OptionParser()
    parser.add_option("-p", "--path", dest="path", help="Path of the video")
    parser.add_option("-s", "--skip", dest="skip", help="Skip seconds for the video. Default is 1 sec",default=1)
    parser.add_option("-d", "--diff", dest="diff", help="""Threshold Difference level with previous slide beyond which
                      the current slide gets captured. Default value id 0.008""",default=0.008)

    (options, arguments) = parser.parse_args()
    if not options.path:
        parser.error("[-] please specify the video path use --help for help")
    return options

def rgb2gray(rgb):

    r, g, b = rgb[:,:,0], rgb[:,:,1], rgb[:,:,2]
    gray = 0.2989 * r + 0.5870 * g + 0.1140 * b

    return gray


class extract_slides:
    def __init__(self, path, confidence, skip):
        self.path = path
        self.conf = confidence
        self.skip = skip
        self.first_img = 0
        self.images = []

        self.pdf_name = (self.path_leaf(self.path)).split('.')[0]
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
        prev = 0
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

                    if first:
                        prev = np.zeros(frame.shape)
                    currg = rgb2gray(frame)
                    prevg = rgb2gray(prev)
                    currgSum = np.sum(np.array(currg))
                    diff3 = abs(np.sum(np.array(currg- prevg)))
                    if currgSum>0:
                        diff3/=currgSum
                    if diff3 > self.conf:

                        if first:
                            # self.first_img = frame
                            self.first_img = Image.fromarray(np.uint8(frame)).convert('RGB')
                        prev = frame
                        frame = Image.fromarray(np.uint8(frame)).convert('RGB')
                        # print(type(frame))
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
            self.first_img.save(f'./{self.pdf_name}.pdf', save_all=True, append_images=list(self.images))
