from index_structure import InvertedIndex

if __name__ == '__main__':
    path = ''
    thread_no = 2
    index = InvertedIndex(thread_no)
    index.process(path)