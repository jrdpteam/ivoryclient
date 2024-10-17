import sys
import socket
import threading
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QTextEdit, 
                             QVBoxLayout, QWidget, QLineEdit, QComboBox, 
                             QCheckBox, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal, QThread
import re
import socks
import urllib.parse


class ClientThread(QThread):
    data_received = pyqtSignal(str)

    def __init__(self, socket, buffer_size, output_widget):
        super().__init__()
        self.socket = socket
        self.buffer_size = buffer_size
        self.output_widget = output_widget
        self.running = True

    def run(self):
        while self.running:
            try:
                data = self.socket.recv(self.buffer_size)
                if data:
                    message = data.decode()
                    self.data_received.emit(message)
                else:
                    self.running = False
            except ConnectionResetError:
                self.data_received.emit("Connection was reset by the server.")
                self.running = False
            except Exception as e:
                self.data_received.emit(f"Error receiving data: {e}")
                self.running = False

    def stop(self):
        self.running = False
        self.socket.close()


class IvoryClient(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("IvoryClient TCP")
        self.setGeometry(300, 300, 600, 400)

        self.socket = None
        self.buffer_size = 1024

        self.init_menu_ui()

    def init_menu_ui(self):
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        layout = QVBoxLayout()

        self.url_input = QLineEdit(self)
        self.url_input.setPlaceholderText("Enter URL (e.g., tcp://127.0.0.1:12345 or tcp://example.onion:12345)")
        layout.addWidget(self.url_input)

        self.buffer_size_input = QLineEdit(self)
        self.buffer_size_input.setPlaceholderText("Enter buffer size")
        layout.addWidget(self.buffer_size_input)

        self.buffer_unit_selector = QComboBox(self)
        self.buffer_unit_selector.addItems(["b", "kB", "MB"])
        layout.addWidget(self.buffer_unit_selector)

        self.proxy_checkbox = QCheckBox("Use SOCKS5 proxy", self)
        layout.addWidget(self.proxy_checkbox)

        self.proxy_input = QLineEdit(self)
        self.proxy_input.setPlaceholderText("Enter SOCKS5 proxy (e.g., 127.0.0.1:9050)")
        self.proxy_input.setEnabled(False)
        layout.addWidget(self.proxy_input)

        self.proxy_checkbox.toggled.connect(self.toggle_proxy_input)

        self.connect_button = QPushButton("Connect", self)
        self.connect_button.clicked.connect(self.connect_to_server)
        layout.addWidget(self.connect_button, alignment=Qt.AlignLeft | Qt.AlignBottom)

        self.central_widget.setLayout(layout)

    def toggle_proxy_input(self):
        if self.proxy_checkbox.isChecked():
            self.proxy_input.setEnabled(True)
        else:
            self.proxy_input.setEnabled(False)

    def connect_to_server(self):
        url = self.url_input.text()
        buffer_size_str = self.buffer_size_input.text()
        buffer_unit = self.buffer_unit_selector.currentText()

        proxy = self.proxy_input.text() if self.proxy_checkbox.isChecked() else None

        if not url.startswith("tcp://"):
            self.output.append("<span style='color:red'>Invalid URL format. Please use 'tcp://'</span>")
            return

        try:
            parsed_url = self.parse_url(url)
            ip_or_domain, port = parsed_url
        except ValueError:
            self.output.append("<span style='color:red'>Invalid URL format. Example: tcp://127.0.0.1:12345</span>")
            return
        
        try:
            if buffer_size_str:
                buffer_size = int(buffer_size_str)
                if buffer_unit == "kB":
                    self.buffer_size = buffer_size * 1024
                elif buffer_unit == "MB":
                    self.buffer_size = buffer_size * 1024 * 1024
                else:
                    self.buffer_size = buffer_size
            else:
                self.buffer_size = 1024

            if proxy:
                proxy_ip, proxy_port = proxy.split(':')
                self.socket = socks.socksocket()
                self.socket.set_proxy(socks.SOCKS5, proxy_ip, int(proxy_port), True)
            else:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            self.socket.connect((ip_or_domain, int(port)))
            self.running = True
            self.init_chat_ui(f"<span style='color:green'>Connected to {ip_or_domain}:{port}, connection type: TCP</span>")
            
            self.client_thread = ClientThread(self.socket, self.buffer_size, self.output)
            self.client_thread.data_received.connect(self.display_received_message)
            self.client_thread.start()
        except Exception as e:
            self.output.append(f"<span style='color:red'>Connection error: {e}</span>")

    def parse_url(self, url):
        parsed_url = urllib.parse.urlparse(url)
        if parsed_url.scheme != "tcp":
            raise ValueError("Invalid scheme. Use 'tcp'")
        if parsed_url.netloc:
            domain = parsed_url.hostname
            port = parsed_url.port
            if port is None:
                raise ValueError("No port specified")
            return domain, port
        raise ValueError("Invalid URL format. Example: tcp://example.onion:12345")

    def init_chat_ui(self, connection_message):
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        layout = QVBoxLayout()

        self.output = QTextEdit(self)
        self.output.setReadOnly(True)
        self.output.setStyleSheet("background-color: black; color: white;")
        layout.addWidget(self.output)

        self.output.append(connection_message)

        self.input = QLineEdit(self)
        self.input.setPlaceholderText("Enter message...")
        self.input.returnPressed.connect(self.send_message)
        layout.addWidget(self.input)

        self.send_button = QPushButton("Send", self)
        self.send_button.clicked.connect(self.send_message)
        layout.addWidget(self.send_button)

        self.back_button = QPushButton("Back to Menu", self)
        self.back_button.clicked.connect(self.disconnect_and_return)
        layout.addWidget(self.back_button)

        self.central_widget.setLayout(layout)

    def send_message(self):
        message = self.input.text()
        if self.socket:
            self.socket.sendall(message.encode())
            self.output.append(f"<span style='color:blue'>Sent: {message}</span>")
            self.input.clear()

    def display_received_message(self, message):
        self.output.append(self.apply_ansi_colors(f"Response: \n{message}"))

    def apply_ansi_colors(self, text):
        ansi_escape = re.compile(r'\x1B\[[0-?9;]*[mK]')
        replacements = {
            '30': 'color: black;',
            '31': 'color: red;',
            '32': 'color: green;',
            '33': 'color: yellow;',
            '34': 'color: blue;',
            '35': 'color: magenta;',
            '36': 'color: cyan;',
            '37': 'color: white;',
            '90': 'color: gray;'
        }

        text = ansi_escape.sub('', text)

        for ansi_code, html_color in replacements.items():
            text = ansi_escape.sub(f"<span style='{html_color}'>", text)

        return text

    def disconnect_and_return(self):
        if self.socket:
            self.running = False
            self.socket.close()
            self.socket = None
            self.output.append("<span style='color:green'>Disconnected</span>")
        
        self.init_menu_ui()


### no bloat here bro  o _ o

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = IvoryClient()
    window.show()
    sys.exit(app.exec_())
