class Emitter:
    def __init__(self, stream, **config):
        default = dict(number_lines = False, 
                       integer_format = "{}", 
                       floating_format = "{0:f}", 
                       line_ending = '\n',
                       program_number = None)
        default.update(config)
        self.configuration = default
        self.stream = stream
        self.position = [None,None,None]
        self.count = 1

    def __enter__(self):
        number = self.configuration['program_number']
        if not number is None:
            self.stream.write('O' + number + self.configuration['line_ending'])
        return self

    def __exit__(self, *ignore):
        self.emit('M30')
        
    def at(self,coords):
        self.position = coords

    def emit(self, *args):
        s = self.stream
        if self.configuration['number_lines']:
            s.write('N')
            s.write(str(self.count))
            s.write(' ')
        for register in args:
            if register is None:
                continue
            if isinstance(register, str):
                s.write(register)
                s.write(' ')
                continue
            axis, value = register
            formatter = self.configuration['integer_format' if isinstance(value, int) else 'floating_format']
            s.write(str(axis))
            s.write(formatter.format(value))
            s.write(' ')
        s.write(self.configuration['line_ending'])
        self.count += 1


    def go(self, x, y, z, feed = None, rapid = False):
        nx, ny, nz = None, None, None

        if (not x is None) and x != self.position[0]:
            self.position[0] = x
            nx = ('X', x)

        if (not y is None) and y != self.position[1]:
            self.position[1] = y
            ny = ('Y', y)

        if (not z is None) and z != self.position[2]:
            self.position[2] = z
            nz = ('Z', z)

        if not feed is None:
            feed = ('F', feed)
            
        self.emit('G01' if not rapid else 'G00', nx, ny, nz, feed)

