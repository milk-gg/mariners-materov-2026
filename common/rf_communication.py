import time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../common'))

from rpi_rf import RFDevice


# gpio pin connections
TX_GPIO = 17
RX_GPIO = 27

END_MARKER = 999999

PULSE = 350
REPEAT = 15
 
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

    rf = RFDevice(gpio)
    rf.enable_tx()

    try:
        codes = encode(text)
        print(f"Sending: '{text}'  {len(code)} codes")
        for code in codes:
            rf.tx_code(code, tx_pulselength = PULSE, tx_repeat = REPEAT)
            time.sleep(.15)

        # send END_MARKER two times to ensure end
        for _ in range(2):
            rf.tx_code(END_MARKER, tx_pulselength = PULSE, tx_repeat = REPEAT)
            time.sleep(.15)
        print("Done sending")
    finally:
        rf.cleanup()

# listen for an RF signal, continue listening until END_MARKER
def receive_string(gpio = RX_GPIO) -> str:
    rf = RFDevice(gpio)
    rf.enable_rx()
    received = {}
    last_ts = None

    print("Listening for message...")

    try:
        while True:
            ts = rf.rx_code_timestamp
            if ts == last_ts:
                time.sleep(0.01)
                continue

            last_ts = ts
            code = rf.rx_code

            if code == END_MARKER:
                break

            char, index = decode(code)
            if char is not None and index not in received:
                received[index] = char
                print(f"    [{index}] '{char}' (code {code})")
    finally:
        rf.cleanup()

    text = "".join(received[i] for i in sorted(received))

    print(f"\nDecrypted message: '{text}'")
    return text