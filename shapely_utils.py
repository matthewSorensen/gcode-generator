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

def cut_ring(line, start, end, eps = 0.0000001):
    j = None
    for index, p in enumerate(line.coords):
        last = line.coords[index - 1]
        if abs(euclidean(start,last)+euclidean(start,p) - euclidean(last,p)) < eps:
            j = index 
            break
    
    if j is None:
        return None
    
    for index, p in enumerate(line.coords[j:]):
        last = line.coords[index + j - 1]
        if abs(euclidean(end,last)+euclidean(end,p) - euclidean(last,p)) < eps:
            return LineString([start] + line.coords[j:(index+j)] + [end])

    for index, p in enumerate(line.coords[0:j]):
        last = line.coords[index - 1]
        if abs(euclidean(end,last)+euclidean(end,p) - euclidean(last,p)) < eps:
            return LineString([start] + line.coords[j:] + line.coords[0:index] + [end])
    
    return None


def cut_line(line, start, end, eps = 0.000001):
    j,k = None, None
    for index, p in enumerate(line.coords[1:]):
        last = line.coords[index]
        seg = euclidean(last,p)
        if abs(euclidean(start,last) + euclidean(start,p) - seg) < eps:
            j = index + 1
        if abs(euclidean(end,last) + euclidean(end,p) - seg) < eps:
            k = index + 1
        if (not j is None) and (not k is None):
            if j <= k:
                return LineString([start] + line.coords[j:k] + [end])
            else:
                l = [end] + line.coords[k:j] + [start]
                l.reverse()
                return LineString(l)

    return None




    




    
    

