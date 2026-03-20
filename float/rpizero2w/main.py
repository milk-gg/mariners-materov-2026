import sys
import time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../common'))

from rf_communication import send_string, receive_string

def main():
    while True:
        print(receive_string())


if __name__ == "__main__":
    main()