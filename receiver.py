# receiver.py
import socket
import time
import base64

# Configuration
TCP_PORT = 5005
UDP_PORT = 5005
NUM_PACKETS = 6

# Function to decode data
def decode_data(data):
    decoded = base64.b64decode(data).decode('utf-8')
    print(f"Decoded data: {decoded}")
    return decoded

# Function to demodulate data using BPSK
def bpsk_demodulate(data):
    print(f"Demodulating data: {data}")
    result = ''.join(['1' if bit == '1' else '0' for bit in data])
    print(f"Demodulated data: {result}")
    return result

# TCP Receiver
def tcp_receiver():
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.bind(("", TCP_PORT))
    tcp_socket.listen(1)
    conn, addr = tcp_socket.accept()
    print(f"TCP Connection established with {addr}")

    start_time = time.time()
    for i in range(NUM_PACKETS):
        data = conn.recv(1024)
        if not data:
            print(f"No TCP data received for packet [{i}]")
            continue

        print(f"Received raw TCP data: {data}")
        demodulated_data = bpsk_demodulate(data)
        binary_data = int(demodulated_data, 2).to_bytes((len(demodulated_data) + 7) // 8, byteorder='big')
        decoded_data = decode_data(binary_data)
        print(f"Decoded TCP packet [{i}]: {decoded_data}")

    tcp_socket.close()
    tcp_time = time.time() - start_time
    print(f"TCP reception time: {tcp_time:.2f} seconds")

# UDP Receiver
def udp_receiver():
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind(("", UDP_PORT))
    print("UDP Receiver ready")

    start_time = time.time()
    for i in range(NUM_PACKETS):
        try:
            data, addr = udp_socket.recvfrom(1024)
            print(f"Received raw UDP data: {data}")

            demodulated_data = bpsk_demodulate(data)
            binary_data = int(demodulated_data, 2).to_bytes((len(demodulated_data) + 7) // 8, byteorder='big')
            decoded_data = decode_data(binary_data)
            print(f"Decoded UDP packet [{i}]: {decoded_data}")
        except Exception as e:
            print(f"Error receiving UDP packet [{i}]: {e}")

    udp_time = time.time() - start_time
    print(f"UDP reception time: {udp_time:.2f} seconds")

# Reliable UDP Receiver
def reliable_udp_receiver():
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind(("", UDP_PORT))
    ack_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print("Reliable UDP Receiver ready")

    start_time = time.time()
    for i in range(NUM_PACKETS):
        while True:
            try:
                data, addr = udp_socket.recvfrom(1024)
                print(f"Received raw Reliable UDP data: {data}")

                demodulated_data = bpsk_demodulate(data)
                binary_data = int(demodulated_data, 2).to_bytes((len(demodulated_data) + 7) // 8, byteorder='big')
                decoded_data = decode_data(binary_data)
                print(f"Decoded Reliable UDP packet [{i}]: {decoded_data}")

                ack_message = f"ACK:{i}".encode()
                ack_socket.sendto(ack_message, addr)
                print(f"Sent ACK for Reliable UDP packet [{i}]")
                break
            except Exception as e:
                print(f"Error receiving Reliable UDP packet [{i}]: {e}")

    udp_socket.close()
    ack_socket.close()
    rudp_time = time.time() - start_time
    print(f"Reliable UDP reception time: {rudp_time:.2f} seconds")

# Main Execution
tcp_receiver()
udp_receiver()
reliable_udp_receiver()
