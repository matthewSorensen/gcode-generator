# Binary STL serializer and deserializer, extracted from code written
# for Washington Open Object Fabricators and UW ME409, Fall 2013.

# Copyright (c) 2013 Matthew D. Sorensen.
# All rights reserved.

# Redistribution and use in source and binary forms are permitted
# provided that the above copyright notice and this paragraph are
# duplicated in all such forms and that any documentation,
# advertising materials, and other materials related to such
# distribution and use acknowledge that the software was developed
# by Matthew D. Sorensen.  The name of Matthew D. Sorensen
# may not be used to endorse or promote products derived
# from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED ``AS IS'' AND WITHOUT ANY EXPRESS OR
# IMPLIED WARRANTIES, INCLUDING, WITHOUT LIMITATION, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.

import struct
import io
import numpy as np

def read_stl(stream, chunk = 256):
    # The stl standard is an 80-character header, followed by a 32-bit uint containing the number of triangles
    # Each triangle is composed of a normal vector, three points, and a 16-bit metadata element.    
    header = struct.Struct('80bi')
    facet  = struct.Struct('12fh')
    # Read and parse a header.
    # However, the length field is ignored, because length fields are a generally bad idea.
    buf = stream.read(header.size)
    h = header.unpack_from(buf)

    buf = stream.read(chunk * facet.size)
    while buf != '':
        index = 0
        while index < len(buf):
            f = facet.unpack_from(buf,index)
            # gives the facet normal, point 1 - 3, and the metadata
            normal = np.array([f[0],f[1],f[2]])
            a = np.array([f[3],f[4],f[5]])
            b = np.array([f[6],f[7],f[8]])
            c = np.array([f[9],f[10],f[11]])

            yield normal, a, b, c, f[12]

            index += facet.size
        buf = stream.read(chunk * facet.size)


def header(n,stream):
    h = struct.pack("80Bi",*(80*[0]+[n]))
    stream.write(h)
    
def order_vertex(points,normal):
    n = np.cross(points[0]-points[1],points[2]-points[1])
    if np.dot(n, normal) < 0:
        points.reverse()
    return points

def flat_tri(t):
    coords = 9*[0]
    i = 0
    for a,b,c in t:
        coords[i] = a
        coords[i+1] = b
        coords[i+2] = c
        i += 3
    return coords

def stream_binary_stl(n, triangles, stream):
    header(n,stream)
    fmt = struct.Struct("12fh")

    for tri, norm in triangles:
        ordered = order_vertex(tri,norm)
        s = fmt.pack(*([0,0,0]+flat_tri(ordered)+[0]))
        stream.write(s)
    return None

def binary_stl(triangles, stream):
    header(0, stream)
    fmt = struct.Struct("12fh")
    count = 0

    for tri, norm in triangles:
        count += 1
        ordered = order_vertex(tri,norm)
        s = fmt.pack(*([0,0,0]+flat_tri(ordered)+[0]))
        stream.write(s)
        
    stream.seek(0)
    header(count, stream)
    return count
