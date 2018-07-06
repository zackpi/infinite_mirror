import cv2
import numpy as np
import tkinter as tk
from PIL import Image, ImageTk
from tkinter import filedialog as fd

class Interact(tk.Tk):
    
    def __init__(self):
        super().__init__()
        self.title("Recursive Image Generator")
        self.minsize(320, 240)
        self.bind("<Configure>", self.on_resize)
        
        self.canvas = RecursiveImageGenerator(self)
        self.canvas.pack()
        self.cnvs_xscl, self.cnvs_yscl = 1, 1
        
        self.menu = tk.Menu(self)
        self.config(menu=self.menu)

        self.filemenu = tk.Menu(self.menu, tearoff=0)
        self.filemenu.add_command(label="Open", command=self.load)
        self.filemenu.add_command(label="Save", command=self.save)
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Exit", command=self.quit)
        self.menu.add_cascade(label="File", menu=self.filemenu)

        self.helpmenu = tk.Menu(self.menu, tearoff=0)
        self.helpmenu.add_command(label="About", command=self.quit)
        self.menu.add_cascade(label="Help", menu=self.helpmenu)
        
        self.mainloop()
    
    def save(self):
        self.canvas.after_cancel(self.canvas.redraw_timer)
        self.update_idletasks()
        savefile = fd.asksaveasfilename()
        cv2.imwrite(savefile, self.canvas.draw)
        self.canvas.after(100, self.canvas.redraw)
    
    def load(self):
        self.canvas.after_cancel(self.canvas.redraw_timer)
        self.update_idletasks()
        imfile = fd.askopenfilename()
        self.canvas.load_image(imfile)
        self.canvas.after(100, self.canvas.redraw) 
    
    def on_resize(self, event):
        r,c = self.canvas.imheight, self.canvas.imwidth
        h,w = self.winfo_height(), self.winfo_width()
        
        # determine new position and scale of canvas to maintain aspect ratio
        iswide = c/r > w/h
        self.cnvs_xscl = c*h/r if not iswide else w
        self.cnvs_yscl = r*w/c if iswide else h
        xoff = (w-self.cnvs_xscl)/2 if not iswide else 0
        yoff = (h-self.cnvs_yscl)/2 if iswide else 0
        
        self.canvas.configure_shape(xoff, yoff, self.cnvs_xscl, self.cnvs_yscl)
        


