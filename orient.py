import numpy as np
from numpy.linalg import norm
from mayavi import mlab
from sklearn.cluster import DBSCAN
import random

import stl
import visualize

def sample_triangles(tri,n):
    result = n*[None]
    i = 0

    prob = float(n) / float(len(tri))
    for t in tri:
        if random.random() <= prob:
            result[i] = t
            i += 1
            if n <= i:
                break
    return result[0:i]
    
def pack_normals(triangles):
    normals = np.zeros((len(triangles),3))
    i = 0

    for face in triangles:
        m = np.cross(face[0]-face[1],face[2]-face[1])
        m = m / norm(m)
        
        normals[i][0] = m[0]
        normals[i][1] = m[1]
        normals[i][2] = m[2]

        i += 1
      
    return normals


def position(normal, angle_eps, position_eps, stream):
    minima = None
    
    for a,b,c in stream:
        face_normal = np.cross(a-b,c-b)
        face_normal = face_normal/norm(face_normal)
        cosine = np.dot(normal, face_normal) 
        
        if cosine < 0:
            if cosine < (-1 + angle_eps):
                position = np.dot(normal, 0.333333 * (a+b+c))
                if minima is None:
                    minima = position
                elif abs(minima - position) > position_eps:
                    return False, minima
            else:
                return False, minima
    return True, minima

def orient_part(triangles, nsamples, cluster):
    triangles = list(triangles)
    samples = sample_triangles(triangles, nsamples)
    normals = pack_normals(samples)


    visualize.show_triangles(triangles, color = (0.3,0.3,0.3))
    visualize.show_triangles(samples)

    clusters = DBSCAN(eps = 0.3, min_samples = cluster).fit(normals)

    candidates = dict()

    for i, group in enumerate(clusters.labels_):
        vector = candidates.get(group)
        if vector is None:    # if we're being smart, we should sort this by count, area, and divergence in the group
            candidates[group] = normals[i]

    for i, vector in candidates.items():
        works, start = position(-1 * vector, 0.1, 0.1, triangles)
        if works:
            print vector, "is a valid part orientation"

with open("test/test.stl","rb") as f:
    gen = stl.read_stl(f)
    length = next(gen)
    orient_part(map(stl.points,gen), 1000, 2)

    mlab.show()
    


