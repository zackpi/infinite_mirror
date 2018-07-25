class Polygon:
    """
    The Polygon class defines a construct for storing points in a polygon, as well as some helper functions for modifying its position and scaling
    """
    
    def __init__(self, pts=None):
        if pts is None:
            pts = [[],[]]
        self.xpts = [p[0] for p in pts]
        self.ypts = [p[1] for p in pts]
    
    def add(self, x, y):
        """
        adds the point (x,y) between this Polygon's (k-1)th and 0th elements
        """
        self.xpts.append(x)
        self.ypts.append(y)
    
    def __setitem__(self, i, pt):
        """
        directly modifies a given point in this Polygon
        """
        assert -i <= len(self.xpts), "Invalid index: " + str(i)
        assert i < len(self.xpts), "Invalid index: " + str(i) + " >= " + str(len(self.xpts))
        self.xpts[i] = pt[0]
        self.ypts[i] = pt[1]
    
    def __getitem__(self, i):
        """
        returns the i-th point in this Polygon
        """
        assert -i <= len(self.xpts), "Invalid index: " + str(i)
        assert i < len(self.xpts), "Invalid index: " + str(i) + " >= " + str(len(self.xpts))
        return self.xpts[i], self.ypts[i]
    
    def __len__(self):
        return len(self.xpts)
    
    def move(self, i, dx, dy):
        """
        moves the i-th point in this Polygon by dx in the x direction and dy in the y direction
        """
        assert -i <= len(self.xpts), "Invalid index: " + str(i)
        assert i < len(self.xpts), "Invalid index: " + str(i) + " >= " + str(len(self.xpts))
        self.xpts[i] += dx
        self.ypts[i] += dy
    
    def scale(self, mx, my):
        """
        scales this entire Polygon by a magnitude of mx in the x axis and my in the y axis
        """
        for i in range(len(xpts)):
            self.xpts[i] *= mx
            self.ypts[i] *= my
    
    def select(self, x, y, r):
        """
        returns the index of the point in this Polygon closest to (x,y) and within r units
        returns None if no such point exists
        """
        min_i, min_d = 0, sys.maxsize
        for i, (h,k) in enumerate(zip(xpts, ypts)):
            if abs(h-x) > r or abs(k-y) > r:
                continue
            d = (h-x)**2 + (k-y)**2
            if d <= r*r:
                min_d = d
                min_i = i
        return i if d < sys.maxsize else None
    
    NUM_INTERP_SEGS = 20
    def render(self, corner="sharp", flat=False):
        """
        returns an ordered list of the points in this Polygon using the given interp method
        
        available interpolation methods:
            sharp:      returns the control points of this Polygon
            bezier:     returns a bezier curve defined by this Polygon's control points
            hermite:    returns a cubic hermite spline through the control points
        """
                
        if corner == "sharp":
            return [self.xpts, self.ypts] if not flat else Polygon.flatten(self.xpts, self.ypts)
        
        elif corner == "bezier":
            x, y = [], []
            numsegs = (len(self.xpts)+1)*Polygon.NUM_INTERP_SEGS
            for segment in range(numsegs+1):
                t = segment/numsegs
                x.append(Polygon.bezier(self.xpts, t))
                y.append(Polygon.bezier(self.ypts, t))
            return [x,y] if not flat else Polygon.flatten(x,y)
        
        elif corner == "hermite":
            x, y = [], []
            for k in range(len(self.xpts)-1):
                for segment in range(Polygon.NUM_INTERP_SEGS+(k==len(self.xpts)-2)):
                    t_k = segment / Polygon.NUM_INTERP_SEGS
                    x.append(Polygon.hermite(self.xpts, t_k, k))
                    y.append(Polygon.hermite(self.ypts, t_k, k))
            return [x,y] if not flat else Polygon.flatten(x,y)
        
        raise ValueError("Invalid corner type: %s" % corner)
    
    @staticmethod
    def flatten(x, y):
        """ returns the flattened zipped list version of x,y """
        return [j for i in zip(x, y) for j in i]


    CHOOSE_MEM = {}
    @staticmethod
    def choose(n,k):
        if (n,k) in Polygon.CHOOSE_MEM:
            return Polygon.CHOOSE_MEM[(n,k)]
        if 0 < k <= n:
            f = Polygon.choose(n-1, k-1) + Polygon.choose(n-1,k)
            Polygon.CHOOSE_MEM[(n,k)] = f
            return f
        return int(not k)
    
    @staticmethod    
    def bezier(ctrl_pts, t):
        n = len(ctrl_pts)-1
        binomial = [Polygon.choose(n,i) for i in range(n+1)]
        bernstein = [(t**i)*((1-t)**(n-i)) for i in range(n+1)]
        bezval = sum([binom*bern*pt for binom, bern, pt in zip(binomial, bernstein, ctrl_pts)])
        return bezval
    
    HERM_00 = lambda t: (1+2*t)*(1-t)**2
    HERM_01 = lambda t: (3-2*t)*t**2
    HERM_10 = lambda t: t*(1-t)**2
    HERM_11 = lambda t: (t-1)*t**2
    @staticmethod
    def hermite(p, t_k, k):
        h_00 = Polygon.HERM_00(t_k)   # solve hermite basis functions
        h_01 = Polygon.HERM_01(t_k)   # for third-degree interpolation
        h_10 = Polygon.HERM_10(t_k)
        h_11 = Polygon.HERM_11(t_k)
        
        m_k0 = (p[k+1]-p[max(0, k-1)])/2    # use finite difference method for tangents
        m_k1 = (p[min(len(p)-1, k+2)]-p[k])/2
        
        hermval = h_00*p[k] + h_10*m_k0 + \
                h_01*p[k+1] + h_11*m_k1
        return hermval

if __name__=="__main__":
    from matplotlib import pyplot as plt
    
    # testing implementation of bezier and hermite splines for use in infmirror.py
    
    p = Polygon([(1,1), (2,5), (7,2), (12,3), (15, 7), (20, 4)])
    
    x1, y1 = p.render(corner="bezier", flat=False)
    x2, y2 = p.render(corner="hermite", flat=False)
    x3, y3 = p.render(corner="sharp", flat=False)
    
    plt.plot(x1, y1, color="r")
    plt.plot(x2, y2, color="g")
    plt.plot(x3, y3, color="b")
    plt.title("Bezier (red), Hermite (green), and Sharp (blue)")
    plt.show()
    
    
    

    



