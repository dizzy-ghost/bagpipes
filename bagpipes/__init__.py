# Syncronous FIFO communication module
# Version 0.0.1 (2020.12.17) by Dmitry "Dizzy" Povarov

import os
import select
import sys
import tempfile
import base64


class bagpipe:

    """
    Named PIPES in a bag
    """

    def __init__(self, xid=0):
        self.tempdir = tempfile.mkdtemp()  # where to store pipes
        self.mode_in = os.O_RDONLY  # input pipe mode
        self.mode_out = os.O_SYNC | os.O_CREAT | os.O_RDWR  # output pipe mode
        self.id = xid

    def make_fifo_pair(self, prefix='worker'):

        """
        Creates temporary FIFO pair for communication with worker
        :param prefix: pipe name prefix
        :param x_id: worker ID
        :return: container object with FIFO descriptors and file names

        Note: Pipes for main and worker ends should be reversed
            pipes.in_file is input for main and output for worker
            pipes.out_file is output for main and input for worker
        """

        # Prepare named FIFOs

        pipe_in = os.path.join(self.tempdir, f'{prefix}_{self.id}_in')
        pipe_out = os.path.join(self.tempdir, f'{prefix}_{self.id}_out')

        for fifo_pair in ((pipe_in, self.mode_in), (pipe_out, self.mode_out)):

            fifo_path, fifo_mode = fifo_pair

            if os.path.exists(fifo_path):
                # Remove existing pipes
                os.remove(fifo_path)
            try:
                # Create new ones
                os.mkfifo(fifo_path)
                fd = os.open(fifo_path, fifo_mode | os.O_NONBLOCK)
            except:
                #traceback.print_exc()
                print(f"Error: Cannot create fifo {fifo_path}, exiting")
                return False

            if fifo_mode == self.mode_in:
                self.in_file = fifo_path
                self.in_fd = fd
            else:
                self.out_file = fifo_path
                self.out_fd = fd

        return True

    def open_fifo_pair(self, pipe_in, pipe_out):

        """
        Opens existing FIFO pair in worker for communication with main process
        :param pipe_in: input pipe path
        :param pipe_out: output pipe path
        :return: True or False if success or not
        """

        # Prepare named FIFOs

        for fifo_pair in ((pipe_in, self.mode_in), (pipe_out, self.mode_out)):

            fifo_path, fifo_mode = fifo_pair

            try:
                fd = os.open(fifo_path, fifo_mode | os.O_NONBLOCK)
            except:
                #traceback.print_exc()
                print(f"Error: Cannot open fifo {fifo_path}, exiting")
                return False

            if fifo_mode == self.mode_in:
                self.in_file = fifo_path
                self.in_fd = fd
            else:
                self.out_file = fifo_path
                self.out_fd = fd

        return True


    def read_from_pipe(self):
        """
        Read data packet from input pipe
        :return: string
        """
        R, W, X = select.select([self.in_fd],[],[])
        if R:
            size_b = os.read(self.in_fd, 4)
            size = int.from_bytes(size_b, 'little')
            #print(f'size={size}')
            R, W, X = select.select([self.in_fd], [], [])
            if R:
                data = os.read(self.in_fd, size)
                #print(f"data={data} size=[{size}]")
                return base64.b64decode(data)
        return None

    def write_to_pipe(self, line):
        """
        Write data packet to output pipe
        :param line: string
        :return: number of bytes written
        """
        if type(line) is str:
            line = bytes(line, 'ascii')
        data = base64.b64encode(line)
        size = len(data)
        size_b = size.to_bytes(4, 'little')
        R, W, X = select.select([],[self.out_fd],[])
        if W:
            os.write(self.out_fd, size_b)
            R, W, X = select.select([], [self.out_fd], [])
            if W:
                write_len = os.write(self.out_fd, bytes(data))
                return write_len

    def close_pipes(self):
        os.close(self.in_fd)
        os.close(self.out_fd)
        os.unlink(self.in_file)
        os.unlink(self.out_file)
        os.rmdir(self.tempdir)

# -[ The end ]-
