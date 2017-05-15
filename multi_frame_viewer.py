import os, glob, csv
import tkinter as tk
from PIL import Image, ImageTk
import math

# CONFIGURATION
COLOR_PRIMARY = "black"
COLOR_SECONDARY = "#115599"
COLOR_TEXT = "white"
IMAGENAME_FORM_DEFAULT = "%d.jpg"

class FolderObj(object):
    def __init__(self, main, foldername, formentry):
        self.parent = main
        self.formentry = formentry
        self.active = False
        self.foldername = foldername
        self.button = tk.Button(self.parent.frame1, text = foldername, bg = COLOR_PRIMARY, fg = COLOR_TEXT, command = self.callback_button)
        self.button.pack(anchor=tk.W, fill = tk.X, expand=1)
        
    def callback_button(self):
        if self.active:
            self.button.configure(relief = tk.RAISED, bg = COLOR_PRIMARY)
            self.active = False
            self.parent.activeCount -= 1
            self.win.destroy()
        else:
            self.button.configure(relief = tk.SUNKEN, bg = COLOR_SECONDARY)
            self.active = True
            self.win = tk.Toplevel(self.parent)
            self.win.title(self.foldername)
            self.win.geometry('320x240+%d+%d' % (self.parent.offsetx+self.parent.activeCount*50,self.parent.offsety+self.parent.activeCount*25))
            self.parent.activeCount += 1
            self.canvas = tk.Canvas(self.win, bg="black")
            self.canvas.pack(fill=tk.BOTH, expand = 1)
            #self.canvas.bind("<Configure>", self.resize_image)
            img = Image.new("1", (320, 240))
            self.tkimg = ImageTk.PhotoImage(img)
            self.cimg = self.canvas.create_image(0,0, image=self.tkimg, anchor=tk.NW)
            self.win.bind("<Down>", self.parent.callback_next_image)
            self.win.bind("<Up>", self.parent.callback_prev_image)
            self.win.protocol("WM_DELETE_WINDOW", self.callback_closing_window)
            self.win.focus_set()
            numFiles = len(os.listdir(self.foldername))
            if numFiles > self.parent.imgMax:
                self.parent.imgMax = numFiles
           
    def load_image(self, currentImg):
        imgname = self.foldername + "\\" + self.formentry % currentImg
        try:
            img = Image.open(imgname)
            iwidth,iheight = img.size
            iratio = iheight/float(iwidth)
            cwidth = self.canvas.winfo_width()
            cheight =int(math.floor(cwidth*iratio))
            #print(cwidth,cheight,iratio,iwidth,iheight)
            img = img.resize((cwidth,cheight))
            self.tkimg = ImageTk.PhotoImage(img)
            self.canvas.itemconfig(self.cimg, image=self.tkimg)
            self.win.title(self.foldername + ": %d" % currentImg)
        except:
            print("Failed %s : %d" % (self.foldername,currentImg))
            
    def callback_closing_window(self):
        self.callback_button()
        
class App(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.offsetx = 300
        self.offsety = 0
        self.currentImg = 1
        self.imgMax = 0
        self.activeCount = 1
        self.currentEvent = 1
        self.configure(bg = COLOR_PRIMARY)
        self.frame1 = tk.Frame(self, bg = COLOR_PRIMARY)
        self.frame2 = tk.Frame(self, bg = COLOR_PRIMARY)
        self.frame1.pack(side=tk.LEFT, fill=tk.Y, expand=1)
        self.frame2.pack(side=tk.RIGHT, fill=tk.Y, expand=1)
        
        tk.Label(self.frame1, text = "Enter Form", bg = COLOR_SECONDARY, fg = COLOR_TEXT).pack(padx=3,pady=3,anchor=tk.W,fill=tk.X,expand=1)
        self.form = tk.Entry(self.frame1, bg = COLOR_PRIMARY, fg = COLOR_TEXT)
        self.form.pack()
        self.form.insert(0, IMAGENAME_FORM_DEFAULT)
        self.filesep = '\\'
        files = os.listdir('.')
        
        self.folders = [i for i in files if os.path.isdir(i)]
        self.buttonFolders = []

        for i,f in enumerate(self.folders):
            self.buttonFolders.append(FolderObj(self, f, self.form.get()))
        
        self.launchCoder = tk.Button(self.frame1, text = "Coder", bg = COLOR_SECONDARY, fg = COLOR_TEXT, command = self.callback_launch_coder)
        self.launchCoder.pack(anchor=tk.W, fill = tk.X, expand=1)
        
        self.bind("<Down>", self.callback_next_image)
        self.bind("<Up>", self.callback_prev_image)
        
        self.scale = tk.Scale(self.frame2, orient=tk.VERTICAL, from_=0, to_=100, bg=COLOR_PRIMARY, fg=COLOR_TEXT, highlightthickness=0)
        self.scale.bind("<ButtonRelease-1>", self.callback_scale)
        self.scale.pack(fill = tk.Y, expand = 1)
    
    def callback_launch_coder(self):
        fid = open("events.txt", "r")
        csvreader = csv.reader(fid, delimiter=",")
        self.events = [[int(a) for a in x] for x in csvreader]
        print(self.events)
        
    def callback_next_image(self, event):
        self.currentImg += 1
        self.update_images()
                
    def callback_prev_image(self, event):
        if self.currentImg > 0:
            self.currentImg -= 1
            self.update_images()
                    
    def callback_scale(self,event):
        self.currentImg = int(math.ceil((self.scale.get()/100.0)*self.imgMax))
        #print(math.ceil((self.scale.get()/100.0)*self.imgMax), self.imgMax, self.currentImg)
        self.update_images()
    
    def update_images(self):
        for f in self.buttonFolders:
            if f.active:
                f.load_image(self.currentImg)
                
                

if __name__ == "__main__":     
    app = App()
    app.update()
    aw = app.winfo_width()
    ah = app.winfo_height()
    app.geometry('%dx%d+0+0' % (aw,ah))
    app.mainloop()