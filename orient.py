import numpy as np
from numpy.linalg import norm
from mayavi import mlab
from sklearn.cluster import DBSCAN
import random

import stl
import visualize

def sample_triangles(tri,n):

    # figure out some way to weight triangle size
    # also, switch to calculating all of the triangle normals at once, and passing them everywhere

    if len(tri) < n:
        return tri

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

    clusters = DBSCAN(eps = 0.1, min_samples = cluster).fit(normals)

    candidates = dict()

    for i, group in enumerate(clusters.labels_):
        if group == -1:
            continue

        orientation = candidates.get(group)
        normal = normals[i]
        if orientation is None:
            candidates[group] = [1, normal, normal, normal] # list, so it is mutable
        else:
            orientation[0] = orientation[0] + 1
            orientation[1] = orientation[1] + normal
            orientation[2] = np.minimum(orientation[2], normal)
            orientation[3] = np.maximum(orientation[3], normal)
            # we actually really want the total area of the cluster as well, assuming our sample is evenly distributed over area.
    candidates = [(can[0], can[1], norm(can[3]-can[2]))for i, can in candidates.items()]    
    # we can now sort by the cluster spread and size, so that we test more probable solutions first, and terminate faster
    for candidate in sorted(candidates, key = lambda x : (x[2], -1 * x[0])):
        normal = -1 * candidate[1] / float(candidate[0])
        works, start = position(normal, 0.01, 0.01, triangles)
        if works:
            print normal, "is a valid part orientation, starting at", start


with open("test/test.stl","rb") as f:
    gen = stl.read_stl(f)
    length = next(gen)
    orient_part(map(stl.points,gen), 1000, 2)
    mlab.show()
    
