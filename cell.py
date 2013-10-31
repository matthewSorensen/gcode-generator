from shapely.geometry import LineString, MultiLineString, LinearRing, Polygon
from shapely.ops import linemerge, polygonize
from math import sqrt
import numpy as np
from numpy.linalg import norm
import shapely_utils
import visualize
from shapely.validation import explain_validity

def extend(tip, first, length):
    tip = np.array(tip)
    first = np.array(first)
    direction = tip - first
    
    tip = first + (length / norm(direction)) * direction
    return (tip[0], tip[1])


def extend_line(line, length):

    points = list(line.coords)
    points[0] = extend(points[0],points[1],length)
    points[-1] = extend(points[-1],points[-2],length)

    return points

i = 0

def to_visual(gen):
    global i
    i -= 10
    for seg in gen:
        yield list((p[0],p[1], i) for p in seg.coords)

def dist(a,b):
    return sqrt(pow(a[0]-b[0],2)+ pow(a[1]-b[1],2))


def new_bound(linear_ring, line, big):    

    start = np.array(line.coords[0])
    end = np.array(line.coords[-1])

    ihat = end - start
    ihat = ihat * 1 / norm(ihat)
    jhat = np.array([-1 * ihat[1], ihat[0]]) # ccw 90 degree rotation, defining the rest of our coordinate system

    low = start - big * ihat
    high = start + big * ihat

    box = Polygon([low, high, high + big * jhat, low + big * jhat]) # half-plane!
    new = shapely_utils.intersect(box, linear_ring)


    #visualize.show_paths(to_visual([line]))
    visualize.show_paths(to_visual(new))
    

    return shapely_utils.best_closure(line, new)

#    if type(new) == MultiLineString:
 #       return shapely_utils.best_closure(line, new)

#    visualize.show_paths(to_visual([line]))
 #   visualize.show_paths(to_visual([linear_ring]))

  #  return shapely_utils.best_closure(line, [new])


class Cell:

    def __init__(self, region, bound, start, offset):
        self.region = region # closed polygonal region
        self.bound = bound   # segment of polygonal region
        self.start = start   # initial part (or, in order of cutting, last)
        self.offset = offset

        self.paths = []
        self.subregions = []

    def construct(self):

        global i

        last = self.start        

        bounds = self.region.bounds
        size = sqrt(pow(bounds[2]-bounds[0],2)+pow(bounds[3]-bounds[1],2))

        region = Polygon(self.region.coords)
        if not region.is_valid:
            visualize.show_paths(to_visual([self.region]),color = (1,0,0))
            print explain_validity(region)
            return
        while True:
            self.paths.append(last)
            last = self.offset(last,size)
            if last.is_empty:
                return

            inside = shapely_utils.intersect(region, last)

            if len(inside) == 0:
                return
            if len(inside) > 1:
                
                i -= 20
                for line in inside:
                    p = new_bound(self.region, line, size)
                    if p.is_empty:
                        print "wtf bad case is bad"
                        continue

                    sub = Cell(p, None, line, self.offset)
        
                    sub.construct()
                    self.subregions.append(sub)

            last = inside[0]

        return None

    def emit(self):
        for sub in self.subregions:
            for seg in sub.emit():
                yield seg

        for seg in self.paths:
            yield seg

def offsetting(obj,size):
    off = obj.parallel_offset(2,'left', join_style = 3)
    if off.is_empty:
        return off

    if type(obj) == LinearRing and type(off) == LineString:
        return shapely_utils.closed_linear_ring(list(off.coords))

    # take the first and last line segments, and make them very long
    copy = list(off.coords)

    copy[0] = extend(copy[0], copy[1], size)
    copy[-1] = extend(copy[-1], copy[-2], size)
    return LineString(copy)
