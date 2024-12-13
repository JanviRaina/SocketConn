# sender.py
import socket
import time
import base64
import random

# Configuration
TCP_IP = "127.0.0.1"
UDP_IP = "127.0.0.1"
TCP_PORT = 5005
UDP_PORT = 5005
NUM_PACKETS = 6
PACKET_DROP_PROBABILITY = 0.3  # Simulated packet drop rate
MAX_RETRIES = 5  # Maximum retries for Reliable UDP

# Function to encode data
def encode_data(data):
    encoded = base64.b64encode(data).decode('utf-8')
    print(f"Encoded data: {encoded}")
    return encoded

# Function to modulate data using BPSK
def bpsk_modulate(data):
    print(f"Modulating data: {data}")
    result = ''.join(['1' if bit == '1' else '0' for bit in data])
    print(f"Modulated data: {result}")
    return result

# TCP Sender
def tcp_sender():
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.connect((TCP_IP, TCP_PORT))
    start_time = time.time()

    for i in range(NUM_PACKETS):
        message = f"[TCP:{i}]".encode()
        encoded_message = encode_data(message)
        binary_message = ''.join(format(ord(char), '08b') for char in encoded_message)
        print(f"Binary message for TCP packet [{i}]: {binary_message}")
        modulated_message = bpsk_modulate(binary_message).encode()
        tcp_socket.send(modulated_message)
        print(f"Sent TCP packet [{i}]: {modulated_message}")
        time.sleep(1)

    tcp_socket.close()
    tcp_time = time.time() - start_time
    print(f"TCP transmission time: {tcp_time:.2f} seconds")

# UDP Sender
def udp_sender():
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    start_time = time.time()

    for i in range(NUM_PACKETS):
        if random.random() < PACKET_DROP_PROBABILITY:
            print(f"Simulated UDP packet drop [{i}]")
            continue

        message = f"[UDP:{i}]".encode()
        encoded_message = encode_data(message)
        binary_message = ''.join(format(ord(char), '08b') for char in encoded_message)
        print(f"Binary message for UDP packet [{i}]: {binary_message}")
        modulated_message = bpsk_modulate(binary_message).encode()
        udp_socket.sendto(modulated_message, (UDP_IP, UDP_PORT))
        print(f"Sent UDP packet [{i}]: {modulated_message}")
        time.sleep(1)

    udp_time = time.time() - start_time
    print(f"UDP transmission time: {udp_time:.2f} seconds")

# Reliable UDP Sender
def reliable_udp_sender():
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    start_time = time.time()
    ack_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ack_socket.bind((UDP_IP, UDP_PORT + 1))

    for i in range(NUM_PACKETS):
        retries = 0
        while retries < MAX_RETRIES:
            message = f"[RUDP:{i}]".encode()
            encoded_message = encode_data(message)
            binary_message = ''.join(format(ord(char), '08b') for char in encoded_message)
            print(f"Binary message for Reliable UDP packet [{i}]: {binary_message}")
            modulated_message = bpsk_modulate(binary_message).encode()
            udp_socket.sendto(modulated_message, (UDP_IP, UDP_PORT))
            print(f"Sent Reliable UDP packet [{i}]: {modulated_message}")

            ack_socket.settimeout(2)
            try:
                ack, _ = ack_socket.recvfrom(1024)
                if ack.decode() == f"ACK:{i}":
                    print(f"Received ACK for Reliable UDP packet [{i}]")
                    break
            except socket.timeout:
                retries += 1
                print(f"Timeout waiting for ACK for Reliable UDP packet [{i}]. Retrying ({retries}/{MAX_RETRIES})...")

        if retries == MAX_RETRIES:
            print(f"Failed to receive ACK for Reliable UDP packet [{i}] after {MAX_RETRIES} retries.")

    udp_socket.close()
    ack_socket.close()
    rudp_time = time.time() - start_time
    print(f"Reliable UDP transmission time: {rudp_time:.2f} seconds")

# Main Execution
tcp_sender()
udp_sender()
reliable_udp_sender()