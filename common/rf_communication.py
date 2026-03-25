import time, sys, os

rpi_rf_path = os.path.join(os.path.dirname(__file__), 'rpi-rf', 'rpi_rf')
sys.path.insert(0, rpi_rf_path)

from rpi_rf import RFDevice

# gpio pin connections
TX_GPIO = 17
RX_GPIO = 27

END_MARKER = 999999

PROTOCOL = 1
PULSE = 0
REPEAT = 10
LENGTH = 24
 
def encode(text: str) -> list[int]:
    """
    Encodes a string of text into a list of 7 digits, with each element being a char + checksum

    ENCODING PROCEDURE:
        digits 1-3 are for index (max 999, start at 1)
        digits 4-6 are for ascii value (032-126)
        digit 7 is for checksum (sum of index and ascii % 10)
    """

    codes = []
    for i, char in enumerate(text, start = 1):
        index_part = i
        ascii_part = ord(char)
        checksum = (index_part + ascii_part) % 10
        code = (index_part * 10000) + (ascii_part * 10) + checksum
        codes.append(code)
    return codes

# decodes code 
def decode (code: int):

    if code <= 0 or code >= END_MARKER:
        return None, None
    
    index = code // 10000
    ascii_val = (code // 10) % 1000
    checksum = code % 10

    # checksum
    if (index + ascii_val) % 10 != checksum:
        return None, None
    
    if not (32 <= ascii_val <= 126):
        return None, None
    
    return chr(ascii_val), index

# send a string
def send_string(text: str, gpio = TX_GPIO):

    rf = None
    try:
        rf = RFDevice(gpio)
        rf.enable_tx()

        codes = encode(text)
        print(f"Sending: '{text}'  {len(codes)} codes")
        for code in codes:
            rf.tx_code(code, PROTOCOL, PULSE, LENGTH)
            time.sleep(.15)

        # send END_MARKER two times to ensure end
        for _ in range(2):
            rf.tx_code(END_MARKER, PROTOCOL, PULSE, LENGTH)
            time.sleep(.15)
        print("Done sending")

    finally:
        if rf is not None:
            rf.cleanup()

# listen for an RF signal, continue listening until END_MARKER
def receive_string(gpio = RX_GPIO, timeout_seconds: float = 60.0) -> str:

    try:
        rf = RFDevice(gpio)
        rf.enable_rx()
    except Exception as e:
        print(f"Failed to initialize RF device: {e}")
        return ""

    received = {}
    last_code = None
    deadline = time.time() + timeout_seconds
    zero_count = 0

    print("Listening for message...")

    try:
        while True:
            if time.time() > deadline:
                print(f"Timeout reached ({timeout_seconds}s), zero codes: {zero_count}")
                break

            code = rf.rx_code

            if code == 0:
                zero_count += 1
                time.sleep(0.01)
                continue

            if code == last_code:
                time.sleep(0.01)
                continue

            last_code = code

            print(f"Received code: {code}")

            if code == END_MARKER:
                break

            char, index = decode(code)
            if char is not None:
                if index not in received:
                    received[index] = char
                    print(f"    [{index}] '{char}' (code {code})")
                else:
                    print(f"    Duplicate index {index} ignored (code {code})")
            else:
                print(f"    Invalid code ignored: {code}")

    finally:
        rf.cleanup()

    text = "".join(received[i] for i in sorted(received))

    print(f"\nDecrypted message: '{text}'")
    return text

recieve_string = receive_string