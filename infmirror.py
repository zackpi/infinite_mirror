import cv2
import numpy as np
import tkinter as tk
from PIL import Image, ImageTk
from tkinter import filedialog as fd


class Interact:
    def __init__(self):
        self.imfile = None
        self.image = None
        self.draw = None
        self.dirty = True
        
        self.root = tk.Tk()
        self.root.title("Recursive Image Generator")
        
        self.menu = tk.Menu(self.root)
        self.root.config(menu=self.menu)

        self.filemenu = tk.Menu(self.menu, tearoff=0)
        self.filemenu.add_command(label="Open", command=self.load)
        self.filemenu.add_command(label="Save", command=self.save)
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Exit", command=self.root.quit)
        self.menu.add_cascade(label="File", menu=self.filemenu)

        self.helpmenu = tk.Menu(self.menu, tearoff=0)
        self.helpmenu.add_command(label="About", command=self.root.quit)
        self.menu.add_cascade(label="Help", menu=self.helpmenu)
        
        self.canvas = tk.Canvas(self.root, width=640, height=480)
        self.canvas.bind("<Button-1>", self.mouseclick)
        self.canvas.bind("<B1-Motion>", self.mousemove)
        self.canvas.bind("<ButtonRelease-1>", self.mousedrop)
        self.canvas.pack()
        self.canvas.focus_set()
        
        self.redraw_timer = self.root.after(100, self.redraw)
        self.root.mainloop()
    
    def make_recursive_image(self, dst):
        if self.image is None:
            defaulttext = "Use File>Open to select an image to modify"
            (width, height), thick = cv2.getTextSize(defaulttext, cv2.FONT_HERSHEY_SIMPLEX, .5, 1)
            self.draw = cv2.putText(np.full((480,640), (0,0,0), dtype=(np.uint8,3)),
                                    defaulttext, (320-width//2,240-height//2), 
                                    cv2.FONT_HERSHEY_SIMPLEX, .5, (100,100,100))
            return
        self.draw = self.image.copy()
        
        r,c,_ = self.draw.shape
        src = np.array([(0,0),(c,0),(c,r),(0,r)])
        dst = np.array(dst)
        hom, _ = cv2.findHomography(src, dst)
        
        for i in range(4):
            warp = cv2.warpPerspective(self.draw, hom, (c,r), flags=cv2.INTER_LANCZOS4)
            cutout = cv2.fillConvexPoly(self.draw, dst, [0,0,0])
            self.draw = cv2.bitwise_or(cutout, warp)
    
    def redraw(self):
        if self.dirty:
            self.dirty = False
            self.make_recursive_image([])
            
            disp = cv2.cvtColor(self.draw, cv2.COLOR_BGR2RGB)
            disp = Image.fromarray(disp)
            disp = ImageTk.PhotoImage(image=disp)
            self.canvas.create_image(320, 240, image=disp)
            self.canvas.image = disp
        
        self.redraw_timer = self.root.after_idle(self.redraw)     
    
    def mouseclick(self, event):
        self.clicked = True
    
    def mousemove(self, event):
        self.mx = 0
        self.my = 0
        self.dirty = True
    
    def mousedrop(self, event):
        self.clicked = False
    
    def save(self):
        self.root.after_cancel(self.redraw_timer)
        self.root.update_idletasks()
        savefile = fd.asksaveasfilename()
        cv2.imwrite(savefile, self.draw)
        self.root.after(100, self.redraw) 
    
    def load(self):
        self.root.after_cancel(self.redraw_timer)
        self.root.update_idletasks()
        self.imfile = fd.askopenfilename()
        self.root.update()
        self.load_image()
        self.root.after(100, self.redraw) 
    
    def load_image(self):
        self.image = cv2.imread(self.imfile)
        h,w = self.image[:2]
        self.root.resizable(True, True)
        self.canvas.config(width=w, height=h)
        self.root.resizable(False, False)
        self.dirty = True


if __name__=="__main__":
    Interact()

