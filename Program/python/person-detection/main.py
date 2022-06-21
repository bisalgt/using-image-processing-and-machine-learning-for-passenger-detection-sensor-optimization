#!/usr/bin/env python3
import tkinter as tk
from datetime import datetime
from os.path import exists
from tkinter.tix import ExFileSelectBox
from venv import create

import cv2
import yolov5
import numpy as np
from PIL import Image, ImageTk
from soupsieve import select

from app_gui import app_gui
from blob_detector import *
from model_class import model_class
#from model_class import model_class

# --- main ---

global cap, run_camera, global_frame, finish_record, roi_points, roi_img
roi_flag = False
run_camera = False
window_app_run = False
status_text = ""
roi_points = []
model_filename = 'yolov5m.pt'
device = "cuda" # or "cpu"

backSub = cv2.createBackgroundSubtractorKNN()
blob_detector = init_blob_detector()

# create window application
window_app = tk.Tk()
window_app.title("Person Detection")
window_app.geometry = ("1080x400")

canvas_w = 320
canvas_h = 320

# first frame with clear white image and init filter_image
white_img = np.zeros([canvas_w, canvas_h, 3], dtype=np.uint8)
roi_img = white_img.copy()
white_img.fill(255) 
roi_img.fill(0)

default_img = Image.fromarray(white_img)
default_img = ImageTk.PhotoImage(default_img) 

default_img2 = Image.fromarray(white_img)
default_img2 = ImageTk.PhotoImage(default_img2) 
global_frame = white_img

model = model_class(model_filename, device)

if not window_app_run:
    window_app_run = True
    gui = app_gui(
        window_app, 
        default_img, 
        default_img2, 
        canvas_w, 
        canvas_h
        )
    
def play():
    '''
    start stream (run_camera and update_image) 
    and change state of buttons_left
    '''
    global cap, run_camera, finish_record
    
    # Check current selected tab
    select_mode = gui.gui_down.get_select_mode()
    record_status = gui.gui_down.get_record_status()
    finish_record = False

    if (select_mode == 0) & (record_status == 0): # CAMERA

        try:
             cam_no = int(gui.gui_down.get_camera_number()) # webcam : 0, other: 1
        except:
            display_status("Camera Number must be Integer")
            return 0
       
        cap = cv2.VideoCapture(cam_no) 

        # Check if source is accessible
        if not cap.isOpened():  
            cap.release()
            stop()
            return 0

        display_status("Realtime Camera Feed")

    elif (select_mode == 1): # VIDEO
        video_path = gui.gui_down.get_video_path()
        
        if not exists(video_path): 
            display_status("path [ " + video_path + " ] does not exist!")
            stop()
            return 0
        else:
            cap = cv2.VideoCapture(video_path)

        fps = cap.get(cv2.CAP_PROP_FPS)
        
        display_status("Video File Feed")         

    elif (select_mode == 0) & (record_status == 1): # Record Mode
        export_path = gui.gui_down.get_record_export_path()

        video_writer = cv2.VideoWriter(export_path)

        write_video(video_writer)

    else:   # Auto Mode
        return 0

    if not run_camera:
        run_camera = True
        
        button_play['state'] = 'disabled'
        button_stop['state'] = 'normal'
        button_pause['state'] = 'normal'
        button_resume['state'] = 'disabled'
        update_frame()

def stop():
    '''
    stop stream (run_camera) 
    and change state of buttons_left
    '''
    global run_camera, finish_record

    if run_camera:
        run_camera = False
        finish_record = True

        cap.release()

    button_play['state'] = 'normal'
    button_stop['state'] = 'disabled'
    button_pause['state'] = 'disabled'
    button_resume['state'] = 'disabled'
    
    display_status("STOP Frame")

def pause_frame():
    '''
    pause the stream
    and change state of buttons_left
    '''
    button_stop['state'] = 'normal'
    button_pause['state'] = 'disabled'
    button_resume['state'] = 'normal'

    display_status("Pause Frame")

