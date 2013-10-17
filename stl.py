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

# Binary STL formats begin with an 80-character header, which is followed bin a 32-bit unsigned integer,
# containing the number of triangles in the file.
header_format = struct.Struct('80bi')
# Each of the triangle is composed of a normal vector, three points, and a 16-bit metadata element.
# All vectors are 3-tuples of 32-bit floats. 
facet_format  = struct.Struct('12fh')

def read_stl(stream, chunk = 256):
    # Read and parse a header.
    # However, the length field is ignored, because length fields are a generally bad idea.
    buf = stream.read(header_format.size)
    h = header_format.unpack_from(buf)

    buf = stream.read(chunk * facet_format.size)
    while buf != '':
        index = 0
        while index < len(buf):
            f = facet_format.unpack_from(buf,index)
            # gives the facet normal, point 1 - 3, and the metadata
            normal = np.array(f[0:3])
            a = np.array(f[3:6])
            b = np.array(f[6:9])
            c = np.array(f[9:12])

            yield normal, a, b, c, f[12]

            index += facet_format.size
        buf = stream.read(chunk * facet_format.size)

def pack_triangle(normal,t):
    flat = 13 * [0]
    flat[0] = normal[0]
    flat[1] = normal[1]
    flat[2] = normal[2]

    i = 3
    for a,b,c in t:
        flat[i] = a
        flat[i+1] = b
        flat[i+2] = c
        i += 3

    return flat

def write_stl(triangles, stream, seekable = True, n = 0):
    """ 
    Writes a binary stl to a stream. If we can't seek on the stream, 
    the number of facets in the file must be explicitly provided by the caller.
    """

    stream.write(header_format.pack(*(80*[0]+[n])))
    count = 0

    for tri, normal in triangles:
        count += 1

        order_norm = np.cross(tri[0]-tri[1],tri[2]-tri[1])
        if np.dot(order_norm, normal) < 0:
            tri.reverse()
  
        s = facet_format.pack(*pack_triangle([0,0,0], tri))
        stream.write(s)

    if seekable:
        stream.seek(0)
        stream.write(header_format.pack(*(80*[0]+[count])))

    return count
