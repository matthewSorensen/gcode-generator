# load an stl file into a dumb bag of triangles.
# Alternately, load it into a slightly smarter bag of points + triangles
# raster it into an array of z-values
import io
import struct

def read_stl(stream, chunk = 1024):
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
            yield (f[0],f[1],f[2]),(f[3],f[4],f[5]),(f[6],f[7],f[8]),(f[9],f[10],f[11]),f[12]
            index += facet.size
        buf = stream.read(chunk * facet.size)
   
