import cv2
import numpy as np
import tkinter as tk

def make_recursive_image(img, dst):
    ret = img.copy()
    
    r,c,_ = img.shape
    src = np.array([(0,0),(c,0),(c,r),(0,r)])
    dst = np.array(dst)
    hom, _ = cv2.findHomography(src, dst)
    
    for i in range(4):
        warp = cv2.warpPerspective(ret, hom, (c,r), flags=cv2.INTER_LANCZOS4)
        ret = cv2.fillConvexPoly(ret, dst, [0,0,0])
        ret = cv2.bitwise_or(ret, warp)
    return ret

class Interact:
    def __init__(self):
        self.imfile = None
        self.image = None
        self.draw = None
        self.dirty = False
        
        self.load_root = None
        self.load_entry = None
        self.load_button = None
        
        self.cnvs_root = None
        self.design()
    
    def redraw(self):
        if self.dirty:
            # drawing code here
            self.dirty = False
        self.cnvs_root.after_idle(self.redraw)
    
    def design(self):
        if self.load_root:
            self.load_root.destroy()
            self.load_root = None
    
        self.cnvs_root = tk.Tk()
        self.canvas = tk.Canvas(self.cnvs_root, width=400, height=400)
        self.canvas.pack()

        self.canvas.bind("<Button-1>", self.mouseclick)
        self.canvas.bind("<B1-Motion>", self.mousedrag)
        self.canvas.bind("<ButtonRelease-1>", self.mousedrop)
        self.canvas.bind("n", self.load)
        self.canvas.bind("s", self.save)
        self.canvas.bind("<Configure>", self.resize)
        
        self.canvas.focus_set()
        self.cnvs_root.after(100, self.redraw)
        self.cnvs_root.mainloop()
    
    def load(self, event):
        if self.cnvs_root:
            self.cnvs_root.destroy()
            self.cnvs_root = None
        
        def load_image():
            self.imfile = self.load_entry.get()
            self.image = cv2.imread(self.imfile)
            self.load_root.destroy()
        
        self.load_root = tk.Tk()
        self.load_entry = tk.Entry(self.load_root)
        self.load_entry.pack()
        self.load_button = tk.Button(self.load_root, text="load", width=10, command=load_image)
        self.load_button.pack()
        
        self.load_entry.focus_set()
        self.load_root.mainloop()
    
    def mouseclick(self, event):
        self.clicked = True
    def mousedrag(self, event):
        print("mousedrag")
    def mousedrop(self, event):
        print("mousedrop")
    def save(self, event):
        print("save")
    def resize(self, event):
        print("resize")
    



if __name__=="__main__":
    i = Interact()

