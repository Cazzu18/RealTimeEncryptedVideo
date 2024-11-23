import cv2
import socket
import pickle
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from hashlib import sha256
import os

#loading the server's public key
with open("public.pem", "rb") as f:
    public_key = RSA.import_key(f.read())

#Generate AES key
aes_key = os.urandom(16)

#Encrypt the AES key using the server's public key
cipher_rsa = PKCS1_OAEP.new(public_key)
encrypted_aes_key = cipher_rsa.encrypt(aes_key)

#Initialize socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

#Constants
SERVER_IP = '127.0.0.1'
SERVER_PORT = 5000

client_socket.sendto(encrypted_aes_key, (SERVER_IP, SERVER_PORT))


#Initialize AES cipher
cipher = AES.new(aes_key, AES.MODE_CBC, iv = os.urandom(AES.block_size))

#video capture
cap = cv2.VideoCapture(0)

print("Live Streaming video(press 'Ctrl+C' to end)")

def send_large_data(data, client_socket, address):
    #Splits data into smaller chunks and sends over UDP
    CHUNK_SIZE = 1024
    data_length = len(data)

    for i in range(0, data_length, CHUNK_SIZE):
        chunk = data[i:i + CHUNK_SIZE]
        client_socket.sendto(chunk, address)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    #serialize and encrypt the frame
    serialized_frame = pickle.dumps(frame)
    encrypted_frame = cipher.encrypt(pad(serialized_frame, AES.block_size))

    #send to server
    send_large_data(encrypted_frame, client_socket, (SERVER_IP, SERVER_PORT))

    #Display local video
    cv2.imshow("Client - Sending Video", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
client_socket.close()