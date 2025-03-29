# Real-Time Encrypted Video Streaming

## Overview

This Python-based real-time video streaming application enables secure transmission of video frames between a client and a server using encryption. The program ensures confidentiality by utilizing:

AES (Advanced Encryption Standard) for encrypting video frames.

RSA (Rivest-Shamir-Adleman) for securely exchanging the AES key.

UDP (User Datagram Protocol) for efficient, low-latency data transfer.

cv2 (OpenCV) for video capture and display.

The system consists of two files:

client.py: Captures video from a webcam, encrypts it, and sends it to the server.

server.py: Receives, decrypts, and displays the video stream.

## Features

End-to-End Encryption: Ensures video data remains confidential using AES and RSA.

Real-Time Streaming: Uses UDP for low-latency communication.

Secure Key Exchange: RSA encryption protects the AES key transmission.

Efficient Data Handling: Large video frames are chunked to prevent UDP packet loss.

## Technologies Used

Python

OpenCV (cv2)

Socket Programming (socket)

Cryptography (Crypto from PyCryptodome)

Pickle (for serialization)

## Installation & Setup

Prerequisites

Ensure you have Python installed (3.x recommended) and install the required dependencies:

pip install opencv-python pycryptodome

Running the Server

Run the server script to generate RSA key pairs and start listening for connections:

python server.py

Running the Client

Run the client script to capture and send encrypted video frames:

python client.py

### Expected Output

The client captures and sends an encrypted video stream.

The server receives, decrypts, and displays the live video.

Security Considerations

Key Management: The private RSA key should be stored securely and not shared.

IV Synchronization: The AES cipher should ensure IV coordination between client and server.

UDP Limitations: UDP does not guarantee packet delivery; enhancements can include packet acknowledgment mechanisms.

## Contribution

We welcome contributions to improve security and performance. To contribute:

Fork the repository.

Create a feature branch.

Submit a pull request with clear documentation.
