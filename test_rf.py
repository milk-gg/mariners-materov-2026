import sys, os
common_path = os.path.join(os.path.dirname(__file__), 'common')
sys.path.insert(0, common_path)

from rf_communication import send_string, receive_string

print("Testing RF communication...")

# Test send
print("Sending 'hello'...")
send_string("hello")

# Test receive (short timeout)
print("Receiving...")
result = receive_string(timeout_seconds=10.0)
print(f"Received: '{result}'")

if result == "hello":
    print("SUCCESS: Loopback worked!")
else:
    print("FAILED: No data received")