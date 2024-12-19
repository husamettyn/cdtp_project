import random
import time
from PyQt5.QtCore import QThread, pyqtSignal

class MockReader(QThread):
    # Sahte veriyi işlemek için bir sinyal
    data_received = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.running = True

    def run(self):
        while self.running:
            # Hangi verini hangi türde geleceği varsayımı aşağıda verilmiştir:
            # touch: 12 uzunluğunda 0, 1 dizisi > [0, 1, 0, 0, 1, ...]
            # accelometer: 3 elemanlı dizi > [x, y, z]
            # heart: işlenmiş olarak gelirse FLOAT, işlenmemişse burada işlenebilir.
            # gsr: 0-1023 arasında INT (bundan ayrıca anlam çıkarılmalı)
            # temp: FLOAT, santigrat derece
            mock_data = {
                "touch": [random.choice([0, 1]) for _ in range(12)],  # 12 uzunluğunda 0/1 dizisi - [0, 0, 0, 0, 1, 1, 0, 1, 0, 1, 1, 1,]
                "accelerometer": [random.uniform(-10, 10) for _ in range(3)],  # x, y, z değerleri
                "heart": random.uniform(60.0, 100.0),  # FLOAT, BPM
                "gsr": random.randint(0, 1023),  # 0-1023 arasında INT
                "temp": random.uniform(35.0, 39.0)  # FLOAT, santigrat derece
            }
            self.data_received.emit(mock_data)
            time.sleep(1)  # 1 saniye bekle

    def stop(self):
        # Thread'i durdur
        self.running = False
