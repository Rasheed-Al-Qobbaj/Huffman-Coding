# Rasheed Alqobbaj

# Function to read bytes and their frequencies from a file
def count_byte_frequencies(file_path):
    frequency_dict = {}
    with open(file_path, 'rb') as file:
        byte = file.read(1)
        while byte:
            if byte in frequency_dict:
                frequency_dict[byte] += 1
            else:
                frequency_dict[byte] = 1
            byte = file.read(1)
    return frequency_dict


# Node class to store byte and frequency information
class Node:
    def __init__(self, byte, frequency, left=None, right=None):
        self.byte = byte
        self.frequency = frequency
        self.left = left
        self.right = right

    def __lt__(self, other):
        return self.frequency < other.frequency

    def is_leaf(self):
        return self.left is None and self.right is None


# Priority queue class to store nodes
class PriorityQueue:
    def __init__(self):
        self._queue = []

    def push(self, item):
        self._queue.append(item)
        self._sort()

    def pop(self):
        return self._queue.pop(0)

    def __len__(self):
        return len(self._queue)

    def _sort(self):
        for i in range(1, len(self._queue)):
            key = self._queue[i]
            j = i - 1
            while j >= 0 and key.frequency < self._queue[j].frequency:
                self._queue[j + 1] = self._queue[j]
                j -= 1
            self._queue[j + 1] = key


# Function to create a huffman tree from a dictionary of byte frequencies
def create_huffman_tree(frequency_dict):
    queue = PriorityQueue()

    for byte, frequency in frequency_dict.items():
        queue.push(Node(byte, frequency))

    while len(queue) > 1:
        node1 = queue.pop()
        node2 = queue.pop()

        merged = Node(None, node1.frequency + node2.frequency, node1, node2)

        queue.push(merged)

    return queue.pop()  # Return root node


# Function to create a table of byte encodings from a huffman tree
def create_encoding_table(root):
    encoding_table = {}

    def traverse(node, code):
        if node is not None:
            if node.byte is not None:
                encoding_table[node.byte] = code
            else:
                traverse(node.left, code + '0')
                traverse(node.right, code + '1')

    traverse(root, '')
    return encoding_table

class BitWriter:
    def __init__(self, file):
        self.file = file  # The file we are writing to
        self.buffer = ''  # The buffer where we store bits until we have a full byte
        self.nbits = 0  # The number of bits in the buffer

    def write_bit(self, bit):
        # Add the bit to the buffer
        self.buffer += bit
        self.nbits += 1

        # If we have a full byte, write it to the file
        if self.nbits == 8:
            self.flush()

    def flush(self):
        # If the buffer is not empty, pad it with zeros and write it to the file
        if self.nbits > 0:
            self.buffer += '0' * (8 - self.nbits)
            self.file.write(bytes([int(self.buffer, 2)]))
            print(f'Write byte: {self.buffer}')  # Print the byte (for debugging purposes)
            self.buffer = ''
            self.nbits = 0

def write_tree(node, bit_writer):
    header = ''
    if node.is_leaf():
        bit_writer.write_bit('1')
        header += '1'
        # Convert the byte to bits and write each bit
        for bit in format(ord(node.byte), '08b'):
            bit_writer.write_bit(bit)
            header += bit
    else:
        bit_writer.write_bit('0')
        header += '0'
        left_header, _ = write_tree(node.left, bit_writer)
        right_header, _ = write_tree(node.right, bit_writer)
        header += left_header + right_header
    return header, len(header)

def write_encoded_data(encoding_table, original_file_path, bit_writer):
    with open(original_file_path, 'rb') as original_file:
        byte = original_file.read(1)
        while byte:
            for bit in encoding_table[byte]:
                bit_writer.write_bit(bit)
            byte = original_file.read(1)

def encode(original_file_path, output_file_path):
    frequency_dict = count_byte_frequencies(original_file_path)
    root = create_huffman_tree(frequency_dict)
    encoding_table = create_encoding_table(root)

    with open(output_file_path, 'wb') as output_file:
        bit_writer = BitWriter(output_file)
        header, header_size = write_tree(root, bit_writer)  # Get the header size directly from the write_tree function
        write_encoded_data(encoding_table, original_file_path, bit_writer)
        bit_writer.flush()  # Make sure to flush the last byte

    original_file_size = sum(frequency for frequency in frequency_dict.values())
    compressed_file_size = len(open(output_file_path, 'rb').read())
    compression_rate = (original_file_size - compressed_file_size) / original_file_size

    return original_file_size, compressed_file_size, header_size, compression_rate, header

class BitReader:
    def __init__(self, file):
        self.file = file
        self.buffer = ''
        self.nbits = 0

    def read_bit(self):
        if self.nbits == 0:
            self.buffer = self.file.read(1)
            if len(self.buffer) == 0:
                return None
            self.buffer = format(ord(self.buffer), '08b')
            self.nbits = 8
            # If this is the last byte in the file, only read the number of bits that were actually written
            if len(self.file.peek(1)) == 0:
                self.nbits = self.buffer.count('1')
        bit = self.buffer[0]
        self.buffer = self.buffer[1:]
        self.nbits -= 1
        print(f'Read bit: {bit}')  # Print the bit
        return bit

def read_tree(bit_reader):
    bit = bit_reader.read_bit()
    header = bit
    if bit == '1':
        byte = ''
        for _ in range(8):
            byte += bit_reader.read_bit()
        header += byte
        return Node(chr(int(byte, 2)), None), header
    else:
        left, left_header = read_tree(bit_reader)
        right, right_header = read_tree(bit_reader)
        return Node(None, None, left, right), header + left_header + right_header

def read_encoded_data(root, bit_reader, output_file_path):
    with open(output_file_path, 'wb') as output_file:
        bit = bit_reader.read_bit()
        while bit is not None:
            node = root
            while not node.is_leaf():
                if bit == '0':
                    node = node.left
                else:
                    node = node.right
                bit = bit_reader.read_bit()
            output_file.write(node.byte.encode())

def decode(input_file_path, output_file_path):
    with open(input_file_path, 'rb') as input_file:
        bit_reader = BitReader(input_file)
        root, header = read_tree(bit_reader)
        read_encoded_data(root, bit_reader, output_file_path)

    with open(input_file_path, 'rb') as f:
        original_size = len(f.read())

    with open(output_file_path, 'rb') as f:
        decompressed_size = len(f.read())

    return original_size, decompressed_size, header

def main():
    file_path = 'test.txt'
    frequency_dict = count_byte_frequencies(file_path)
    print(frequency_dict)
    p = PriorityQueue()
    for byte, frequency in frequency_dict.items():
        p.push(Node(byte, frequency))

    # print the queue
    while len(p) > 0:
        node = p.pop()
        print(node.byte, node.frequency)

    root = create_huffman_tree(frequency_dict)
    encoding_table = create_encoding_table(root)
    print(encoding_table)

    original_file_path = 'test.txt'
    output_file_path = 'test.huff'
    original_file_size, compressed_file_size, header_size, compression_rate, header = encode(original_file_path, output_file_path)
    print(f'Original file size: {original_file_size} bytes ({original_file_size*8} bits)')
    print(f'Compressed file size: {compressed_file_size} bytes ({compressed_file_size*8} bits)')
    print(f'Header size: {round(header_size/8)} bytes ({header_size} bits)')
    print(f'Compression rate: {compression_rate*100:.2f}%')

    decode('test.huff', 'test_decoded.txt')





if __name__ == '__main__':
    main()

