# app_gui_down
import tkinter as tk
import tkinter.scrolledtext as st

class app_gui_down():

    def __init__(self, window_app, canvas_w, canvas_h):

        self.camera_var = tk.StringVar()
        self.video_var  = tk.StringVar()
        self.record_var = tk.StringVar()
        self.proc_device = tk.StringVar()
        self.model_file = tk.StringVar()
        
        self.roi_x_entry = tk.StringVar()
        self.roi_y_entry = tk.StringVar()
        self.roi_radius = tk.StringVar()

        self.select_mode = 0 # Mode 0: Camera 1: Video 2: Auto
        self.record_status = 0 # Record Mode only

        # TODO! Deal with this default value
        default_video_path = "videos/Person_stand.mp4"
        
        # GUI lower part -------------------------------

        # GUI Scroll text left
        self.scroll_txt_left = st.ScrolledText(
            window_app, 
            width = (int)(0.125*canvas_w),
            height = 20
            )
        self.scroll_txt_left.grid(row=1, column=0)

        # GUI Setting Right
        self.setting_frame = tk.Frame(
            window_app, 
            width = (int)(0.125*canvas_w),
            height = 20)
        self.setting_frame.grid(row=1, column=1)

        i = 0

        tk.Label(
            self.setting_frame,
            text="Control and Setting Panel"
        ).grid(row=i, columnspan=2)

        # Create components with Button, Label and Entry box
        # label
        # label + entry box

        # 1: Camera (DEFAULT)
        self.btn_camera     = tk.Button(self.setting_frame, text="Camera", command=self.press_btn_camera)
        self.btn_camera.grid(row=2*i+1, column=0, sticky='w')
        self.btn_camera.config(relief=tk.SUNKEN)

        self.label_camera   = tk.Label(self.setting_frame, text="Camera Number")
        self.label_camera.grid(row=2*i+2, column=0, sticky='w')

        self.entry_camera   = tk.Entry(self.setting_frame, textvariable=self.camera_var)
        self.entry_camera.grid(row=2*i+2, column=1, sticky='e')       
        i = i + 1

        # 2: Video
        self.btn_video     = tk.Button(self.setting_frame, text="Video", command=self.press_btn_video)
        self.btn_video.grid(row=2*i+1, column=0, sticky='w')

        self.label_video   = tk.Label(self.setting_frame, text="Video Path")
        self.label_video.grid(row=2*i+2, column=0, sticky='w')

        self.entry_video   = tk.Entry(self.setting_frame, textvariable=self.video_var)
        self.entry_video.grid(row=2*i+2, column=1, sticky='e')
        self.entry_video.insert(tk.END, default_video_path)
        i = i + 1

        # 3: Record
        self.btn_record     = tk.Button(self.setting_frame, text="Start Record", command=self.press_btn_start_record)
        self.btn_record.grid(row=2*i+1, column=0, sticky='w')

        self.btn_stop_record = tk.Button(self.setting_frame, text="Stop Record", command=self.press_btn_stop_record)
        self.btn_stop_record.grid(row=2*i+1, column=1, sticky='w')

        self.label_record   = tk.Label(self.setting_frame, text="Export Directory")
        self.label_record.grid(row=2*i+2, column=0, sticky='w')

        self.entry_record   = tk.Entry(self.setting_frame, textvariable=self.record_var)
        self.entry_record.grid(row=2*i+2, column=1, sticky='e')
        self.entry_record.insert(tk.END, "records/record.mp4") # TODO read from config
        i = i + 1
        
        # 4: Processing Device
        self.label_proc_device = tk.Label(self.setting_frame, text="Processing Unit")
        self.label_proc_device.grid(row=2*i+1, column=0, sticky='w')
        
        self.entry_proc_device   = tk.Entry(self.setting_frame, textvariable=self.proc_device)
        self.entry_proc_device.grid(row=2*i+1, column=1, sticky='e')
        self.entry_proc_device.insert(tk.END, "cuda") #TODO read from config
        
        self.label_model_file = tk.Label(self.setting_frame, text="Model filename")
        self.label_model_file.grid(row=2*i+2, column=0, sticky='w')
        
        self.entry_model_file   = tk.Entry(self.setting_frame, textvariable=self.model_file)
        self.entry_model_file.grid(row=2*i+2, column=1, sticky='e')
        self.entry_model_file.insert(tk.END, "models/yolov5m.pt") #TODO read from config
        i = i + 1
        
        # 5: Model Setting
        # TODO Model Confidence Threshold
        
        
    # Find out if button is raised or flat
    def RaisedOrFlat(self, buttonName):
        
        button = buttonName
        # check if the button is Raised
        if button['relief']== "raised": 
            return 'raised'
        # check if the button is flat
        elif button['relief'] == "sunken": 
            return 'sunken'

    # Display text on scroll text widget
    def display_scrolltext(self, txt):
        self.scroll_txt_left.config(state=tk.NORMAL)
        self.scroll_txt_left.insert(tk.END, '\n'+txt)
        self.scroll_txt_left.yview_pickplace("end")
        self.scroll_txt_left.config(state=tk.DISABLED)

    # Button actions for MODE selection
    def press_btn_camera(self):
        self.btn_camera.config(relief=tk.SUNKEN)
        self.btn_video.config(relief=tk.RAISED)
        self.btn_record.config(relief=tk.RAISED)

        self.select_mode = 0

    def press_btn_video(self):
        self.btn_camera.config(relief=tk.RAISED)
        self.btn_video.config(relief=tk.SUNKEN)
        self.btn_record.config(relief=tk.RAISED)

        self.select_mode = 1
        self.record_status = 0

    def press_btn_start_record(self):
        self.btn_camera.config(relief=tk.SUNKEN)
        self.btn_video.config(relief=tk.RAISED)
        self.btn_record.config(relief=tk.SUNKEN)

        self.record_status = 1

    def press_btn_stop_record(self):

        self.record_status = 0
        return 0
        
    # Method for get value from entry boxes
    def get_camera_number(self):
        return self.entry_camera.get()

    def get_video_path(self):
        return self.entry_video.get() 

    def get_record_export_path(self):
        return self.record_var.get()

    def get_select_mode(self):
        return self.select_mode

    def get_record_status(self):
        return self.record_status
