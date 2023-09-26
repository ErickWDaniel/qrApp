import sys
import uuid
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QGraphicsScene, QMessageBox
from PyQt5.QtGui import QPixmap, QImage
from qrcode import QRCode, constants
from PIL import Image
from cv2 import cv2
from qrcodedesign import Ui_MainWindow

class QRCodeApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setup_signals()
        self.graphics_scene = QGraphicsScene()
        self.ui.graphicsView.setScene(self.graphics_scene)

    def setup_signals(self):
        self.ui.Input_text_lineEdit_Ok_Button.clicked.connect(self.generate_text_qrcode)
        self.ui.Input_whataspp_lineEdit_Ok_Button.clicked.connect(self.generate_whatsapp_qrcode)
        self.ui.save_button.clicked.connect(self.save_image)
        self.ui.open_button.clicked.connect(self.upload_image)
        self.ui.close_button.clicked.connect(self.close_application)
        self.ui.decode_button.clicked.connect(self.decode_qrcode)

        # Connect "Open" action in the menu to upload_image()
        self.ui.actionOpen.triggered.connect(self.upload_image)

        # Connect "Save" action in the menu to save_image()
        self.ui.actionSave.triggered.connect(self.save_image)

        # Connect "Exit" action in the menu to close_application()
        self.ui.actionExit.triggered.connect(self.close_application)

    def generate_qrcode(self, data):
        try:
            qr = QRCode(version=1, error_correction=constants.ERROR_CORRECT_L, box_size=10, border=4)
            qr.add_data(data)
            qr.make(fit=True)
            img = qr.make_image(fill='black', back_color='white')
            self.display_qrcode(img)
            self.clear_input_fields()
        except Exception as e:
            self.show_error_message("Error generating QR code", str(e))

    def generate_text_qrcode(self):
        data = self.ui.Input_text_lineEdit.text()
        if data:
            self.generate_qrcode(data)

    def generate_whatsapp_qrcode(self):
        whatsapp_text = self.ui.Input_text_whatsapp_lineEdit.text()
        if whatsapp_text:
            input_text = f'https://wa.me/{whatsapp_text}'
            self.generate_qrcode(input_text)

    def display_qrcode(self, img):
        temp_filename = 'temp_qrcode.png'
        img.save(temp_filename)
        pixmap = QPixmap(temp_filename)
        self.graphics_scene.clear()
        self.graphics_scene.addPixmap(pixmap)

    def save_image(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Image", "", "Images (*.png);;All Files (*)")
        if file_path:
            pixmap = self.ui.graphicsView.grab().toImage()
            pixmap.save(file_path)
            self.show_info_message("Image Saved", "Image saved successfully.")

    def upload_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Upload Image", "", "Images (*.png *.jpg *.jpeg *.gif)")
        if file_path:
            self.display_image(file_path)
            self.clear_input_fields()

    def display_image(self, file_path):
        img = Image.open(file_path)
        img_np = np.array(img)
        que_img = QImage(img_np.data, img_np.shape[1], img_np.shape[0], img_np.strides[0], QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(que_img)
        self.graphics_scene.clear()
        self.graphics_scene.addPixmap(pixmap)

    def decode_qrcode(self):
        try:
            unique_filename = str(uuid.uuid4()) + ".png"
            image_path = unique_filename
            pixmap = self.ui.graphicsView.grab().toImage()
            pixmap.save(image_path)
            img_np = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
            detector = cv2.QRCodeDetector()
            retval, decoded_info, points, straight_qrcode = detector.detectAndDecodeMulti(img_np)
            if retval:
                decoded_data = ' '.join(decoded_info)
                self.display_decoded_message(decoded_data)
                self.clear_input_fields()
            else:
                self.show_warning_message("QR Code Decoding", "No QR code found in the image.")
        except Exception as e:
            self.show_error_message("Error decoding QR code", str(e))

    def display_decoded_message(self, decoded_data):
        QMessageBox.information(self, "Decoded Message", f"Message:\n{decoded_data}")

    def clear_input_fields(self):
        self.ui.Input_text_lineEdit.clear()
        self.ui.Input_text_whatsapp_lineEdit.clear()

    def close_application(self):
        self.close()

    def show_info_message(self, title, message):
        QMessageBox.information(self, title, message)

    def show_warning_message(self, title, message):
        QMessageBox.warning(self, title, message)

    def show_error_message(self, title, message):
        QMessageBox.critical(self, title, message)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = QRCodeApp()
    mainWindow.show()
    sys.exit(app.exec_())
