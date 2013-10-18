import stl
import numpy as np
from numpy.linalg import norm
from mayavi import mlab
from sklearn.cluster import DBSCAN


def sample_normals(n, stream):
    """ This does a horrible job of actually sampling the normals """
    normals = np.zeros((n,3))
    i = 0
    for face in stream:
        m = np.cross(face[1]-face[2],face[3]-face[2])
        m = m / norm(m)
        
        normals[i][0] = m[0]
        normals[i][1] = m[1]
        normals[i][2] = m[2]

        i += 1
        if i >= n:
            break
    return normals


def position(normal, angle_eps, position_eps, stream):
    minima = None
    
    for face in stream:
        a,b,c = face[1:4]
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


facets = None
length = 0

with open("test/part3.stl","rb") as f:
    gen = stl.read_stl(f)
    length = next(gen)
    facets = list(gen)

print length

normals = sample_normals(len(facets), facets) # choosing the number of samples
clustered = DBSCAN(eps = 0.3, min_samples = 1).fit(normals) # and min samples per cluster are key to getting this to work
labels = clustered.labels_

candidates = dict()
for i, group in enumerate(labels):
    vector = candidates.get(group)

    if vector is None:
        # if we're being smart, we should sort this by count, area, and divergence in the group
        candidates[group] = normals[i]
    
for i,vector in candidates.items():
    works, start = position(-1 * vector, 0.1, 0.1, facets)
    if works:
        print vector, "is a valid part orientation"
