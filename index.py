import os
import string
from multiprocessing.pool import Pool
from collections import defaultdict
from typing import Optional
from time import perf_counter

import numpy as np


def format_text(text):
    return text.translate(str.maketrans('', '', string.punctuation)).replace('<br />', '\n').lower()


class Index:
    """Inverted index implementation"""
    def __init__(self):
        self.__storage = defaultdict(list)

    def add(self, session_path: str, th_no: int = 1, var: Optional[int] = None):
        """
        Add files to index
        :param session_path: parental directory of target files
        :type session_path: str
        :param th_no: number of threads
        :type th_no: int
        :param var: optional task variant
        :type var: int or None
        :raise: FileNotFoundError in session_path not exist
        :return: number of files added
        :rtype: int
        """
        if os.path.exists(session_path):
            files = self.__get_file_names(session_path, var)
            if th_no <= 1:
                res = [self._process_thread(files)]
            else:
                split = self.__split_files(files, th_no)
                pool = Pool(processes=th_no)
                res = pool.map(self._process_thread, split)
                pool.close()
                pool.join()
            self.__finalize(res)

            return len(files)
        else:
            raise FileNotFoundError(f'{session_path} does not exists')

    def search(self, word: str):
        """
        Search inside index
        :param word: word to search
        :type word: str
        :return: search result
        :rtype: List[tuple]
        """
        return self.__storage[format_text(word)]

    def reset(self):
        """
        Empty index
        """
        self.__storage = defaultdict(list)

    @staticmethod
    def _process_thread(files):
        s = perf_counter()
        ret = []
        for file in files:
            with open(file, 'r', encoding="utf8") as f:
                data = f.read()
            words = format_text(data).split()
            ret.extend([(word, file, i) for i, word in enumerate(words)])

        return ret, perf_counter() - s

    def __get_file_names(self, session_path, var):
        f = []
        if var is None:
            for (path, dirs, files) in os.walk(session_path):
                f.extend([os.path.join(path, file).replace('\\', '/') for file in files])
        else:
            _dirs = []
            for (path, dirs, files) in os.walk(session_path):
                _dirs.extend([os.path.join(path, dir).replace('\\', '/') for dir in dirs])

            for dir in _dirs:
                if any(file.endswith('.txt') for file in os.listdir(dir)):
                    N = len(os.listdir(dir))
                    start = int((N / 50 * (var - 1)) % N)
                    end = int((N / 50 * var) % N)
                    f.extend([os.path.join(dir, file) if end > int(file.replace('.txt', '').split('_')[0]) >= start else None for file in os.listdir(dir)])
                    f = list(filter(lambda a: a is not None, f))
        return f

    def __split_files(self, files, n):
        aux = defaultdict(list)
        sum = 0
        for file in files:
            sum += os.stat(file).st_size
            aux[os.stat(file).st_size].append(file)

        split = [[] for i in range(n)]
        target_size = sum / n

        i = 0
        mem_count = 0
        for size, bucket in aux.items():
            for file in bucket:
                if mem_count + size > target_size and i != n - 1:
                    i += 1
                    mem_count = 0
                split[i].append(file)
                mem_count += size

        return split

    def __finalize(self, res):
        for _data in res:
            for data in _data[0]:
                self.__storage[data[0]].append((data[1], data[2]))