def resume_frame():
    '''
    resume the stream after pause
    and change state of buttons_left
    '''
    button_stop['state'] = 'normal'
    button_pause['state'] = 'normal'
    button_resume['state'] = 'diabled'

    display_status("Resume Frame")
    
def apply_ROI():
    global roi_flag, roi_points
    
    if roi_points:
        roi_flag = True
    else:
        display_status("ROI points not yet specified")
        roi_flag = False
    
def default_roi():
    
    '''
    Set roi points to default
    '''
    
    global roi_points, roi_img
    
    roi_points = [[59, 172],
                  [91, 53],
                  [166, 1],
                  [228, 50],
                  [267, 186],
                  [279, 233],
                  [238, 234],
                  [211, 301],
                  [162, 319],
                  [121, 302],
                  [89, 234],
                  [55, 229]]
    
    # Connect dots and create polygon       
    pts = np.array(roi_points,np.int32)
    roi_img = cv2.fillPoly(roi_img, [pts], (255,255,255))
    
def draw_polygon_roi(frame):
    
    global roi_points
    
    # draw polygon if with the specified points
    if roi_points: # not empty
        
        pts = np.array(roi_points, np.int32)
        frame_roi = cv2.polylines(frame, [pts], isClosed = True, color = (255,0,0), thickness=1)
        
        return frame_roi
    else: # empty
        return frame
        
def preprocess_frame(frame):

    # Resize frame
    dim = (gui.canvas_w, gui.canvas_h)
    frame_resize = cv2.resize(frame, dim, interpolation = cv2.INTER_AREA)

    # Correct the color
    frame_corr_color = cv2.cvtColor(frame_resize, cv2.COLOR_BGR2RGB)

    # Mirror horizontally
    frame_flip = np.fliplr(frame_corr_color)
        
    return frame_flip    

def update_frame():

    global global_frame, roi_img, roi_flag

    ret, frame = cap.read()

     # If can't read frame
    if (ret is None) | (ret == False):
        display_status("Cannot capture frame from source")
        stop()
        return 0

    frame_flip = preprocess_frame(frame)
    global_frame = frame_flip.copy()
    
    # Apply ROI filter
    if roi_flag == True: 
        frame_show = frame_flip.copy()
        frame_show = draw_polygon_roi(frame_show)
        frame_flip[roi_img == 0] = 0 
        
    else:
        frame_show = frame_flip
    
    img = Image.fromarray(frame_show)
    gui.gui_top.canvas_l_img.paste(img)
    
    # Apply Background Subtraction
    frame_bg_sub = backSub.apply(frame_flip)
    
    # Select Method for Foreground detection
    if gui.gui_down.select_method == 0:
        # Background Subtraction 
        #frame_bg_sub = backSub.apply(frame_flip) # TODO uncomment this line

        # Filter only bg Sub part
        frame_filter = frame_flip
        frame_filter[frame_bg_sub==0] = 0

    elif gui.gui_down.select_method == 1:

        # Check if image path exist
        if not exists(gui.gui_down.get_bg_img_path()):
            display_status("Background image path does not exist!")
            stop()
            return 0

        # TODO: Need to read only once, just a temporary solution 
        dim = (gui.canvas_w, gui.canvas_h)
        bg_img = cv2.imread(gui.gui_down.get_bg_img_path(), cv2.IMREAD_COLOR)
        bg_img = cv2.resize(bg_img, dim, interpolation = cv2.INTER_AREA)
        bg_img = np.fliplr(bg_img)

        # Absolute Diff
        frame_filter = frame_flip.copy()
        frame_filter = cv2.cvtColor(frame_filter, cv2.COLOR_BGR2RGB)
        frame_sad = cv2.absdiff(frame_filter, bg_img)
        frame_filter[frame_sad<=20] = 0

    # Blob detection
    # blob_keypoints = blob_detector.detect(frame_filter)
    select_mode = gui.gui_down.get_select_mode()

    # Classification
    predictions = model.predict_result(frame_flip)
    categories = predictions[:, 5]
    
    # Check if there is any person in the frame
    if ( len(predictions) == 1 and (0 in categories) ):
        boxes = predictions[:, :4] # x1, y1, x2, y2
        
        img_with_keypoints = frame_flip.copy()
        try:
            cv2.rectangle(img_with_keypoints, (boxes[0,0],boxes[0,1]), (boxes[0,2],boxes[0,3]), (0,255,0), (10))
        except:
            print("boxes does not exist")
        
        img2 = Image.fromarray(img_with_keypoints)

        if select_mode == 1:
            curr_frame = cap.get(cv2.CAP_PROP_POS_FRAMES)
            text = "Frame No. "+str(curr_frame)+" : Person"
        else:
            dateTimeObj = datetime.now()
            text = dateTimeObj.strftime("%m/%d/%Y, %H:%M:%S")+': Person'
    else:
        img2 = Image.fromarray(frame_filter)
        
        if  select_mode== 1:
            curr_frame = cap.get(cv2.CAP_PROP_POS_FRAMES)
            text = "Frame No. "+str(curr_frame)+" : Empty Scene"
        else:
            dateTimeObj = datetime.now()
            text = dateTimeObj.strftime("%m/%d/%Y, %H:%M:%S")+': Empty Scene'          
    
    
       
    gui.gui_down.display_scrolltext(text)
    gui.gui_top.canvas_r_img.paste(img2)
    
    if run_camera:
        window_app.after(10, update_frame)

