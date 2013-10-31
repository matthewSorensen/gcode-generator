from shapely.geometry import LinearRing, LineString, MultiLineString
from math import sqrt

def euclidean(x,y):
    return sqrt(pow(x[0]-y[0],2)+pow(x[1]-y[1],2))


def closed_linear_ring(coord):
    if coord[0] != coord[-1]:
        coord.append(coord[0])
    return LinearRing(coord)


def best_closure(seg, can, eps = 0.001):
    start = seg.coords[0]
    end = seg.coords[-1]
    existing = list(seg.coords)
    
    for c in can:
        if eps > euclidean(start, c.coords[0]) and eps > euclidean(end, c.coords[-1]):
            new = list(c.coords)
            new.reverse()
            return closed_linear_ring(existing[1:]+new[1:])

        if eps > euclidean(start, c.coords[-1]) and eps > euclidean(end, c.coords[0]):
            new = list(c.coords)
            return closed_linear_ring(existing[1:]+new[1:])

    return LineString()

def merge_adjacent(acc, seg):
    eps = 0.0001

    if acc == []:
        return [list(seg.coords)]

    last = acc[-1]
    a, b = last[0], last[-1]
    c, d = seg.coords[0], seg.coords[-1]
    
    if eps > euclidean(b,c):
        last.append(list(seg.coords)[1:])
    elif eps > euclidean(a,d):
        new = list(seg.coords) + last[1:]
        acc[-1] = new
    else:
        acc[-1] = LineString(last)
        acc.append(list(seg.coords))
    return acc

def intersect(polygon,curve):
    result = polygon.intersection(curve)
    if result.is_empty:
        return []
    if type(result) == MultiLineString:
        if type(curve) == LinearRing:
            merged = reduce(merge_adjacent, result, [])
            merged[-1] = LineString(merged[-1])
            return merged
        return list(result)              
    else:
        return [result]



    # if curve is a single curve, we're all good
    # otherwise, if curve is a linear ring, and the intersection yields a MultiLine string, we may have to carefully repair it
