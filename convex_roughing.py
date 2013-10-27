import numpy as np
import banyan 

from scipy.spatial import ConvexHull


def construct_intervals(mesh, zhat):
    points, triangles = mesh

    intervals = banyan.SortedDict([], key_type = (float,float), updator = banyan.OverlappingIntervalsUpdator)

    for i, tri in enumerate(triangles):
        a,b,c = tri
        z = [np.dot(zhat, points[a]),np.dot(zhat, points[b]),np.dot(zhat, points[c])]
        intervals[(min(z),max(z))] = i

    return intervals

def eps_sign(x,e): 
    """ Sign of a number, with a given tolerance for equality to zero """ 
    if abs(x) <= e:
        return 0
    elif x < 0:
        return -1
    else:
        return 1

def linear_comb(points,heights):
    t = heights[1] / (heights[1] - heights[0])
    return t * points[0] + (1-t) * points[1]
                  
def points_on_plane(tri, zval, zhat, eps = 0.0001):
    a,b,c = tri
    za = np.dot(a, zhat) - zval
    zb = np.dot(b, zhat) - zval
    zc = np.dot(c, zhat) - zval

    signs = np.array([eps_sign(za, eps), eps_sign(zb, eps), eps_sign(zc, eps)])
    sig = sum(signs)

    if np.prod(signs) == 0: # degenerate cases with one or more points on the plane
            # all zeros are intersections, by definition:
        if signs[0] == 0:
            yield a 
        if signs[1] == 0:
            yield b 
        if signs[2] == 0:
            yield c

        if sig == 0 and not all(signs == 0): # one zero, and a convex combination of the other two
            for i, z in enumerate(signs):
                if z == 0: #solve for the convex combination that works
                    yield linear_comb([[b,c],[a,c],[a,b]][i],[[zb,xc],[za,zc],[za,zb]][i])
                    break 
    elif abs(sig) == 1: # sig can't be zero or two, becase three of -1 or 1 must sum to absolute value of 3 or 1
        for i, z in enumerate(signs):
            if z == -1 * sig: # odd one out - [-1,-1,1] sums to -1, 1 is odd one, etc
                this = [[a,za],[b,zb],[c,zc]][i]
                others = [[b,c],[a,c],[a,b]][i]
                othersh = [[zb,zc],[za,zc],[za,zb]][i]

                yield linear_comb([others[0],this[0]],[othersh[0], this[1]])
                yield linear_comb([others[1],this[0]],[othersh[1], this[1]])

                break

def con(g):
    for h in g:
        for f in h:
            yield f

def comp(points,triangles,interval,i):
    a,b,c = triangles[interval[i]]
    return (points[a],points[b], points[c])

def hull_on_plane(mesh, intervals, zval, zhat):
    points, triangles = mesh

    points = list(con(points_on_plane(comp(points,triangles,intervals,i),zval,zhat) for i in intervals.overlap_point(zval)))
 
    flat = np.zeros((len(points),2))
    for i, p in enumerate(points):
        flat[i][0] = p[0]
        flat[i][1] = p[1]

    return ConvexHull(flat, incremental = True)
