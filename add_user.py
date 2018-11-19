import json
import getpass
from password_manager import PW_MANAGER 


def main():
    print "ADD USER CREDENTIALS"
    username = raw_input("Username: ")
    password = password = getpass.getpass('Password: ')
    pm = PW_MANAGER()
    pm.hash_pwd(username, password)


if __name__ == '__main__':
    main()
