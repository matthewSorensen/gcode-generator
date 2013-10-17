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



#def position(normal, stream):
#    minima, maxima = 0,0
#    is_three_axis = True

 #   for face in stream:
  #      a,b,c = face[1:4]
   #     centroid = 0.33333 * (a+b+c)
        
    #    c = np.dot(normal, centroid)

     #   minima = min(minima, c)
      #  maxima = max(maxima, c)

       # if np.dot(normal, np.cross(a-b, c-b)) < -0.001:
            # this is actually a more complex test than Ganter thinks, once you take fixturing into account.
            # three axis test == all facets are either coplanar with reference plane, or n hat . plane hat > 0
       #     is_three_axis = False

#    return minima, maxima, is_three_axis

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

with open("test/part3.stl","rb") as f:
    facets = list(stl.read_stl(f))

normals = sample_normals(len(facets), facets)
clustered = DBSCAN(eps = 0.3, min_samples = 1).fit(normals)
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
