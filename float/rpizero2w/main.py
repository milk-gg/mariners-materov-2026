import sys
import time

common_path = os.path.join(os.path.dirname(__file__), '../../common')
sys.path.insert(0, common_path)

from rf_communication import send_string, receive_string

def main():
    while True:
        print(receive_string())


if __name__ == "__main__":
    main()
