# Binary STL serializer and deserializer, extracted from code written
# for Washington Open Object Fabricators and UW ME409, Fall 2013.

# Copyright (c) 2013 Matthew D. Sorensen.
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the <organization> nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL MATTHEW D SORENSEN BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import struct
import io

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

    yield h[80]

    buf = stream.read(chunk * facet_format.size)
    while buf != '':
        index = 0
        while index < len(buf):
            f = facet_format.unpack_from(buf,index)
            # gives the facet normal, point 1 - 3, and the metadata
            normal = np.array(f[0:3])
            a = tuple(f[3:6])
            b = tuple(f[6:9])
            c = tuple(f[9:12])

            yield normal, a, b, c, f[12]

            index += facet_format.size
        buf = stream.read(chunk * facet_format.size)

def points(vert):
    return vert[1:4]

def pack_triangle(normal,t, facet):
    facet[0] = normal[0]
    facet[1] = normal[1]
    facet[2] = normal[2]

    i = 3
    for a,b,c in t:
        facet[i] = a
        facet[i+1] = b
        facet[i+2] = c
        i += 3

def write_stl(triangles, stream, seekable = True, n = 0):
    """ 
    Writes a binary stl to a stream. If we can't seek on the stream, 
    the number of facets in the file must be explicitly provided by the caller.
    """

    stream.write(header_format.pack(*(80*[0]+[n])))
    count = 0

    facet = 13*[0]

    for tri, normal in triangles:
        count += 1

        order_norm = np.cross(tri[0]-tri[1],tri[2]-tri[1])
        if np.dot(order_norm, normal) < 0:
            tri.reverse()

        pack_triangle([0,0,0], tri, facet)
        s = facet_format.pack(*facet) 
        stream.write(s)

    if seekable:
        stream.seek(0)
        stream.write(header_format.pack(*(80*[0]+[count])))

    return count
