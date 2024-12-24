import math
import sys
import speech_recognition as sr
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QGuiApplication, QIcon, QPainter, QPalette, QColor, QFont
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QSplitter
)
from transformers import pipeline
from huggingface_hub import login
import torch
from mock import MockReader  # Your provided mock reader
import pyttsx3  # <-- (1) TTS import

class SpeechRecognitionThread(QThread):
    recognizedText = pyqtSignal(str)

    def run(self):
        """Run the speech recognition in a separate thread."""
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            print("Listening for speech...")
            audio = recognizer.listen(source)

        try:
            text = recognizer.recognize_google(audio, language='en-EN')
            self.recognizedText.emit(text)
        except sr.UnknownValueError:
            self.recognizedText.emit("Could not understand the audio.")
        except sr.RequestError as e:
            self.recognizedText.emit(f"Speech recognition service error: {e}")


class MainWindow(QMainWindow):
    def __init__(self, reader):
        super().__init__()
        
        print("Loading LLM model... This may take a while.")

        model_id = "meta-llama/Llama-3.2-1B-Instruct"
        login(token="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")
        
        self.pipe = pipeline(
            "text-generation", 
            model=model_id,
            torch_dtype=torch.bfloat16, 
            device_map="auto"
        )
        
        print("Model loaded.")
        
        # (2) Initialize the TTS engine
        self.tts_engine = pyttsx3.init()
        # Optionally configure voice parameters
        self.tts_engine.setProperty('rate', 150)
        self.tts_engine.setProperty('volume', 1.0)

        self.init_window()

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.splitter = QSplitter(Qt.Horizontal, self)
        self.splitter.setChildrenCollapsible(False)

        ############ RIGHT SIDE ############
        self.wheel_widget = QWidget(self)
        self.wheel_layout = QVBoxLayout()

        self.drawing_title = QLabel("Dokunma Verisi")
        self.drawing_title.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        self.drawing_title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        self.drawing_title.setStyleSheet("color: white")

        self.wheel_drawing = self.WheelDrawingWidget(self)
        self.wheel_drawing.setMinimumSize(300, 300)

        self.wheel_layout.setAlignment(Qt.AlignTop)
        self.wheel_layout.addWidget(self.drawing_title)
        self.wheel_layout.addWidget(self.wheel_drawing)

        self.wheel_widget.setLayout(self.wheel_layout)

        ############ LEFT SIDE ############
        self.text_widget = QWidget(self)
        self.text_layout = QVBoxLayout()
        self.text_widget.setMaximumWidth(300)

        self.accel_title = QLabel("İvmeölçer")
        self.accel_label = QLabel("Accelerometer: Bekleniyor...")

        self.heart_title = QLabel("Kalp Atış Hızı")
        self.heart_label = QLabel("Heart Rate: Bekleniyor...")

        self.gsr_title = QLabel("GSR")
        self.gsr_label = QLabel("GSR: Bekleniyor...")

        self.temp_title = QLabel("Sıcaklık")
        self.temp_label = QLabel("Temperature: Bekleniyor...")

        self.speech_title = QLabel("Konuşma Tanıma")
        self.speech_label = QLabel("Press 'S' to start listening...")
        self.speech_label.setWordWrap(True)

        bold_font = QFont("Arial", 16, QFont.Weight.Bold)
        self.accel_title.setFont(bold_font)
        self.heart_title.setFont(bold_font)
        self.gsr_title.setFont(bold_font)
        self.temp_title.setFont(bold_font)
        self.speech_title.setFont(bold_font)

        self.text_layout.addWidget(self.accel_title)
        self.text_layout.addWidget(self.accel_label)
        self.text_layout.addWidget(self.heart_title)
        self.text_layout.addWidget(self.heart_label)
        self.text_layout.addWidget(self.gsr_title)
        self.text_layout.addWidget(self.gsr_label)
        self.text_layout.addWidget(self.temp_title)
        self.text_layout.addWidget(self.temp_label)

        self.text_layout.addWidget(self.speech_title)
        self.text_layout.addWidget(self.speech_label)

        self.text_widget.setLayout(self.text_layout)
        self.splitter.addWidget(self.text_widget)
        self.splitter.addWidget(self.wheel_widget)

        main_layout = QHBoxLayout()
        main_layout.addWidget(self.splitter)
        self.central_widget.setLayout(main_layout)

        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 1)
        self.splitter.setSizes([500, 500])

        self.reader = reader
        self.reader.data_received.connect(self.update_labels)
        self.reader.start()

        self.touch_data = [0] * 12

        self.speech_thread = SpeechRecognitionThread()
        self.speech_thread.recognizedText.connect(self.on_speech_recognized)

    def interpret_sensor_data(self, mock_data: dict, user_question: str) -> str:
        print(mock_data)
        messages = [
            {
                "role": "system",
                "content": "You are a helpful assistant who provides information about the sensor data to driver."
            },
            {
                "role": "user",
                "content": f"""
                    The sensor readings are:
                    - Human Temperature: {mock_data["temp"]:.2f}
                    - Heart Rate: {mock_data["heart"]:.2f}
                    - GSR: {mock_data["gsr"]:.2f}

                    I also have a question for you regarding these readings:
                    \"{user_question}\"
                """
            }
        ]

        outputs = self.pipe(messages, max_new_tokens=128)
        # The pipeline returns a variety of structures; adjust as needed
        # For demonstration, let's assume the model's text is in an easily accessible field
        response = outputs[0]["generated_text"][-1]['content']
        print(response)

        return response

    def init_window(self):
        screen_geometry = QGuiApplication.primaryScreen().geometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()

        window_width = 6 * screen_width // 10
        window_height = 6 * screen_height // 10

        self.setGeometry(
            (screen_width - window_width) // 2,
            (screen_height - window_height) // 2,
            window_width,
            window_height
        )

        self.setWindowTitle("Akıllı Direksiyon - ÇDTP")
        self.setWindowIcon(QIcon('icon.png'))

    def update_labels(self, data):
        self.latest_data = data
        self.touch_data = data["touch"]
        self.wheel_drawing.set_touch_data(self.touch_data)

        accel_data = data["accelerometer"]
        self.accel_label.setText(f"X={accel_data[0]:.2f}, "
                                 f"Y={accel_data[1]:.2f}, Z={accel_data[2]:.2f}")

        self.heart_label.setText(f"{data['heart']:.2f} BPM")
        self.gsr_label.setText(f"{data['gsr']} ({self.gsr_analysis(data['gsr']).capitalize()})")
        self.temp_label.setText(f"{data['temp']:.2f} °C")

    @staticmethod
    def gsr_analysis(gsr_value):
        if gsr_value < 300:
            return "Low Stress"
        elif gsr_value < 700:
            return "Medium Stress"
        else:
            return "High Stress"

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_S:
            self.speech_label.setText("Listening... (speak now)")
            self.speech_thread.start()
        else:
            super().keyPressEvent(event)

    def on_speech_recognized(self, recognized_text):
        """
        Called by the QThread when speech is recognized.
        """
        self.speech_label.setText(f"Recognized Speech: {recognized_text}")
        answer = self.interpret_sensor_data(self.latest_data, recognized_text)
        self.speech_label.setText(f"Recognized Speech: {recognized_text} \n Answer: {answer}")

        # (3) Text-to-Speech here
        self.tts_engine.say(answer)
        self.tts_engine.runAndWait()

    class WheelDrawingWidget(QWidget):
        def __init__(self, parent=None):
            super().__init__(parent)
            self.touch_data = [0] * 12

        def set_touch_data(self, touch_data):
            self.touch_data = touch_data
            self.update()

        def paintEvent(self, event):
            painter = QPainter(self)
            drawing_area = self.rect()
            center_x = drawing_area.center().x()
            center_y = drawing_area.center().y()
            radius = int(0.4 * min(drawing_area.width(), drawing_area.height()))

            for i in range(12):
                angle = math.radians(-i * 30)
                x = center_x + int(radius * math.cos(angle))
                y = center_y - int(radius * math.sin(angle))
                painter.drawText(x - 10, y - 20, f"{(i * 30 + 90) % 360}°")

                if self.touch_data[(i + 3) % 12] == 1:
                    painter.setBrush(QColor(0, 255, 0))
                else:
                    painter.setBrush(QColor(200, 0, 0))
                painter.setPen(QColor(0, 0, 0))

                ellipse_size = int(radius * 0.1)
                painter.drawEllipse(x - ellipse_size // 2, y - ellipse_size // 2, ellipse_size, ellipse_size)

    def closeEvent(self, event):
        self.reader.stop()
        self.reader.wait()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ToolTipBase, Qt.black)
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.HighlightedText, Qt.black)
    app.setPalette(palette)

    reader = MockReader()
    window = MainWindow(reader)
    window.show()
    sys.exit(app.exec_())