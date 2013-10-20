import itertools
import numpy
import math

def unique_points(triangles):
    i = itertools.count(0)
    unique = dict()
    for a,b,c in triangles:
        ai = unique.get(a)
        bi = unique.get(b)
        ci = unique.get(c)
        if ai is None:
            ai = unique[a] = next(i)
        if bi is None:
            bi = unique[b] = next(i)
        if ci is None:
            ci = unique[c] = next(i)
        yield (ai, bi, ci)
    yield unique, next(i)

def triangles_to_mesh(triangles):
    force = list(unique_points(triangles))
    point_dict, n = force[-1]

    points = numpy.empty((3,n), dtype = float) 

    for point, i in point_dict.iteritems(): # this is a natural place to put a coordinate conversion 
        points[0][i] = point[0]
        points[1][i] = point[1]
        points[2][i] = point[2]

    return points, force[0:len(force)-1] 

def dot2(a,b):
    # all of our barycentric coordinate math requires work on two vectors,
    # but we want to keep the original vectors three-vectors
    return a[0]*b[0]+a[1]*b[1]

def raster_mesh(verts, tri, trans, matrix):
    trans = numpy.array([trans[0],trans[1],1]) # trans is a 2D scaling vector - expand to 3-space

    for a,b,c in tri:
        a = numpy.transpose(verts[...,a]) * trans
        b = numpy.transpose(verts[...,b]) * trans
        c = numpy.transpose(verts[...,c]) * trans

        # pick some direction; identify the interval we need to raster upon  
        y = [a[1],b[1],c[1]]
        yinterval = int(math.floor(min(y))), int(math.ceil(max(y)) + 1)
        # pick a second direction, indentify that interval
        x = [a[0],b[0],c[0]]
        xinterval = int(math.floor(min(x))), int(math.ceil(max(x)) + 1)

        v0 = c - a
        v1 = b - a
        dot00 = dot2(v0,v0)
        dot01 = dot2(v0,v1)
        dot11 = dot2(v1,v1)

        size = dot00 * dot11 - dot01 * dot01
        if size == 0:
            continue

        # this does twice as much work as needed, but is rather simple
        for i in xrange(*xinterval):
            for j in xrange(*yinterval):
                v2 = numpy.array([i,j,0]) - a
               
                dot02 = dot2(v0,v2)
                dot12 = dot2(v1,v2)

                v = (dot00 * dot12 - dot01 * dot02) / size
                u = (dot11 * dot02 - dot01 * dot12) / size
                
                if (u >= 0) and (v >= 0) and (u + v <= 1):
                    matrix[i][j] = max(matrix[i][j], (1-u-v)*a[2]+v*b[2]+u*c[2]) # yay barycentric coordinates!

