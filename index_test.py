import os

from index import Index, format_text


def check_if_correct(path: str, th_no: int):
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


if __name__ == '__main__':
    session_path = ''
    err = check_if_correct(session_path, 10)
    print(err)
