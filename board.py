import serial
from PyQt5.QtCore import QThread, pyqtSignal


class BoardReader(QThread):
    # Arduino'dan gelen veriyi işlemek için bir sinyal
    data_received = pyqtSignal(str)

    def __init__(self, port, baudrate):
        super().__init__()
        self.port = port
        self.baudrate = baudrate
        self.running = True
        self.serial_connection = None

    def run(self):
        # Seri bağlantıyı aç
        try:
            self.serial_connection = serial.Serial(self.port, self.baudrate, timeout=1)
        except serial.SerialException as e:
            print(f"Seri bağlantı hatası: {e}")
            return

        # Arduino'dan veri oku
        while self.running:
            if self.serial_connection.in_waiting > 0:
                line = self.serial_connection.readline().decode('utf-8').strip()
                self.data_received.emit(line)

    def stop(self):
        # Thread'i durdur
        self.running = False
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
