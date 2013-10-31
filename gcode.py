# most general overview of the entire process:
# * load a binary stl
#    (reorient it for machinability, convert into the machine's coordinate frame)
# * convert this into two forms:
#       1) set of points and a triangulation over their indexes (in machine coordinates)
#       2) a matrix of heights (in tool-width x sample density coordinates)
# * generate CEA HSM path to rough stock to the convex hull of the point set in 1
#    (because this is a convex hull, path is tool-radius independent and constant-angle is comparatively easy)
# * generate profiling code with Ganter's trivial algorithm
# * alternately, find pockets and other single-boundary regions, and use a slightly smarter roughing algorithm to rough them.

# Target machining process:
# - big roughing endmill at HSM-type feeds and speeds (flat end)
# - smaller roughing endmill at somewhat more conservative f/s (flat end)
# - profiling with a small ball endmill

import stl
import convert_mesh
import numpy
import convex_roughing
import visualize
import scipy.spatial as spatial
import numpy as np
from pylab import *
import cell
from shapely.ops import polygonize
import shapely.geometry as shape

z = 9

def to_visual(gen):
    for seg in gen:
        yield list((p[0],p[1], z)       for p in seg.coords)

gen = None
mesh = None 

with open("test/test.stl","rb") as f:
    gen = stl.read_stl(f)
    next(gen) # ignore the length
    mesh = convert_mesh.triangles_to_mesh(map(stl.points, gen))

zbuf = convex_roughing.construct_intervals(mesh,np.array([0,0,1]))
hull = convex_roughing.hull_on_plane(mesh, zbuf, z, np.array([0,0,1]))


points = list(hull.points[i] for i in hull.vertices)
points.append(points[0])

points.reverse()
polygon = shape.LinearRing(points)


region = shape.LinearRing([(-10,0),(100,0),(100,100),(-10,100)])

c = cell.Cell(region, region, polygon, cell.offsetting)

c.construct()

visualize.show_paths(to_visual(c.emit()))
visualize.show_paths(to_visual([shape.LinearRing([(0,0),(100,0),(100,100),(0,100)])]))

visualize.show_mesh(*mesh)
visualize.show()

