import mayavi.mlab as mlab
import numpy as np

def show_paths(gen):
    for seg in gen:
        seg = list(seg)
        points = np.zeros((3,len(seg)))
        i = 0
        for p in seg:
            points[0][i] = p[0]
            points[1][i] = p[1]
            points[2][i] = p[2]
            i += 1
        mlab.plot3d(points[0],points[1],points[2], tube_radius = None)

def show_matrix(mat):
    mlab.surf(mat)
    
def show_mesh(points, triangles):
    mlab.triangular_mesh(points[...,0],points[...,1],points[...,2], triangles)

def show():
    mlab.show()
