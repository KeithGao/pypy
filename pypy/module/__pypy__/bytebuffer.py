#
# A convenient read-write buffer.  Located here for want of a better place.
#

from rpython.rlib.buffer import Buffer
from pypy.interpreter.gateway import unwrap_spec


class ByteBuffer(Buffer):
    _immutable_ = True

    def __init__(self, len):
        self.data = ['\x00'] * len
        self.readonly = False

    def getlength(self):
        return len(self.data)

    def getitem(self, index):
        return self.data[index]

    def setitem(self, index, char):
        self.data[index] = char


@unwrap_spec(length=int)
def bytebuffer(space, length):
    return space.newbuffer(ByteBuffer(length))
