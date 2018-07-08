from matplotlib import pyplot as plt

class Polygon:
    def __init__(self, pts=None):
        if pts is None:
            pts = [[],[]]
        self.xpts = [p[0] for p in pts]
        self.ypts = [p[1] for p in pts]
    
    def add(self, x, y):
        self.xpts.append(x)
        self.ypts.append(y)
    
    def __setitem__(self, i, pt):
        self.xpts[i] = pt[0]
        self.ypts[i] = pt[1]
    
    def __getitem__(self, i):
        return self.xpts[i], self.ypts[i]
    
    def __len__(self):
        return len(self.xpts)
    
    def move(self, i, dx, dy):
        self.xpts[i] += dx
        self.ypts[i] += dy
    
    def scale(self, mx, my):
        for i in range(len(xpts)):
            self.xpts[i] *= mx
            self.ypts[i] *= my
    
    def select(self, x, y, r):
        min_i, min_d = 0, sys.maxsize
        for i, (h,k) in enumerate(zip(xpts, ypts)):
            if abs(h-x) > r or abs(k-y) > r:
                continue
            d = (h-x)**2 + (k-y)**2
            if d <= r*r:
                min_d = d
                min_i = i
        return i if d < sys.maxsize else None
    
    NUM_INTERP_SEGS = 10
    def render(self, corner="sharp"):        
        if corner == "sharp":
            return Polygon.flatten(self.xpts, self.ypts)
        
        elif corner == "bezier":
            pts = []
            numsegs = (len(self.xpts)+1)*Polygon.NUM_INTERP_SEGS
            for segment in range(numsegs+1):
                t = segment/numsegs
                pts.append(Polygon.bezier(self.xpts, t))    # add an xvalue
                pts.append(Polygon.bezier(self.ypts, t))    # and its yvalue
            return pts
        
        elif corner == "hermite":
            return
        
        raise ValueError("Invalid corner type: %s" % corner)
    
    @staticmethod
    def flatten(x, y):
        return [j for i in zip(x, y) for j in i]


    choose_mem = {}
    @staticmethod
    def choose(n,k):
        if (n,k) in Polygon.choose_mem:
            return Polygon.choose_mem[(n,k)]
        if 0 < k <= n:
            f = Polygon.choose(n-1, k-1) + Polygon.choose(n-1,k)
            Polygon.choose_mem[(n,k)] = f
            return f
        return int(not k)
    
    @staticmethod    
    def bezier(ctrl_pts, t):
        n = len(ctrl_pts)-1
        binomial = [Polygon.choose(n,i) for i in range(n+1)]
        bernstein = [(t**i)*((1-t)**(n-i)) for i in range(n+1)]
        bezval = sum([binom*bern*pt for binom, bern, pt in zip(binomial, bernstein, ctrl_pts)])
        return bezval
    
    h_00 = lambda t: (1+2*t)*(1-t)**2
    h_01 = lambda t: t*(1-t)**2
    h_10 = lambda t: (3-2*t)*t**2
    h_11 = lambda t: (t-1)*t**2
    @staticmethod
    def hermite(p, x, k):
        return


if __name__=="__main__":
    p = Polygon([(1,1), (4,5), (7,6), (10,2)])
    
    x1, y1 = [], []
    for i, val in enumerate(p.render(corner="bezier")):
        if i % 2 == 0:
            x1.append(val)
        else:
            y1.append(val)
    
    x2, y2 = [], []
    for i, val in enumerate(p.render(corner="bezier")):
        if i % 2 == 0:
            x2.append(val)
        else:
            y2.append(val)
    
    x3, y3 = [], []
    for i, val in enumerate(p.render(corner="hermite")):
        if i % 2 == 0:
            x3.append(val)
        else:
            y3.append(val)
    
    plt.plot(x1, y1, color="r")
    plt.plot(x2, y2, color="g")
    plt.plot(x3, y3, color="b")
    plt.title("Bezier (red), Hermite (green), and Sharp (blue)")
    plt.show()
    
    
    

    



