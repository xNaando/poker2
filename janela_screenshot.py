import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QComboBox, QMessageBox
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt
import win32gui
import win32ui
import win32con
import win32api
from PIL import Image, ImageGrab
import io

# Função para listar janelas abertas
def listar_janelas():
    janelas = []
    def callback(hwnd, _):
        if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd):
            janelas.append((hwnd, win32gui.GetWindowText(hwnd)))
    win32gui.EnumWindows(callback, None)
    return janelas

# Função para capturar screenshot de uma janela
# Agora captura a tela inteira e recorta a área da janela
def capturar_janela(hwnd):
    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    # Captura a tela inteira
    screenshot = ImageGrab.grab()
    # Recorta a área da janela
    img = screenshot.crop((left, top, right, bottom))
    return img

class App(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Captura de Janela do Windows')
        self.setGeometry(100, 100, 800, 600)
        self.layout = QVBoxLayout()

        self.combo = QComboBox()
        self.btn_atualizar = QPushButton('Atualizar Janelas')
        self.btn_capturar = QPushButton('Capturar Screenshot')
        self.label_img = QLabel('A imagem aparecerá aqui')
        self.label_img.setAlignment(Qt.AlignCenter)

        self.layout.addWidget(self.combo)
        self.layout.addWidget(self.btn_atualizar)
        self.layout.addWidget(self.btn_capturar)
        self.layout.addWidget(self.label_img)
        self.setLayout(self.layout)

        self.btn_atualizar.clicked.connect(self.atualizar_janelas)
        self.btn_capturar.clicked.connect(self.capturar_screenshot)

        self.atualizar_janelas()

    def atualizar_janelas(self):
        self.combo.clear()
        self.janelas = listar_janelas()
        for hwnd, titulo in self.janelas:
            self.combo.addItem(f'{titulo} (HWND: {hwnd})', hwnd)

    def capturar_screenshot(self):
        idx = self.combo.currentIndex()
        if idx == -1:
            QMessageBox.warning(self, 'Aviso', 'Selecione uma janela!')
            return
        hwnd = self.combo.itemData(idx)
        img = capturar_janela(hwnd)
        if img is None:
            QMessageBox.warning(self, 'Erro', 'Não foi possível capturar a janela.')
            return
        # Converter PIL Image para QPixmap
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        qt_img = QImage.fromData(buf.getvalue())
        pixmap = QPixmap.fromImage(qt_img)
        self.label_img.setPixmap(pixmap.scaled(700, 400, Qt.KeepAspectRatio))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(app.exec_()) 