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


# Function to write a file with the encoding table and the encoded data
def write_encoded_file(input_file_path, output_file_path, encoding_table, root):
    input_file_size = 0
    output_file_size = 0
    header_size = 0

    def write_node(node, output_file, bit_buffer, buffer_length):
        nonlocal output_file_size, header_size
        if buffer_length >= 8:
            output_file.write(int(bit_buffer[:8], 2).to_bytes(1, 'big'))
            bit_buffer = bit_buffer[8:]
            buffer_length -= 8

        if node.is_leaf():
            bit_buffer += '1' + format(ord(node.byte), '08b')
            buffer_length += 9
        else:
            bit_buffer += '0'
            buffer_length += 1
            bit_buffer, buffer_length = write_node(node.left, output_file, bit_buffer, buffer_length)
            bit_buffer, buffer_length = write_node(node.right, output_file, bit_buffer, buffer_length)

        return bit_buffer, buffer_length

    with open(input_file_path, 'rb') as input_file, open(output_file_path, 'wb') as output_file:
        bit_buffer, buffer_length = write_node(root, output_file, '', 0)
        while buffer_length >= 8:
            output_file.write(int(bit_buffer[:8], 2).to_bytes(1, 'big'))
            bit_buffer = bit_buffer[8:]
            buffer_length -= 8
        if buffer_length > 0:
            output_file.write(int(bit_buffer, 2).to_bytes(1, 'big'))
            output_file_size += 1
            header_size += 1

        buffer = ''
        byte = input_file.read(1)
        while byte:
            input_file_size += 1
            buffer += encoding_table[byte]
            while len(buffer) >= 8:
                output_file.write(int(buffer[:8], 2).to_bytes(1, 'big'))
                buffer = buffer[8:]
                output_file_size += 1
            byte = input_file.read(1)

        # Write the remaining bits in the buffer, if any
        if buffer:
            output_file.write(int(buffer, 2).to_bytes(1, 'big'))
            output_file_size += 1

    # Calculate and print the compression statistics
    print(f'Original file size: {input_file_size} bytes ({input_file_size * 8} bits)')
    print(f'Compressed file size: {output_file_size} bytes ({output_file_size * 8} bits)')
    print(f'Compression ratio: {output_file_size / input_file_size:.2f}')
    print(f'Header size: {header_size} bytes ({header_size * 8} bits)')

    return header_size, output_file_size



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

    input_file_path = 'test.txt'
    output_file_path = 'test.huff'
    write_encoded_file(input_file_path, output_file_path, encoding_table, root)



if __name__ == '__main__':
    main()

