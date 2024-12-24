import random
import time

from PyQt5.QtCore import QThread, pyqtSignal

class MockReader(QThread):
    # Signal that emits both the raw data and the LLM interpretation
    data_received = pyqtSignal(dict)

    def __init__(self, parent=None):
        
        super().__init__(parent)
        self.running = True

    def run(self):
        while self.running:
            # Generate mock data
            mock_data = {
                "touch": [random.choice([0, 1]) for _ in range(12)],
                "accelerometer": [random.uniform(-10, 10) for _ in range(3)],
                "heart": random.uniform(60.0, 100.0),
                "gsr": random.randint(0, 1023),
                "temp": random.uniform(35.0, 39.0)
            }

            # Wait 1 second before generating new data
            self.data_received.emit(mock_data)
            time.sleep(1)
    def stop(self):
        # Stop the thread gracefully
        self.running = False