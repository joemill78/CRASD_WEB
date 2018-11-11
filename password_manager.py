from bcrypt import hashpw, gensalt
from database import DB


class PW_MANAGER(object):
    def __init__(self):
        self.pwd = None

    def validate(self, username, pwd):
        pg = DB()
        pg.connect()
        pwd_db = pg.get_password(username)

        if pwd_db:
            if hashpw(pwd, pwd_db[0]) == pwd_db[0]:
                return True
            else:
                return False
        else:
            return False

    def hash_pwd(self, username, pwd):
        hashed_pwd = hashpw(pwd, gensalt())
        pg = DB()
        pg.connect()
        pg.add_user(username, hashed_pwd)
        pg.close()


if __name__ == '__main__':
    pm = PW_MANAGER()
    username = 'jmillan'
    password = 'admin'
    #pm.hash_pwd(username, password)
    if pm.validate(username, password):
        print "password match"
    else:
        print "invalid credentials"