#!/usr/bin/env python

"""

ТРОНЕТЕ ХОТЬ ЧТО-ТО 




ПОУБИВАЮ

"""

import os
import sys
import time
import math

from pymavlink import mavutil

from tkinter import filedialog
from tkinter import Tk

from PIL import Image

CANVAS_SIZE=16000

class Stitcher:
    _root = Tk()
    _root.withdraw()

    # Use TK to ask and set working directory
    def ask_for_dir(self):
        dir_selected = filedialog.askdirectory()
        self.set_wdir(dir_selected)

    # Function to set working directory
    def set_wdir(self, dir):
        self._wdir = dir
    
    # Find and set main tlog file
    def find_tlog(self):
        for filename in os.listdir(self._wdir):
            if filename.endswith(".tlog"):
                self.set_tlog(os.path.join(self._wdir, filename))
                break
    
    # Set main tlog file
    def set_tlog(self, file):
        self._tlog = file

    # Main solve func
    def solve(self):
        self.find_tlog()

        print("creating canvas...")
        canvas = Image.new("RGBA", (CANVAS_SIZE, CANVAS_SIZE), (0,0,0,0))
        print("finished creating canvas...")

        mlog = mavutil.mavlink_connection(self._tlog)
        data = []
        i = 0
        while True:
            m = mlog.recv_match(type=["CAMERA_FEEDBACK"]) 
            if m is None:
                break
            
            data.append(m.to_dict())
        
        dx, dy = 0,0
        for i in range(len(data)):
            target_photo_path = None
            idata = data[i]
            photo_id = '{0:03d}'.format(idata["img_idx"])

            """
            ОСОБЕННО ТУТ НИЧЕГО НЕ ТРОГАТЬ
            """

            lat = idata["lat"]//75
            lng = idata["lng"]//75
            if idata["img_idx"] == 1:
                dy,dx = abs(CANVAS_SIZE//2 - lat), abs(CANVAS_SIZE//10 - lng)
                print("dx, dy: ", dx, dy)
            py, px = lat - dy, lng - dx

            #if not (photo_id == "055" or photo_id == "056" or photo_id == "057"):
            #    continue

            for filename in os.listdir(self._wdir):
                if filename.endswith(photo_id + ".JPG"):
                    target_photo_path = os.path.join(self._wdir, filename)
                    break
            
            if target_photo_path == None:
                print("skipping photo")
                continue
            
            target_photo = Image.open(target_photo_path).convert("RGBA").rotate(idata["yaw"]-180, expand=1).resize((600, 450), Image.ANTIALIAS)
            
            print("id: ", photo_id)
            print("px, py: ", px, py)

        
            print("pasting image #{}".format(photo_id))
            canvas.paste(target_photo, (px, py), target_photo)

        canvas.show()

algo = Stitcher()
algo.ask_for_dir()
algo.solve() 
