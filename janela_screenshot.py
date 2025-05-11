import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QComboBox, QMessageBox, QFrame, QTextEdit
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt
import win32gui
import win32ui
import win32con
import win32api
from PIL import Image, ImageGrab
import io
import base64
import requests

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
        self.label_img = QLabel()
        self.label_img.setAlignment(Qt.AlignCenter)
        self.label_img.setMinimumHeight(400)
        self.label_img.setStyleSheet('background: #f0f0f0; border: 1px solid #ccc;')

        self.btn_analisar = QPushButton('Analisar')
        self.btn_analisar.setEnabled(False)
        self.resposta_card = QTextEdit()
        self.resposta_card.setReadOnly(True)
        self.resposta_card.setFrameStyle(QFrame.Panel | QFrame.Raised)
        self.resposta_card.setStyleSheet('background: #e8f5e9; font-size: 18px;')
        self.resposta_card.hide()

        self.layout.addWidget(self.combo)
        self.layout.addWidget(self.btn_atualizar)
        self.layout.addWidget(self.btn_capturar)
        self.layout.addWidget(self.label_img, stretch=1)
        self.layout.addWidget(self.btn_analisar)
        self.layout.addWidget(self.resposta_card)
        self.setLayout(self.layout)

        self.btn_atualizar.clicked.connect(self.atualizar_janelas)
        self.btn_capturar.clicked.connect(self.capturar_screenshot)
        self.btn_analisar.clicked.connect(self.analisar_imagem)

        self.atualizar_janelas()
        self.img_capturada = None

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
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        qt_img = QImage.fromData(buf.getvalue())
        pixmap = QPixmap.fromImage(qt_img)
        self.label_img.setPixmap(pixmap.scaled(700, 400, Qt.KeepAspectRatio))
        self.img_capturada = buf.getvalue()
        self.btn_analisar.setEnabled(True)
        self.resposta_card.hide()

    def analisar_imagem(self):
        if not self.img_capturada:
            QMessageBox.warning(self, 'Aviso', 'Capture uma imagem primeiro!')
            return
        prompt = 'me fale qual a jogada mais lucrativa nessa mão de poker. quero que me responda apenas: "FOLD, CALL, CHECK, RAISE X"'
        img_b64 = base64.b64encode(self.img_capturada).decode('utf-8')
        try:
            resp = requests.post('http://127.0.0.1:5000/analisar', json={
                'prompt': prompt,
                'image': img_b64
            }, timeout=120)
            if resp.status_code == 200:
                resposta = resp.json().get('resposta', 'Sem resposta')
                self.resposta_card.setText(resposta)
                self.resposta_card.show()
            else:
                erro = resp.json().get('erro', 'Erro desconhecido')
                self.resposta_card.setText(f'Erro: {erro}')
                self.resposta_card.show()
        except Exception as e:
            self.resposta_card.setText(f'Erro ao conectar ao backend: {e}')
            self.resposta_card.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(app.exec_()) 