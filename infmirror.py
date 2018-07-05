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
        self.disp = None
        self.dirty = True
        
        self.root = tk.Tk()
        self.root.title("Recursive Image Generator")
        
        self.menu = tk.Menu(self.root)
        self.root.config(menu=self.menu)
        self.root.bind("<Configure>", self.on_resize)

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
        self.canvas.bind("<Button-1>", self.on_mouseclick)
        self.canvas.bind("<B1-Motion>", self.on_mousemove)
        self.canvas.bind("<ButtonRelease-1>", self.on_mousedrop)
        self.canvas.pack(fill="both", expand=True)
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
            self.make_recursive_image([(40,5),(380,40),(400,270),(60,280)])
            
            center = np.zeros((self.height+1, self.width), dtype=(np.uint8,3))
            h,w = self.draw.shape[:2]
            narrow = w/h < self.width/self.height
            xoff = (self.width-w)//2 if narrow else 0
            yoff = (self.height-h)//2 if not narrow else 0
            scl = self.width/w
            center[yoff:yoff+int(1+scl*h), xoff:xoff+int(scl*w)] = cv2.resize(self.draw, (0,0), fx=scl, fy=scl)
            
            img_cv2 = cv2.cvtColor(center, cv2.COLOR_BGR2RGB)
            img_pil = Image.fromarray(img_cv2)
            img_tk = ImageTk.PhotoImage(image=img_pil)
            self.disp = img_tk
        
        self.canvas.delete("ALL")
        self.canvas.create_image(self.width//2, self.height//2, image=self.disp)
        self.canvas.image = self.disp
        self.redraw_timer = self.root.after(100, self.redraw)     
    
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
        h,w = self.image.shape[:2]
        self.root.minsize(w, h)
        self.dirty = True
    
    def on_mouseclick(self, event):
        self.clicked = True
    
    def on_mousemove(self, event):
        self.mx = 0
        self.my = 0
        self.dirty = True
    
    def on_mousedrop(self, event):
        self.clicked = False
    
    def on_resize(self, event):
        self.width = event.width
        self.height = event.height


if __name__=="__main__":
    Interact()

