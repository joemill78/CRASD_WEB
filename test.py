import json
from database import DB


def mem_to_g(value):
    return round(int(value) / 1024)

def main():
    pg = DB()
    pg.connect()
    data = pg.get_mem_utilized()

    labels = []
    values = []

    for line in data:
        values.append(mem_to_g(line[0]))
        labels.append(line[1].strftime('%Y-%m-%d %H:%M:%S'))

    print values
    print labels
    pg.close()



if __name__ == '__main__':
    main()

