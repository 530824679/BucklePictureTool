import os
import glob
import tkinter as tk
import tkinter.filedialog as dlg
import tkinter.messagebox as msgbx
from tkinter import Label, Button, Canvas, Entry, Frame
from PIL import Image, ImageTk

class ImageData():
    def __init__(self, path):
        self.file_path = path
        self.base_name = None
        self.isEditted = False

        self.set_basename()

    def set_basename(self):
        if self.file_path is not None:
            self.base_name = os.path.basename(self.file_path)

class DataAnnotationTool(object):
    def __init__(self):
        self.image_dir = None
        self.save_dir = None
        self.data_list = []
        self.num_img_file = 0

        self.ref_id = None

        self.window_width = 1000
        self.window_height = 800

        self.class_index = 1
        self.class_dict = {
            "calling": 0,
            "normal": 1,
            "smoking": 2
        }

        self.anno_index = 0

        self.set_widgets()

    def set_widgets(self):
        # create main window
        self.mainWindow = tk.Tk()
        self.mainWindow.geometry(str(self.window_width) + 'x' + str(self.window_height))
        self.mainWindow.title("data annotation tool")

        # create total Frame to lay out all components
        self.frame = Frame(self.mainWindow)
        self.frame.pack(fill=tk.BOTH, expand=tk.YES, side=tk.LEFT)

        # create directory label frame
        self.lf_dir = tk.LabelFrame(self.frame, text='Directory')
        self.lf_dir.pack(fill=tk.BOTH, anchor=tk.W, padx=10, pady=2)

        # create diectory entry bar
        self.src_label_img = tk.Label(self.lf_dir, text="图像目录：")
        self.src_label_img.grid(row=0)

        self.load_entry_dir = tk.Entry(self.lf_dir, width=110)
        self.load_entry_dir.grid(row=0, column=1, columnspan=10)

        # create open button
        self.open_btn_dir = tk.Button(self.lf_dir, text='Open Folder', command=self.open_img_directory, width=14)
        self.open_btn_dir.grid(row=0, column=12, padx=15)

        self.dst_label_img = tk.Label(self.lf_dir, text="存储目录：")
        self.dst_label_img.grid(row=1)

        self.save_entry_dir = tk.Entry(self.lf_dir, width=110)
        self.save_entry_dir.grid(row=1, column=1, rowspan=2, columnspan=10)

        # create save button
        self.save_btn_dir = tk.Button(self.lf_dir, text='Save Folder', command=self.open_save_directory, width=14)
        self.save_btn_dir.grid(row=1, column=12, columnspan=2, padx=15, pady=10)

        # create image canvas
        self.f_canvas = tk.Frame(self.frame)
        self.f_canvas.pack(fill=tk.X, padx=10)

        # create file list box
        self.lf_filelistbox = tk.LabelFrame(self.f_canvas, text='file list', fg='Blue')
        self.lf_filelistbox.pack(side=tk.LEFT, fill=tk.Y)

        self.sc_file = tk.Scrollbar(self.lf_filelistbox)
        self.sc_file.pack(side=tk.RIGHT, fill=tk.Y)

        filelistvar = tk.StringVar("")
        self.filelistbox = tk.Listbox(self.lf_filelistbox, listvariable=filelistvar, yscrollcommand=self.sc_file.set)
        self.filelistbox.configure(selectmode="single")
        self.filelistbox.pack(side=tk.LEFT, fill=tk.Y)
        self.filelistbox.bind('<<ListboxSelect>>', self.filelistbox_selected)
        self.sc_file.config(command=self.filelistbox.yview)

        self.f_canvas_ref = tk.Frame(self.f_canvas)
        self.f_canvas_ref.pack(side=tk.LEFT)
        self.canvas_ref = tk.Canvas(self.f_canvas_ref, bg="black", width=600, height=520)
        self.canvas_ref.pack(side=tk.LEFT, padx=5)
        self.canvas_ref.bind("<ButtonPress-1>", self.on_left_clicked)
        self.canvas_ref.bind("<ButtonRelease-1>", self.on_left_released)
        self.canvas_ref.bind("<ButtonPress-3>", self.on_right_clicked)
        self.canvas_ref.bind("<ButtonRelease-3>", self.on_right_released)
        self.canvas_ref.bind("<Button1-Motion>", self.on_mouse_move)
        self.canvas_ref.bind("<Button3-Motion>", self.on_mouse_move)

        # create class list box
        self.lf_classlistbox = tk.LabelFrame(self.f_canvas, text='class list', fg='Blue')
        self.lf_classlistbox.pack(side=tk.TOP, fill=tk.X)

        self.sc_class = tk.Scrollbar(self.lf_classlistbox)
        self.sc_class.pack(side=tk.RIGHT, fill=tk.Y)

        classinfo = ("calling", "normal", "smoking")
        classlistvar = tk.StringVar(value=classinfo)
        self.classlistbox = tk.Listbox(self.lf_classlistbox, listvariable=classlistvar, height=8, yscrollcommand=self.sc_class.set)
        self.classlistbox.configure(selectmode="single")
        self.classlistbox.pack(side=tk.TOP, fill=tk.X)
        self.classlistbox.bind('<<ListboxSelect>>', self.classlistbox_selected)
        self.sc_class.config(command=self.classlistbox.yview)

        # create anno object
        self.lf_annolistbox = tk.LabelFrame(self.f_canvas, text='annotation list', fg='Blue')
        self.lf_annolistbox.pack(side=tk.TOP, fill=tk.X)

        self.sc_anno = tk.Scrollbar(self.lf_annolistbox)
        self.sc_anno.pack(side=tk.RIGHT, fill=tk.Y)

        annolistvar = tk.StringVar("")
        self.annolistbox = tk.Listbox(self.lf_annolistbox, listvariable=annolistvar, height=8, yscrollcommand=self.sc_anno.set)
        self.annolistbox.configure(selectmode="single")
        self.annolistbox.pack(side=tk.TOP, fill=tk.X)
        self.annolistbox.bind('<<ListboxSelect>>', self.annolistbox_selected)
        self.sc_anno.config(command=self.annolistbox.yview)

        self.lf_button = tk.LabelFrame(self.f_canvas, text='operation', fg='Blue')
        self.lf_button.pack(side=tk.TOP, fill=tk.X)

        # create load button
        self.read_btn_text = tk.StringVar()
        self.read_btn_text.set('Load Images')
        self.read_btn_dir = tk.Button(self.lf_button, textvariable=self.read_btn_text, width=14, command=self.load_images)
        self.read_btn_dir.pack(pady=5)

        # create rect button
        self.rect_btn_text = tk.StringVar()
        self.rect_btn_text.set('Create Rect')
        self.rect_btn_dir = tk.Button(self.lf_button, textvariable=self.rect_btn_text, width=14, command=self.create_rect)
        self.rect_btn_dir.pack(pady=6)

        # create verify button
        self.verify_btn_text = tk.StringVar()
        self.verify_btn_text.set('Verify Rect')
        self.verify_btn_dir = tk.Button(self.lf_button, textvariable=self.verify_btn_text, width=14, command=self.verify_rect)
        self.verify_btn_dir.pack(pady=6)

        # create save button
        self.save_btn_text = tk.StringVar()
        self.save_btn_text.set("Save Anno")
        self.save_btn = tk.Button(self.lf_button, textvariable=self.save_btn_text, width=14, command=self.on_save_btn_pressed)
        self.save_btn.pack(pady=6)

        # create image switch button
        self.fr_btn = tk.Frame(self.frame)
        self.fr_btn.pack(anchor=tk.S, padx=10, pady=2)
        self.prev_btn = tk.Button(self.fr_btn, text='←Previous', command=self.on_previous_btn_pressed)
        self.prev_btn.pack(side=tk.LEFT, padx=2)
        self.entry_pagejump = tk.Entry(self.fr_btn, width=5)
        self.entry_pagejump.pack(side=tk.LEFT, padx=5)
        self.jump_btn = tk.Button(self.fr_btn, text='Jump', command=self.on_jump_btn_pressed)
        self.jump_btn.pack(side=tk.LEFT, padx=2)
        self.next_btn = tk.Button(self.fr_btn, text='Next→', command=self.on_next_btn_pressed)
        self.next_btn.pack(side=tk.RIGHT, padx=5)

    def on_previous_btn_pressed(self):
        if self.ref_id == None: return

        self.ref_id -= 1
        if self.ref_id < 0:
            self.ref_id = self.num_img_file - 1

        self.load_image()

    def on_jump_btn_pressed(self):
        if self.ref_id is None: return

        # Get image id
        id_str = self.entry_pagejump.get()

        if(id_str is None) or (id_str is ""): return
        id = int(id_str) - 1
        if id < 0:
            id = self.num_img_file - abs(id)
        if id > self.num_img_file:
            id = self.num_img_file - 1

        self.ref_id = id
        self.load_image()

        self.entry_pagejump.delete(0, tk.END)

    def on_next_btn_pressed(self):
        if self.ref_id == None: return

        self.ref_id += 1
        if self.ref_id >= self.num_img_file:
            self.ref_id = 0

        self.load_image()

    def on_save_btn_pressed(self):
        pass

    def filelistbox_selected(self, evemt):
        for i in self.filelistbox.curselection():
            self.ref_id = i
            self.load_image()
            self.isDrawable = True

    def classlistbox_selected(self, event):
        for i in self.classlistbox.curselection():
            self.class_index = self.class_dict[self.classlistbox.get(i)]

    def annolistbox_selected(self, event):
        for i in self.annolistbox.curselection():
            self.anno_index = self.annolistbox.get(i)

    def on_left_clicked(self):
        pass

    def on_left_released(self):
        pass

    def on_right_clicked(self):
        pass

    def on_right_released(self):
        pass

    def on_mouse_move(self):
        pass

    def open_img_directory(self):
        self.image_dir = dlg.askdirectory()
        if self.image_dir:
            self.load_entry_dir.delete(0, 'end')
            self.load_entry_dir.insert(0, self.image_dir)

        filelist = os.listdir(self.image_dir)
        filelist.sort(key = lambda x: int(x[:-4]))
        self.filelistbox.delete(0, 'end')
        self.ref_id = 0
        self.data_list.clear()
        for index, file in enumerate(filelist):
            self.filelistbox.insert(index, file)

    def open_save_directory(self):
        self.save_dir = dlg.askdirectory()

        if self.save_dir:
            if not os.path.exists(self.save_dir):
                try:
                    os.mkdir(self.save_dir)
                    tk.messagebox.showinfo('create annotation directory: \n' + self.save_dir)
                except:
                    pass

            self.save_entry_dir.delete(0, 'end')
            self.save_entry_dir.insert(0, self.save_dir)

    def load_images(self):
        if self.image_dir:
            dir = self.image_dir
            dir = os.path.join(dir, "*.jpg")
            file_list = sorted(glob.glob(dir))

            self.num_img_file = len(file_list)
            print("Number of images in {}: {}".format(self.image_dir, str(self.num_img_file)))

            # read first image
            if self.num_img_file > 0:
                for i in range(self.num_img_file):
                    self.data_list.append(ImageData(file_list[i]))

                self.ref_id = 0
                self.load_image()
                self.isDrawable = True

    def load_image(self):
        if self.ref_id == None: return

        ref_filepath = self.get_reference_filepath()
        self.ref_image_org = Image.open(ref_filepath)

        self.show_images()
        self.canvas_ref.config(height=self.ref_image_org.height, width=self.ref_image_org.width)

    def show_images(self):
        self.ref_image_display = ImageTk.PhotoImage(self.ref_image_org)
        self.canvas_ref.create_image(0, 0, anchor="nw", image=self.ref_image_display)

    def create_rect(self):
        pass

    def verify_rect(self):
        pass

    def get_reference_filepath(self):
        return self.data_list[self.ref_id].file_path

    def get_save_filepath(self):
        filename = self.data_list[self.ref_id].base_name
        return os.path.join(self.save_dir, filename)

    def run(self):
        self.mainWindow.mainloop()


if __name__ == '__main__':
    data_annotation_tool = DataAnnotationTool()
    data_annotation_tool.run()