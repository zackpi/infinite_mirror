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
        self.default_background()
        
        self.xoff, yoff = 0,0
        self.disp = None
        self.dirty = True
        
        self.width = 1
        self.height = 1
        self.root = tk.Tk()
        self.root.title("Recursive Image Generator")
        self.root.minsize(120, 100)
        
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
        
        self.canvas = tk.Canvas(self.root, bg="#000", width=640, height=480)
        self.canvas.bind("<Button-1>", self.on_mouseclick)
        self.canvas.bind("<B1-Motion>", self.on_mousemove)
        self.canvas.bind("<ButtonRelease-1>", self.on_mousedrop)
        self.canvas.bind("<Configure>", self.on_resize)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.focus_set()
        
        self.window = [(50,40),(70,40),(70,60),(50,60)]
        
        self.redraw_timer = self.root.after(100, self.redraw)
        self.root.mainloop()
    
    def make_recursive_image(self, dst):
        if self.image is None:
            self.default_background()
            return
        self.draw = self.image.copy()
        
        r,c = self.draw.shape[:2]
        src = np.array([(0,0),(c,0),(c,r),(0,r)])
        dst = np.array(dst)
        hom, _ = cv2.findHomography(src, dst)
        
        for i in range(4):
            warp = cv2.warpPerspective(self.draw, hom, (c,r), flags=cv2.INTER_LANCZOS4)
            cutout = cv2.fillConvexPoly(self.draw, dst, [0,0,0])
            self.draw = cv2.bitwise_or(cutout, warp)
    
    def redraw(self):
        self.canvas.unbind("<Configure>")
        r,c = self.draw.shape[:2]
        h,w = self.height, self.width
        wide = c/r > w/h
        xscl = c*h/r if not wide else w
        yscl = r*w/c if wide else h
        xoff = (w-xscl)/2 if not wide else 0
        yoff = (h-yscl)/2 if wide else 0
        
        if self.dirty:
            self.dirty = False
            self.make_recursive_image([(40,5),(380,40),(400,270),(60,280)])
            
            img_cv2 = cv2.cvtColor(self.draw, cv2.COLOR_BGR2RGB)
            img_pil = Image.fromarray(img_cv2)
            img_tk = ImageTk.PhotoImage(image=img_pil)
            self.disp = img_tk
        
        self.canvas.delete("all")
        self.canvas.create_image(xoff, yoff, anchor=tk.NW, image=self.disp)
        self.canvas.create_polygon(*self.window[0], *self.window[1],
                                    *self.window[2], *self.window[3], 
                                    fill="#1c4", outline="#3e7", activefill="#5fa")
        self.canvas.image = self.disp
        self.canvas.addtag_all("all")
        
        self.canvas.bind("<Configure>", self.on_resize)
        self.redraw_timer = self.root.after(100,self.redraw)     
    
    def default_background(self):
        defaulttext = "Use File>Open to select an image to modify"
        (width, height), thick = cv2.getTextSize(defaulttext, cv2.FONT_HERSHEY_SIMPLEX, .5, 1)
        self.draw = cv2.putText(np.full((482,642), (0,0,0), dtype=(np.uint8,3)),
                                defaulttext, (320-width//2,240-height//2), 
                                cv2.FONT_HERSHEY_SIMPLEX, .5, (100,100,100))
    
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
        self.canvas.scale("all",0,0,event.width/self.width,event.height/self.height)
        self.width = event.width
        self.height = event.height
        self.dirty = True


if __name__=="__main__":
    Interact()

