import cv2
import socket
import pickle
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import os

# Generate RSA public/private key pair
# RSA is used for asymmetric encryption to securely exchange the AES key.
key = RSA.generate(2048)  # 2048-bit key ensures strong encryption
private_key = key.export_key()  # Export private key for decryption
public_key = key.publickey().export_key()  # Export public key for sharing with clients

# Save the keys to files for persistent use
# Private key should be kept secure and not shared.
with open("private.pem", "wb") as f:
    f.write(private_key)

with open("public.pem", "wb") as f:
    f.write(public_key)

# Networking constants
SERVER_IP = '127.0.0.1'  # Loopback address for local testing
SERVER_PORT = 5000  # Port for UDP communication

# Initialize UDP socket for receiving data
# UDP is chosen for low-latency streaming but doesn't guarantee reliability.
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((SERVER_IP, SERVER_PORT))

# Receive AES-encrypted key from the client
# AES is used for symmetric encryption of the video frames.
# 256 bytes to accommodate RSA-encrypted AES key
encrypted_aes_key, client_address = server_socket.recvfrom(256)

# Load the server's private key to decrypt the received AES key
with open("private.pem", "rb") as f:
    private_key = RSA.import_key(f.read())  # Import private key from file

# Decrypt the AES key using the private RSA key
# PKCS1_OAEP padding ensures secure decryption, preventing certain attacks.
cipher_rsa = PKCS1_OAEP.new(private_key)
decrypted_aes_key = cipher_rsa.decrypt(encrypted_aes_key)

print(f"Decrypted AES Key: {decrypted_aes_key}")

KEY = decrypted_aes_key  # Store the decrypted AES key for subsequent decryption

# Initialize AES cipher for decryption
# CBC mode ensures secure encryption by chaining blocks.
cipher = AES.new(KEY, AES.MODE_CBC, iv=os.urandom(AES.block_size))  # IV is random but not coordinated here

print("Receiving Live Stream(press 'Ctrl+C' to end)")

# Buffer to store incoming encrypted frame data
frame_data = b""

def receive_large_data(server_socket):
    """
    Function to receive large amounts of data in chunks using UDP.
    This is necessary because UDP datagrams have a maximum size limit.
    """
    global frame_data
    CHUNK_SIZE = 1024  # Maximum size of each chunk
    while True:
        chunk, _ = server_socket.recvfrom(CHUNK_SIZE)
        if chunk:
            frame_data += chunk
        
        if len(chunk) < CHUNK_SIZE:  # End of data
            break

while True:
    # Receive frame data from the client
    receive_large_data(server_socket)

    if not frame_data:
        continue  # Skip if no data received

    try:
        # Decrypt the received data and unpad to retrieve the original frame
        decrypted_frame = unpad(cipher.decrypt(frame_data), AES.block_size)
        frame = pickle.loads(decrypted_frame)  # Deserialize frame to reconstruct the original object

        # Display the received video frame
        cv2.imshow("Server - Receiving Video", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):  # Exit on 'q' key press
            break

        frame_data = b""  # Reset frame data buffer

    except Exception as e:
        # Log any errors that occur during decryption or deserialization
        print(f"Error decrypting frame: {e}")
        continue

cv2.destroyAllWindows()
server_socket.close()  # Close the socket connection
