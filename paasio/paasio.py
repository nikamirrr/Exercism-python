import errno
import io
import os


class MeteredFile(io.BufferedRandom):
    """Implement using a subclassing model."""

    def __init__(self, *args, **kwargs):
        super.__init__(*args, **kwargs)
        self.__in_context = False
        self.__read_ops = 0
        self.__read_bytes = 0
        self.__write_ops = 0
        self.__write_bytes = 0

    def __enter__(self):
        self.__in_context = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__in_context = False
        return super().__exit__(exc_type, exc_val, exc_tb)

    def __iter__(self):
        super().seek(0)
        return self

    def __next__(self):
        self.__read_ops += 1
        line = super().readline()
        if len(line) == 0:
            raise StopIteration()
        self.__read_bytes += len(line)
        return line

    def read(self, size=-1):
        if self.__in_context:
            temp = super().read(size)
            self.__read_ops += 1
            self.__read_bytes += len(temp)
            return temp
        raise ValueError("I/O operation on closed file.")

    @property
    def read_bytes(self):
        return self.__read_bytes

    @property
    def read_ops(self):
        return self.__read_ops

    def write(self, b):
        if self.__in_context:
            temp = super().write(b)
            self.__write_ops += 1
            self.__write_bytes += temp
            return temp
        raise ValueError("I/O operation on closed file.")

    @property
    def write_bytes(self):
        return self.__write_bytes

    @property
    def write_ops(self):
        return self.__write_ops


class MeteredSocket:
    """Implement using a delegation model."""

    def __init__(self, socket):
        self.__socket = socket
        self.__in_context = False
        self.__recv_ops = 0
        self.__recv_bytes = 0
        self.__send_ops = 0
        self.__send_bytes = 0

    def __enter__(self):
        self.__in_context = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__in_context = False
        return self.__socket.__exit__(exc_type, exc_val, exc_tb)

    def recv(self, bufsize, flags=0):
        if self.__in_context:
            self.__recv_ops += 1
            temp = self.__socket.recv(bufsize, flags)
            self.__recv_bytes += len(temp)
            return temp
        else:
            raise OSError(os.strerror(errno.EBADF))

    @property
    def recv_bytes(self):
        return self.__recv_bytes

    @property
    def recv_ops(self):
        return self.__recv_ops

    def send(self, data, flags=0):
        if self.__in_context:
            self.__send_ops += 1
            temp = self.__socket.send(data, flags)
            self.__send_bytes += temp
            return temp
        else:
            raise OSError(os.strerror(errno.EBADF))

    @property
    def send_bytes(self):
        return self.__send_bytes

    @property
    def send_ops(self):
        return self.__send_ops
