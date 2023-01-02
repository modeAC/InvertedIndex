import os
from collections import defaultdict
from multiprocessing.pool import ThreadPool

import numpy as np


class InvertedIndex:
    def __init__(self, thread_no: int = 1):
        """
        Args:
            thread_no: number of threads to invoke

        Raises:
            Exception: If thread number is lower than 1
        """
        if thread_no <= 0:
            raise Exception('thread number can`t be lower than 1')
        self.__th_no = thread_no
        self.__tp = ThreadPool(processes=self.__th_no)

        self.__map = defaultdict(list)

    def process(self, session_path: str):
        """
        Args:
            session_path: target directory path
        """
        files = self.__traverse_dir(session_path)
        split = np.array_split(files, self.__th_no)
        self.__start_threads(split)

    def search(self, word: str):
        """
        Args:
            word: word to search (any string)

        Returns:
            list([file_path, word_pos],...)
        """
        return self.__map[word]

    def clear(self):
        self.__map = defaultdict(list)

    def release(self):
        self.__tp.close()
        self.__tp.join()

    def __del__(self):
        self.release()

    def __start_threads(self, split):
        self.__tp.map(self.__single_thread, split)

    def __single_thread(self, files):
        for file in files:
            with open(file, 'r') as f:
                data = f.read()

            split = data.split()
            for i in range(len(split)):
                word = split[i]
                self.__map[word].append((file, i))

    def __traverse_dir(self, session_path):
        f = []
        for (dirpath, dirnames, filenames) in os.walk(session_path):
            f.extend([os.path.join(dirpath, path).replace('\\', '/') for path in filenames])
        return f
