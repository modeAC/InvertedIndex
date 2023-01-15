import os
import unittest

from index import Index, format_text


def get_project_path() -> str:
    """
    Returns absolute path to project directory
    :return: path to project
    :rtype: str
    """
    return os.path.dirname(os.path.abspath(__file__))


def check_if_correct(path: str, th_no: int) -> list:
    """
    :param path: path to test files
    :type path: str
    :param th_no: number of parallel units
    :type th_no: int
    :return: list of tuples with anomalies
    :rtype: list
    """
    i = Index()
    i.add(path, th_no=th_no)

    err = []
    for file in os.listdir(path):
        with open(os.path.join(path, file), 'r', encoding="utf8") as f:
            data = f.read()
        for w in format_text(data).split():
            found = False
            for res in i.search(w):
                if res[0] == os.path.join(path, file).replace('\\', '/'):
                    found = True
                    break
            if not found:
                err.append((w, file))
    if len(err) == 0:
        print('everything is fine')
    else:
        print('something went wrong')
    return err


class TestIndex(unittest.TestCase):
    proj_path = get_project_path()

    def test_parallel(self):
        path = os.path.join(self.proj_path, 'test_selection')
        th_no = 5

        err = check_if_correct(path, th_no=th_no)
        self.assertTrue(len(err) == 0)

    def test_sequential(self):
        path = os.path.join(self.proj_path, 'test_selection')
        th_no = 1

        err = check_if_correct(path, th_no=th_no)
        self.assertTrue(len(err) == 0)


if __name__ == '__main__':
    unittest.main()
