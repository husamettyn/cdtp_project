import math
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QHBoxLayout, QWidget, QSplitter
from PyQt5.QtGui import QGuiApplication, QIcon, QPainter
from mock import MockReader
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QColor, QFont

class MainWindow(QMainWindow):
    def __init__(self, reader):
        super().__init__()
        
        self.init_window()

        # Ana widget ve layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # QSplitter ile sağ ve sol blokları oluştur
        self.splitter = QSplitter(Qt.Horizontal, self)
        self.splitter.setChildrenCollapsible(False)

        
        ############ RIGHT SIDE ############
        self.wheel_widget = QWidget(self)
        self.wheel_layout = QVBoxLayout()
              
        self.drawing_title = QLabel("Dokunma Verisi")
        self.drawing_title.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        self.drawing_title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        self.drawing_title.setStyleSheet("color: white")
        
        # Wheel layout
        self.wheel_drawing = self.WheelDrawingWidget(self)
        self.wheel_drawing.setMinimumSize(300, 300)  # Minimum boyut
        
        self.wheel_layout.setAlignment(Qt.AlignTop)
        self.wheel_layout.addWidget(self.drawing_title)
        self.wheel_layout.addWidget(self.wheel_drawing)

        self.wheel_widget.setLayout(self.wheel_layout)
        
        
        ############ LEFT SIDE ############
        self.text_widget = QWidget(self)
        self.text_layout = QVBoxLayout()
        self.text_widget.setMaximumWidth(300)

        # QLabel'ler
        self.accel_title = QLabel("İvmeölçer")
        self.accel_label = QLabel("Accelerometer: Bekleniyor...")
        
        self.heart_title = QLabel("Kalp Atış Hızı")
        self.heart_label = QLabel("Heart Rate: Bekleniyor...")
        
        self.gsr_title = QLabel("GSR")
        self.gsr_label = QLabel("GSR: Bekleniyor...")
        
        self.temp_title = QLabel("Sıcaklık")
        self.temp_label = QLabel("Temperature: Bekleniyor...")
        
        self.accel_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.heart_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.gsr_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.temp_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        
        self.accel_title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        self.heart_title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        self.gsr_title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        self.temp_title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        
        # QLabel'leri sağ layout'a ekle
        self.text_layout.addWidget(self.accel_title)
        self.text_layout.addWidget(self.accel_label)
        self.text_layout.addWidget(self.heart_title)
        self.text_layout.addWidget(self.heart_label)
        self.text_layout.addWidget(self.gsr_title)
        self.text_layout.addWidget(self.gsr_label)
        self.text_layout.addWidget(self.temp_title)
        self.text_layout.addWidget(self.temp_label)

        self.text_widget.setLayout(self.text_layout)
        
        
        ############ SPLITTER ############
        self.splitter.addWidget(self.text_widget)
        self.splitter.addWidget(self.wheel_widget)

        # Splitter'ı ana widget'a yerleştir
        main_layout = QHBoxLayout()
        main_layout.addWidget(self.splitter)
        self.central_widget.setLayout(main_layout)

        # Sağ ve sol blokların boyutlarını eşit olarak ayarla
        self.splitter.setStretchFactor(0, 1)  # Sol taraf
        self.splitter.setStretchFactor(1, 1)  # Sağ taraf
        self.splitter.setSizes([500, 500])  # Başlangıç boyutları


        ############ READER ############
        # Veri okuyucusunu bağla
        self.reader = reader
        self.reader.data_received.connect(self.update_labels)
        self.reader.start()

        # Başlangıç için touch_data
        self.touch_data = [0] * 12

    def init_window(self):
        # Ekran boyutlarını al
        screen_geometry = QGuiApplication.primaryScreen().geometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()

        # Pencere boyutlarını ekranın yarısı olarak ayarla
        window_width = 6 * screen_width // 10
        window_height = 6 * screen_height // 10

        # Pencere boyutunu ve pozisyonunu ayarla
        self.setGeometry(
            (screen_width - window_width) // 2,  # X pozisyonu (ortala)
            (screen_height - window_height) // 2,  # Y pozisyonu (ortala)
            window_width,  # Genişlik
            window_height  # Yükseklik
        )

        self.setWindowTitle("Akıllı Direksiyon - ÇDTP")
        self.setWindowIcon(QIcon('icon.png'))

    def update_labels(self, data):
        # LABEL Güncellemeleri
        self.touch_data = data["touch"]
        self.wheel_drawing.set_touch_data(self.touch_data)  # Yeni veri gönder
        self.accel_label.setText(f"X={data['accelerometer'][0]:.2f}, "
                                 f"Y={data['accelerometer'][1]:.2f}, Z={data['accelerometer'][2]:.2f}")
        self.heart_label.setText(f"{data['heart']:.2f} BPM")
        self.gsr_label.setText(f"{data['gsr']} ({self.gsr_analysis(data['gsr']).capitalize()})")
        self.temp_label.setText(f"{data['temp']:.2f} °C")

    @staticmethod
    def gsr_analysis(gsr_value):
        # GSR değerinden anlam çıkar
        if gsr_value < 300:
            return "Low Stress"
        elif gsr_value < 700:
            return "Medium Stress"
        else:
            return "High Stress"
        
    class WheelDrawingWidget(QWidget):
        def __init__(self, parent=None):
            super().__init__(parent)
            self.touch_data = [0] * 12  # Default touch data

        def set_touch_data(self, touch_data):
            self.touch_data = touch_data
            self.update()  # Trigger repaint

        def paintEvent(self, event):
            painter = QPainter(self)
            drawing_area = self.rect()
            center_x = drawing_area.center().x()
            center_y = drawing_area.center().y()
            radius = int(0.4 * min(drawing_area.width(), drawing_area.height()))

            for i in range(12):
                angle = math.radians(-i * 30)  # Saat yönünde açı azalır
                x = center_x + int(radius * math.cos(angle))
                y = center_y - int(radius * math.sin(angle))
                painter.drawText(x - 10, y - 20, f"{(i * 30 + 90) % 360}°")

                if self.touch_data[(i + 3) % 12] == 1:
                    painter.setBrush(QColor(0, 255, 0))  # Aktif: Yeşil
                else:
                    painter.setBrush(QColor(200, 0, 0))  # Pasif: Daha koyu kırmızı
                painter.setPen(QColor(0, 0, 0))  # Çerçeve rengi

                ellipse_size = int(radius * 0.1)  # Çap, radius'a bağlı olarak %10
                painter.drawEllipse(x - ellipse_size // 2, y - ellipse_size // 2, ellipse_size, ellipse_size)
                
    def closeEvent(self, event):
        # Uygulama kapandığında thread'i durdur
        self.reader.stop()
        self.reader.wait()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Force the style to be the same on all OSs:
    app.setStyle("Fusion")

    # Now use a palette to switch to dark colors:
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

    # Mock okuyucu
    reader = MockReader()

    window = MainWindow(reader)
    window.show()
    sys.exit(app.exec_())
