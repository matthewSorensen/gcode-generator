import numpy as np
from mayavi.mlab import *

def threetuple(nump):
    return (nump[0], nump[1], nump[2])

def deduplicate_vertices(triangles):
    i = 0
    tri = dict()
    for a,b,c in triangles:
        a = threetuple(a)
        b = threetuple(b)
        c = threetuple(c)
        ai = tri.get(a)
        bi = tri.get(b)
        ci = tri.get(c)
        if ai is None:
            ai = tri[a] = i
            i += 1
        if bi is None:
            bi = tri[b] = i
            i += 1
        if ci is None:
            ci = tri[c] = i
            i += 1
        yield (ai,bi,ci)
    yield i, tri

def points_and_connect(triangles):
    tris = list(deduplicate_vertices(triangles))
    i, verts = tris[-1]
    del tris[-1]

    points = np.zeros((3, i))
    for point, index in verts.iteritems():
        points[0][index] = point[0]
        points[1][index] = point[1]
        points[2][index] = point[2]
    return points, tris


def show_triangles(triangles, color = False):
    vert, tri = points_and_connect(triangles)
    if color:
        triangular_mesh(vert[0], vert[1], vert[2], tri, color = color)
    else:
        triangular_mesh(vert[0], vert[1], vert[2], tri)
    