class RecursiveImageGenerator(tk.Canvas):
    def __init__(self, parent, bg="#000", width=640, height=480):
        
        # set up widget
        super().__init__(parent, bg=bg, width=width, height=height)
        self.bind("<Button-1>", self.on_mouseclick)
        self.bind("<B1-Motion>", self.on_mousemove)
        self.bind("<Motion>", self.on_mousemove)
        self.bind("<ButtonRelease-1>", self.on_mousedrop)
        
        # init instance vars
        self.imfile = None  # str - image file path
        self.image = None   # np img - unmodified image
        self.draw = None    # np img - modified image
        self.disp = None    # tk img - photoimage for tk
        
        self.imwidth, self.imheight = width, height
        self.realwidth, self.realheight = width, height
        self.mousex, self.mousey = 0, 0
        self.dirty = True  # whether drawing needs to be updated
        self.ready = False  # whether the parent is done setting up
        
        # init display elements
        self.poly = [(50,40),(70,40),(70,60),(50,60)]
        self.default_background()
        self.disp = self.to_tkimg(self.draw)
        self.create_image(0,0, anchor=tk.NW, image=self.disp, tag="img")
        self.redraw_window()
        
        self.topleft = self.create_oval(*self.poly[0], self.poly[0][0]-5, self.poly[0][1]-5,
                                        fill="#6fe", activefill="#0d0", tags=("poly", "topleft"))
        self.topright = self.create_oval(*self.poly[1], self.poly[1][0]+5, self.poly[1][1]-5,
                                        fill="#6fe", activefill="#0d0", tags=("poly", "topright"))
        self.botright = self.create_oval(*self.poly[2], self.poly[2][0]+5, self.poly[2][1]+5,
                                        fill="#6fe", activefill="#0d0", tags=("poly", "botright"))
        self.botleft = self.create_oval(*self.poly[3], self.poly[3][0]-5, self.poly[3][1]+5,
                                        fill="#6fe", activefill="#0d0", tags=("poly", "botleft"))
        self.corners = {self.topleft: 0, self.topright: 1, self.botright: 2, self.botleft: 3}
        self.selected = None
        
        self.after(100, self.redraw)
    
    def to_tkimg(self, img):
        img_cv2 = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_scl = cv2.resize(img_cv2, (int(self.realwidth), int(self.realheight)))
        img_pil = Image.fromarray(img_scl)
        img_tk = ImageTk.PhotoImage(image=img_pil)
        return img_tk
    
    def default_background(self):
        defaulttext = "Use File>Open to select an image to modify"
        (width, height), thick = cv2.getTextSize(defaulttext, cv2.FONT_HERSHEY_SIMPLEX, .5, 1)
        self.image = cv2.putText(np.full((480,640), (0,0,0), dtype=(np.uint8,3)),
                                defaulttext, (320-width//2,240-height//2), 
                                cv2.FONT_HERSHEY_SIMPLEX, .5, (100,100,100))
        self.draw = self.image.copy()
    
    def redraw_window(self):
        self.delete("window")
        self.create_polygon(*self.poly[0], *self.poly[1], *self.poly[2], *self.poly[3],
                            fill="#1c4", outline="#3e7",
                            outlinestipple="gray50", stipple="gray12", tag="window")
    
    def make_recursive_image(self, dst):
        self.draw = self.image.copy()
        
        r,c = self.imheight, self.imwidth
        src = np.array([(0,0),(c,0),(c,r),(0,r)])
        dst = np.array(dst)
        hom, _ = cv2.findHomography(src, dst)
        
        for i in range(4):
            warp = cv2.warpPerspective(self.draw, hom, (c,r), flags=cv2.INTER_LANCZOS4)
            cutout = cv2.fillConvexPoly(self.draw, dst, [0,0,0])
            self.draw = cv2.bitwise_or(cutout, warp)
    
    def redraw(self):
        self.ready = True
        if self.dirty:
            self.make_recursive_image(self.poly)
        self.disp = self.to_tkimg(self.draw)
        self.itemconfig("img", image=self.disp)
        self.redraw_timer = self.after(100, self.redraw) 
    
    def load_image(self, imfile):
        self.imfile = imfile
        self.image = cv2.imread(self.imfile)
        self.imheight, self.imwidth = self.image.shape[:2]
        self.dirty = True
    
    def on_mouseclick(self, event):
        x,y = event.x, event.y
        touch = self.find_overlapping(x-3, y-3, x+3, y+3)
        if self.topleft in touch:
            self.selected = self.topleft
        if self.topright in touch:
            self.selected = self.topright
        if self.botright in touch:
            self.selected = self.botright
        if self.botleft in touch:
            self.selected = self.botleft
    
    def on_mousemove(self, event):
        dx,dy = event.x - self.mousex, event.y - self.mousey
        self.mousex, self.mousey = event.x, event.y
        if self.selected is not None:
            x1,y1,x2,y2 = self.bbox(self.selected)
            corner = self.corners[self.selected]
            self.poly[corner] = ((x1+x2)//2, (y1+y2)//2)
            self.move(self.selected, dx, dy)
            self.redraw_window()
            self.dirty = True
    
    def on_mousedrop(self, event):
        self.selected = None
    
    def configure_shape(self, x, y, w, h):
        if not self.ready:
            return
        rw, rh = self.realwidth, self.realheight
        
        self.place(x=x,y=y,width=w,height=h)
        self.scale("window", 0, 0, w/rw, h/rh)
        self.scale("poly", 0, 0, w/rw, h/rh)
        self.poly = [(int(x*w/rw), int(y*h/rh)) for (x,y) in self.poly]
        self.realwidth, self.realheight = w, h

if __name__=="__main__":
    Interact()

