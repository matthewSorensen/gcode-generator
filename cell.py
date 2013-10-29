from shapely.geometry import LineString, MultiLineString, LinearRing, Polygon

from math import sqrt
import numpy as np
from numpy.linalg import norm
import visualize

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

def to_visual(gen):
    for seg in gen:
        yield list((p[0],p[1], 0)       for p in seg.coords)


def arbitrary_bounding_box(start,end, coords, big):
    start = np.array(start)
    end = np.array(end)

    ihat = end - start
    ihat = ihat * 1 / norm(ihat)
    jhat = np.array([-1 * ihat[1], ihat[0]]) # ccw 90 degree rotation, defining the rest of our coordinate system

    xbounds, ybounds = (0,0),(0,0)

    for point in coords:
        disp = np.array(point) - start
        xc = np.dot(ihat,disp)
        yc = np.dot(jhat,disp)
        
        xbounds = (min(xbounds[0], xc), max(xbounds[1], xc))
        ybounds = (min(ybounds[0], yc), max(ybounds[1], yc))
 
    low = start + xbounds[0] * ihat
    high = end + max(0, xbounds[1] - np.dot(ihat, end)) * ihat
    lower = start + (xbounds[0] - big) * ihat
    higher = end + max(0, big + xbounds[1] - np.dot(ihat, end)) * ihat
    
#    box = [lower, low, low - big * jhat, high - big * jhat, high, higher, higher + big * jhat, lower + big * jhat]
#    box = [ lower, low, low - big * jhat, high - big * jhat, high + big * jhat, low + big* jhat]


    # meh, we need to partition all of the region into non-intersecting subregions - don't need complete coverage, but
    # we do need complete coverage of the areas we haven't covered.
    return box

class Cell:

    def __init__(self, region, bound, start, offset):
        self.region = region # closed polygonal region
        self.bound = bound   # segment of polygonal region
        self.start = start   # initial part (or, in order of cutting, last)
        self.offset = offset

        self.paths = []
        self.subregions = []

    def construct(self):
        last = self.start        


        bounds = self.region.bounds
        size = sqrt(pow(bounds[2]-bounds[0],2)+pow(bounds[3]-bounds[1],2))

        while True:
            self.paths.append(last)
            last = self.offset(last,size)

            if last.is_empty:
                return

            inside = self.region.intersection(last)
          
            if inside.is_empty:
                return

            if type(inside) == MultiLineString:
                for line in inside:

                    p = arbitrary_bounding_box(line.coords[0],line.coords[-1],line.coords, 100)

                 #   visualize.show_paths(to_visual([LinearRing(p)]))
                    
                    box = Polygon(p)

                    region = self.region.intersection(box) 
                    if region.is_empty:
                        continue

                    sub = Cell(region,box.intersection(self.bound),line, self.offset)
                    sub.construct()
                    self.subregions.append(sub)
                return

            last = inside
        return None

    def emit(self):
        for sub in self.subregions:
            for seg in sub.emit():
                yield seg

        for seg in self.paths:
            yield seg

def offsetting(obj,size):
    off = obj.parallel_offset(1,'left', join_style = 2)
    if off.is_empty:
        return off


    if type(off) == LinearRing:
        return off

    # take the first and last line segments, and make them very long
    copy = list(off.coords)

    copy[0] = extend(copy[0], copy[1], size)
    copy[-1] = extend(copy[-1], copy[-2], size)
    return LineString(copy)
