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
        digit 7 is a checksum (sum of index and ascii % 10)
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
    start_time = time.time()
    end_marker_count = 0
    
    try:
        print(f"Listening for RF signal (timeout: {timeout_seconds}s)...")
        while True:
            # Check for timeout
            if time.time() - start_time > timeout_seconds:
                print("Timeout reached, stopping listener")
                break

            # Check for received code
            if rf.rx_code_timestamp:
                code = rf.rx_code_timestamp["code"]

                # Check for end marker
                if code == END_MARKER:
                    end_marker_count += 1
                    print("End marker received")
                    if end_marker_count >= 2:
                        break
                else:
                    # Decode the code
                    char, index = decode(code)
                    if char is not None:
                        received[index] = char
                        print(f"Received: '{char}' (index {index})")
                    else:
                        print(f"Failed to decode code: {code}")

                # Reset timestamp so we don't process the same code twice
                rf.rx_code_timestamp = None

            time.sleep(0.01)

    finally:
        rf.cleanup()

    text = "".join(received[i] for i in sorted(received))

    print(f"\nDecrypted message: '{text}'")
    return text

if __name__ == "__main__":
    receive_string()