import json
from database import DB


def mem_to_g(value):
    return round(int(value) / 1024)

def main():
    pg = DB()
    pg.connect()
    data = pg.get_password('jmillan')
    if data:
        print data[0]
    else:
        print "user not found"

    pg.close()



if __name__ == '__main__':
    main()

