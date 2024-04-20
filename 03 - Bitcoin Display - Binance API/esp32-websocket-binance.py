#Trying to use websocket for data
#on micropython v1.22.2

import usocket as socket
import ssl
import ujson as json
import network

# Connect to the Wi-Fi network
sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
sta_if.connect("wifi_ssid", "wifi_password")

# Wait until connected
while not sta_if.isconnected():
    pass

# Symbol to track
symbol = "BTCUSDT"

# Binance WebSocket URL
url = f"data-stream.binance.vision"
path = f"/ws/{symbol.lower()}@kline_1m"

# Connect to the WebSocket server
ws = socket.socket()
addr = socket.getaddrinfo(url, 443)[0][-1]
s = socket.socket()
s.connect(addr)
s = ssl.wrap_socket(s)

# Perform the WebSocket handshake
s.write("GET {} HTTP/1.1\r\n".format(path).encode())
s.write("Host: {}\r\n".format(url).encode())
s.write("Upgrade: websocket\r\n".encode())
s.write("Connection: Upgrade\r\n".encode())
s.write("Sec-WebSocket-Key: x3JJHMbDL1EzLkh9GBhXDw==\r\n".encode())
s.write("Sec-WebSocket-Version: 13\r\n".encode())
s.write("\r\n".encode())

# Main loop to receive and process messages
while True:
    data = s.read(1024)
    if data:
        print(str(data) + '\n')

# Close the WebSocket connection
s.close()
