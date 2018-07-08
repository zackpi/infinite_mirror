class Polygon:
    def __init__(self, pts=None):
        if pts is None:
            pts = [[],[]]
        self.xpts = pts[0]
        self.ypts = pts[1]
    
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
    
    def _flatten(x, y):
        return [j for i in zip(x, y) for j in i]
    
    def render(self, corner="sharp"):
        if corner == "sharp":
            return _flatten(self.xpts, self.ypts)
        
        elif corner == "bezier":
            return self.flattened_vertices()
        
        elif corner == "spline":
            return self.flattened_vertices()
        
        raise ValueError("Invalid corner type: %s" % corner)
