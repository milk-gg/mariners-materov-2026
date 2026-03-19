# TODO: find a way to make transmission more reliable with more checksums
# did i cook or what.

from rpi_rf import RFDevice
import time

TX_GPIO = 17
RX_GPIO = 27

END_MARKER = 999999

PULSE = 350
REPEAT = 15

# encodes a string of text into a list of 6 digits, with each element being a char
def encode(text: str) -> list[int]:
    
    # ENCODING PROCEDURE
    # digits 1-3 are for index (max 999, start at 1)
    # digits 4-6 are for ascii value (032-126)

    codes = []
    for i, char in enumerate(text, start = 1):
        index_part = i
        ascii_part = ord(char)
        code = (index_part * 1000) + ascii_part
        codes.append(code)
    return codes

# decodes code 
def decode (code: int):

    if code <= 0 or code >= END_MARKER:
        return None, None
    
    index = code // 1000
    ascii_val = code % 1000

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
def recieve_string(gpio = RX_GPIO) -> str:
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