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

def linear_comb(x,y,zx,zy):
    t = zy / (zy - zx)
    return t * x + (1-t) * y

def intersect_triangle_plane(triangle, normal, value, eps = 0.0001):
    zvalues = list(np.dot(v, normal) - value for v in triangle)
    signs = list(eps_sign(z, eps) for z in zvalues)
    sig = sum(signs)

    if np.prod(signs) == 0:
        is_convex = sig == 0 and not all(signs == 0)

        for i, z in enumerate(signs):
            if z == 0:
                yield tri[i]
                if is_convex:
                    j,k = (i+1) % 3, (i+2) % 3
                    yield linear_comb(tri[j],tri[k], zvalues[j], zvalues[k])

    elif abs(sig) == 1:
        for i, z in enumerate(signs):
            if z == -1 * sig:
                j,k = (i+1) % 3, (i+2) % 3
                yield linear_comb(triangle[j], triangle[i], zvalues[j], zvalues[i])
                yield linear_comb(triangle[k], triangle[i], zvalues[k], zvalues[i])
                break

def con(g):
    for h in g:
        for f in h:
            yield f

def triangles_containing(points, triangles, intervals, z):
    for i in intervals.overlap_point(z):
        a,b,c = triangles[intervals[i]]
        yield points[a], points[b], points[c]


def hull_on_plane(mesh, intervals, zval, zhat):
    points, triangles = mesh

    points = list(con(intersect_triangle_plane(tri, zhat, zval) for tri in triangles_containing(points,triangles, intervals,zval)))

    flat = np.zeros((len(points),2))
    for i, p in enumerate(points):
        flat[i][0] = p[0]
        flat[i][1] = p[1]

    return ConvexHull(flat, incremental = True)

# now for the fun part: generating contours from a convex polygon
