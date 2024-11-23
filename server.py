import cv2
import socket
import pickle
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

#Importing to generate RSA public/private key pair
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

import os

#Generate RSA public/private key pair
key = RSA.generate(2048)
private_key = key.export_key()
public_key = key.publickey().export_key()

#save the keys to files
with open("private.pem", "wb") as f:
    f.write(private_key)

with open("public.pem", "wb") as f:
    f.write(public_key)


#Constants
SERVER_IP = '127.0.0.1'
SERVER_PORT = 5000

#Initialize socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((SERVER_IP, SERVER_PORT))

#Receive AES-encrypted key from the client
encrypted_aes_key, client_address = server_socket.recvfrom(256)

#Load the server's private key
with open("private.pem", "rb") as f:
    private_key = RSA.import_key(f.read())

#Decrypt the AES key using server's private key
cipher_rsa = PKCS1_OAEP.new(private_key)
decrypted_aes_key = cipher_rsa.decrypt(encrypted_aes_key)

print(f"Decrypted AES Key: {decrypted_aes_key}")

KEY = decrypted_aes_key

#Initialize AES Cipher
#Initialize AES cipher
cipher = AES.new(KEY, AES.MODE_CBC, iv = os.urandom(AES.block_size))

print("Receiving Live Stream(press 'Ctrl+C' to end)")

#incoming data chunks
frame_data = b""

def receive_large_data(server_socket):
    #receives data in chunks and reassembles them
    global frame_data
    CHUNK_SIZE = 1024

    while True:
        chunk, _ = server_socket.recvfrom(CHUNK_SIZE)
        if chunk:
            frame_data += chunk
        
        if len(chunk) < CHUNK_SIZE:
            break

while True:
    #Receive data from client in chunks
    receive_large_data(server_socket)

    if not frame_data:
        continue
    #encrypted_frame, client_address = server_socket.recvfrom(65535)
    try:
        #Decrypt and deserialize the frame
        decrypted_frame = unpad(cipher.decrypt(frame_data), AES.block_size)
        frame = pickle.loads(decrypted_frame)

        #Display received video
        cv2.imshow("Server - Receiving Video", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        #reset frame data buffer
        frame_data = b""

    except Exception as e:
        print(f"Error decrypting frame: {e}")
        continue
cv2.destroyAllWindows()
server_socket.close()