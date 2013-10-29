from shapely.geometry import LineString, MultiLineString, LinearRing, Polygon

from math import sqrt
import numpy as np
from numpy.linalg import norm

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
                    a,b,c,d = line.bounds
                    box = Polygon([(a,b),(c,b),(c,d),(a,d)])
                    region = box.intersection(self.region)
                    if region.is_empty:
                        continue

                    sub = Cell(region,box.intersection(self.bound),line, self.offset)
                    sub.construct()
                    self.subregions.append(sub)
                break

            last = inside
        return None

    def emit(self):
        for sub in self.subregions:
            for seg in sub.emit():
                yield seg

        for seg in self.paths:
            yield seg

def extend(tip, first, length):
    tip = np.array(tip)
    first = np.array(first)
    direction = tip - first
    
    tip = first + (length / norm(direction)) * direction
    return (tip[0], tip[1])

def offsetting(obj,size):
    off = obj.parallel_offset(1,'left')
    if off.is_empty:
        return off


    if type(off) == LinearRing:
        return off

    # take the first and last line segments, and make them very long
    copy = list(off.coords)

    copy[0] = extend(copy[0], copy[1], size)
    copy[-1] = extend(copy[-1], copy[-2], size)
    return LineString(copy)
