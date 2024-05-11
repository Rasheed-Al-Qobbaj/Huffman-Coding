# Huffman Coding

# Custom heap (priority queue) implementation
class Heap:
    def __init__(self):
        self.heap = []

    def insert(self, node):
        self.heap.append(node)
        self.heapify_up(len(self.heap)-1)

    def heapify_up(self, index):
        parent = (index-1)//2
        if parent >= 0 and self.heap[parent].freq > self.heap[index].freq:
            self.heap[parent], self.heap[index] = self.heap[index], self.heap[parent]
            self.heapify_up(parent)

    def remove(self):
        if len(self.heap) == 0:
            return None
        self.heap[0], self.heap[-1] = self.heap[-1], self.heap[0]
        node = self.heap.pop()
        self.heapify_down(0)
        return node

    def heapify_down(self, index):
        left = 2*index + 1
        right = 2*index + 2
        smallest = index
        if left < len(self.heap) and self.heap[left].freq < self.heap[smallest].freq:
            smallest = left
        if right < len(self.heap) and self.heap[right].freq < self.heap[smallest].freq:
            smallest = right
        if smallest != index:
            self.heap[smallest], self.heap[index] = self.heap[index], self.heap[smallest]
            self.heapify_down(smallest)

    def size(self):
        return len(self.heap)

    def is_empty(self):
        return len(self.heap) == 0


# Binary tree node
class Node:
    def __init__(self, char, freq):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None

    def __lt__(self, other):
        return self.freq < other.freq

    def __eq__(self, other):
        return self.freq == other.freq

    def __repr__(self):
        return f'{self.char}: {self.freq}'


# Huffman coding
def huffman_encoding(data):
    if len(data) == 0:
        return '', None

    # Calculate frequency of each character
    freq = {}
    for char in data:
        if char not in freq:
            freq[char] = 0
        freq[char] += 1

    # Create heap of nodes
    heap = Heap()
    for char, freq in freq.items():
        heap.insert(Node(char, freq))

    # Build Huffman tree
    while heap.size() > 1:
        left = heap.remove()
        right = heap.remove()
        new_node = Node(None, left.freq + right.freq)
        new_node.left = left
        new_node.right = right
        heap.insert(new_node)

    root = heap.remove()

    # Generate encoding for each character
    encoding = {}
    def generate_encoding(node, code):
        if node is None:
            return
        if node.char is not None:
            encoding[node.char] = code
            return
        generate_encoding(node.left, code + '0')
        generate_encoding(node.right, code + '1')

    generate_encoding(root, '')

    # Encode data
    encoded_data = ''.join([encoding[char] for char in data])

    return encoded_data, root


# Display Huffman tree
def display_tree(node, level=0):
    if node is None:
        return
    display_tree(node.right, level+1)
    print('   '*level + str(node))
    display_tree(node.left, level+1)


# Display Table
def display_table(data, encoding):
    print('Character\tFrequency\tHuffman Code')
    for char, freq in data.items():
        print(f'{char}\t\t{freq}\t\t{encoding[char]}')


def main():
    data = 'The bird is the word'
    encoded_data, tree = huffman_encoding(data)

    print('Original data:', data)
    print('Encoded data:', encoded_data)
    print('Huffman tree:')
    display_tree(tree)

    freq = {}
    for char in data:
        if char not in freq:
            freq[char] = 0
        freq[char] += 1

    print('\nTable:')
    display_table(freq, {char: code for char, code in tree})


if __name__ == '__main__':
    main()