def write_video(video_writer, filepath):
    ret, frame = cap.read()

    video_writer.write(frame)

    if finish_record:
        video_writer and video_writer.release()
    else:
        write_video(video_writer, filepath)

def create_roi():
    
    global roi_points
    
    roi_points = []
    
    # Get Points from callback functions  
    cv2.imshow('ROI', global_frame)
    cv2.setMouseCallback('ROI', click_event_ROI)
    

def click_event_ROI(event, x, y, flags, params):

    global roi_img 
    
    roi_img = np.zeros([canvas_w, canvas_h, 3], dtype=np.uint8)
       
    # checking for left mouse clicks
    if event == cv2.EVENT_LBUTTONDOWN:
 
        # displaying the coordinates
        # on the image window
        font = cv2.FONT_HERSHEY_SIMPLEX
        
        cv2.putText(global_frame, str(x) + ',' +
                    str(y), (x,y), font,
                    1, (255, 0, 0), 2)
        roi_points.append([x,y])
        cv2.imshow('ROI', global_frame)
        cv2.waitKey(0)
        cv2.destroyWindow('ROI')
        
        # Connect dots and create polygon       
        pts = np.array(roi_points,np.int32)
        roi_img = cv2.fillPoly(roi_img, [pts], (255,255,255))
    
def display_status(msg):
    status_msg = "STATUS: "+msg
    status_text.config(text=status_msg)

# ---- buttons_left ----
buttons_left = tk.Frame(window_app)
buttons_left.grid(row=2, column=0)

button_play = tk.Button(buttons_left, text="Play", command=play)
button_play.pack(side='left')

button_stop = tk.Button(buttons_left, text="Stop", command=stop, state='disabled')
button_stop.pack(side='left')

button_pause = tk.Button(buttons_left, text="Pause", command=pause_frame, state='disabled')
button_pause.pack(side='left')

button_resume = tk.Button(buttons_left, text="Resume", command=resume_frame, state='disabled')
button_resume.pack(side='left')

# ---- buttons_right ----
buttons_right = tk.Frame(window_app)
buttons_right.grid(row=2, column=1)

button_apply_ROI     = tk.Button(buttons_right, text="Apply ROI filter", command=apply_ROI)
button_apply_ROI.pack(side='left')

button_create_ROI    = tk.Button(buttons_right, text="Create ROI filter", command=create_roi)
button_create_ROI.pack(side='left')

button_default_ROI    = tk.Button(buttons_right, text="default ROI value", command=default_roi)
button_default_ROI.pack(side='left')
# ---- /end buttons_left ----

# Status Bar
status_text = tk.Label(window_app)
status_text.grid(row=3, column=0)

window_app.mainloop()

#cap.release()
