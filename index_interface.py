import time

import jsonpickle
import requests


class IndexUI:
    def __init__(self, ip, port=5000):
        self.ip = ip
        self.port = port
        self.url = f'http://{ip}:{port}/api'

    def get_url(self, endpoint):
        return '/'.join(s.strip('/') for s in (self.url, endpoint))

    def run(self):
        while True:
            cmd = input('$ ').split()
            if cmd[0] == 'add':
                self.__add(cmd)
            elif cmd[0] == 'reset':
                self.__reset(cmd)
            elif cmd[0] == 'search':
                res = self.__search(cmd)
                for f, d in res:
                    print(f, d)
            elif cmd[0] == 'exit':
                break
            elif cmd[0] == 'help':
                print('Available options are:\n'
                      '\tadd {sesion_path}\n'
                      '\tsearch {word_1} {word_2} ...\n'
                      '\treset\n'
                      '\texit')
            else:
                print('Unknown command')

    def __add(self, cmd: list, max_wait: float = 3):
        path = cmd[1]
        var = None
        if '-v' in cmd:
            var = int(cmd[cmd.index('-v') + 1])

        url = self.get_url('add_files')
        start = time.perf_counter()
        while True:
            try:
                response = requests.post(url, data=jsonpickle.encode({'path': path, 'var': var}))
            except requests.exceptions.RequestException as e:
                if not max_wait or time.perf_counter() - start < max_wait:
                    time.sleep(0.1)
                else:
                    raise TimeoutError('Could not get response from server in time') from e
            else:
                break

        result = jsonpickle.decode(response.content)
        print(f'Added {result["files"] if "files" in result else ""} new files')

    def __search(self, cmd: list, max_wait: float = 3):
        word = cmd[1]

        url = self.get_url('search')
        start = time.perf_counter()
        while True:
            try:
                request = {'words': [word]}
                response = requests.get(url, data=jsonpickle.encode(request))
            except requests.exceptions.RequestException as e:
                if not max_wait or time.perf_counter() - start < max_wait:
                    time.sleep(0.1)
                else:
                    raise TimeoutError('Could not get response from server in time') from e
            else:
                break

        result = jsonpickle.decode(response.content)
        if 'results' in result:
            return result['results']
        else:
            return None

    def __reset(self, cmd: list, max_wait: float = 3):
        url = self.get_url('clear')
        start = time.perf_counter()
        while True:
            try:
                request = {}
                requests.post(url, data=jsonpickle.encode(request))
            except requests.exceptions.RequestException as e:
                if not max_wait or time.perf_counter() - start < max_wait:
                    time.sleep(0.1)
                else:
                    raise TimeoutError('Could not get response from server in time') from e
            else:
                print(f'Index was emptied')
                break


if __name__ == '__main__':
    cmd = IndexUI('localhost')
    cmd.run()
