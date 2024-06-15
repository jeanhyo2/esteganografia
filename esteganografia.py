from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QPushButton, QFileDialog, QTextEdit, QMessageBox
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from PIL import Image
import sys

class SteganographyApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Steganography App")
        self.setGeometry(100, 100, 600, 400)

        self.image_label = QLabel("No Image Loaded", self)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.text_edit = QTextEdit(self)
        
        self.load_image_button = QPushButton("Load Image", self)
        self.load_image_button.clicked.connect(self.load_image)

        self.encode_button = QPushButton("Encode Text into Image", self)
        self.encode_button.clicked.connect(self.encode_text)

        self.decode_button = QPushButton("Decode Text from Image", self)
        self.decode_button.clicked.connect(self.decode_text)

        layout = QVBoxLayout()
        layout.addWidget(self.image_label)
        layout.addWidget(self.text_edit)
        layout.addWidget(self.load_image_button)
        layout.addWidget(self.encode_button)
        layout.addWidget(self.decode_button)

        container = QLabel()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.image_path = None

    def load_image(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Image File", "", "Image Files (*.png *.jpg *.bmp)", options=options)
        if file_name:
            self.image_path = file_name
            pixmap = QPixmap(file_name)
            self.image_label.setPixmap(pixmap.scaled(self.image_label.width(), self.image_label.height(), Qt.KeepAspectRatio))

    def encode_text(self):
        if not self.image_path:
            QMessageBox.warning(self, "Warning", "No image loaded")
            return

        text = self.text_edit.toPlainText()
        if not text:
            QMessageBox.warning(self, "Warning", "No text to encode")
            return

        image = Image.open(self.image_path)
        encoded_image = self.encode_image(image, text)
        save_path, _ = QFileDialog.getSaveFileName(self, "Save Encoded Image", "", "PNG Files (*.png);;All Files (*)")
        if save_path:
            encoded_image.save(save_path)
            QMessageBox.information(self, "Success", "Text encoded into image successfully")

    def decode_text(self):
        if not self.image_path:
            QMessageBox.warning(self, "Warning", "No image loaded")
            return

        image = Image.open(self.image_path)
        decoded_text = self.decode_image(image)
        self.text_edit.setPlainText(decoded_text)

    def encode_image(self, image, text):
        encoded_image = image.copy()
        width, height = image.size
        text += chr(0)  # Add null character to signify the end of text

        binary_text = ''.join([format(ord(char), '08b') for char in text])
        data_index = 0
        for x in range(width):
            for y in range(height):
                if data_index < len(binary_text):
                    pixel = list(image.getpixel((x, y)))
                    for n in range(3):  # Modify the RGB values
                        if data_index < len(binary_text):
                            pixel[n] = int(format(pixel[n], '08b')[:-1] + binary_text[data_index], 2)
                            data_index += 1
                    encoded_image.putpixel((x, y), tuple(pixel))
                else:
                    return encoded_image
        return encoded_image

    def decode_image(self, image):
        binary_text = ""
        width, height = image.size
        for x in range(width):
            for y in range(height):
                pixel = list(image.getpixel((x, y)))
                for n in range(3):  # Read the RGB values
                    binary_text += format(pixel[n], '08b')[-1]
        chars = [chr(int(binary_text[i:i+8], 2)) for i in range(0, len(binary_text), 8)]
        decoded_text = ''.join(chars)
        null_index = decoded_text.find(chr(0))
        if null_index != -1:
            decoded_text = decoded_text[:null_index]
        return decoded_text

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SteganographyApp()
    window.show()
    sys.exit(app.exec_())
