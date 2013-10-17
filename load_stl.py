# load an stl file into a dumb bag of triangles.
# Alternately, load it into a slightly smarter bag of points + triangles
# raster it into an array of z-values
import io
import struct
import numpy as np

from math import floor, ceil

from stl import read_stl

ihat = np.array([1,0,0])
jhat = np.array([0,1,0])
khat = np.array([0,0,1])

def dot2(a,b):
    # all of our barycentric coordinate math requires work on two vectors,
    # but we want to keep the original vectors three-vectors
    return a[0]*b[0]+a[1]*b[1]

def raster_triangles(matrix, triangles, transformation = lambda(x): x):
    for normal, a, b, c, meta in triangles:
        a = transformation(a)
        b = transformation(b)
        c = transformation(c)

        # pick some direction; identify the interval we need to raster upon  
        y = [np.dot(jhat,a),np.dot(jhat,b),np.dot(jhat,c)]
        yinterval = int(floor(min(y))), int(ceil(max(y)) + 1)
        # pick a second direction, indentify that interval
        x = [np.dot(ihat,a),np.dot(ihat,b),np.dot(ihat,c)]
        xinterval = int(floor(min(x))), int(ceil(max(x)) + 1)

        v0 = c - a
        v1 = b - a
        dot00 = dot2(v0,v0)
        dot01 = dot2(v0,v1)
        dot11 = dot2(v1,v1)

        size = dot00 * dot11 - dot01 * dot01
        if size == 0:
            continue

        # this does twice as much work as needed, but is rather simple
        for i in range(*xinterval):
            for j in range(*yinterval):
                v2 = np.array([i,j,0]) - a
               
                dot02 = dot2(v0,v2)
                dot12 = dot2(v1,v2)

                v = (dot00 * dot12 - dot01 * dot02) / size
                u = (dot11 * dot02 - dot01 * dot12) / size
                
                if (u >= 0) and (v >= 0) and (u + v <= 1):
                    matrix[i][j] = max(matrix[i][j], (1-u-v)*a[2]+v*b[2]+u*c[2]) # yay barycentric coordinates!


test = np.zeros((90,70))

with open("test/test.stl","rb") as f:
    raster_triangles(test, read_stl(f))

import matplotlib.pyplot as plt
plt.imshow(test)
plt.show()
