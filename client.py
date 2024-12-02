import cv2
import socket
import pickle
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import os

# Load the server's public key for encrypting the AES key
# Public key is shared openly and used to secure the communication.
with open("public.pem", "rb") as f:
    public_key = RSA.import_key(f.read())

# Generate a random AES key for encrypting video frames
aes_key = os.urandom(16)  # AES-128 (16 bytes) for efficient symmetric encryption

# Encrypt the AES key with the server's public RSA key
# RSA ensures secure exchange of the AES key over an untrusted network.
cipher_rsa = PKCS1_OAEP.new(public_key)
encrypted_aes_key = cipher_rsa.encrypt(aes_key)

# Initialize UDP socket for sending data
# UDP is chosen for its low-latency and high-speed data transmission.
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Networking constants
SERVER_IP = '127.0.0.1'  # Loopback address for local testing
SERVER_PORT = 5000  # Port for UDP communication

# Send the encrypted AES key to the server
client_socket.sendto(encrypted_aes_key, (SERVER_IP, SERVER_PORT))

# Initialize AES cipher for encryption
# CBC mode provides secure encryption; IV should be random.
cipher = AES.new(aes_key, AES.MODE_CBC, iv=os.urandom(AES.block_size))

# Capture video from the webcam
cap = cv2.VideoCapture(0)

print("Live Streaming video(press 'Ctrl+C' to end)")

def send_large_data(data, client_socket, address):
    """
    Function to send large amounts of data in smaller chunks using UDP.
    This avoids issues with UDP's maximum datagram size.
    """
    CHUNK_SIZE = 1024
    data_length = len(data)

    for i in range(0, data_length, CHUNK_SIZE):
        chunk = data[i:i + CHUNK_SIZE]
        client_socket.sendto(chunk, address)  # Send each chunk separately

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break  # Exit if no frame is captured

    # Serialize the video frame and encrypt it
    serialized_frame = pickle.dumps(frame)  # Convert frame to a byte stream
    encrypted_frame = cipher.encrypt(pad(serialized_frame, AES.block_size))  # Encrypt with padding

    # Send encrypted frame to the server
    send_large_data(encrypted_frame, client_socket, (SERVER_IP, SERVER_PORT))

    # Display the video being sent
    cv2.imshow("Client - Sending Video", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):  # Exit on 'q' key press
        break

cap.release()
cv2.destroyAllWindows()
client_socket.close()  # Close the socket connection
