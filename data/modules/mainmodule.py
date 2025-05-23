import sys
import os
from pathlib import Path
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto.Random import get_random_bytes
from PyQt5.QtWidgets import QApplication, QWidget, QFileDialog
from PyQt5.QtGui import QIcon
from data.windows.workspace import Ui_Workspace
from data.modules.infomodule import collectinfo
from data.modules.keymodule import formdeckey, formenckey


class Workspace(QWidget, Ui_Workspace):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.fileButton.clicked.connect(self.choosefile)
        self.encryptButton.clicked.connect(self.encrypt)
        self.decryptButton.clicked.connect(self.decrypt)
        self.infoButton.clicked.connect(self.getinfo)
        self.setFixedSize(self.size())

    def choosefile(self):
        self.directory = QFileDialog.getOpenFileName(self, "Выберите файл")[0]
        self.pathEdit.setText(self.directory)

    def encrypt(self):
        self.directory = self.pathEdit.text()
        if os.path.isdir(self.directory) and self.directory[-1] == '/':
            self.directory = self.directory[0:-1]
        self.outdirectory = str(os.path.dirname(os.path.abspath(__file__))) + "\\output\\encrypted\\"
        if not os.path.isdir(self.outdirectory):
            os.mkdir(self.outdirectory)
        if os.path.isfile(self.directory):
            self.filename = self.directory.split('/')[-1]
            self.baseencrypt(self.directory, self.filename)
        elif os.path.isdir(self.directory):
            p = Path(self.directory)
            for file in p.rglob("*"):
                if file.is_file():
                    try:
                        self.filename = str(file).split('\\')[-1]
                        self.baseencrypt(file, self.filename)
                    except Exception as e:
                        print('Файл', str(file), "не был зашифрован. Причина: " + str(e))

    def baseencrypt(self, file, filename):
        self.directory = file
        self.nonce = get_random_bytes(12)
        self.filename = filename
        reqdata = self.choosedata('encrypt')
        passwd = self.passEdit.text().encode('utf-8')
        if passwd:
            password = SHA256.new(passwd).digest()
        else:
            password = b''
        self.key = formenckey(password, reqdata)
        self.enc = AES.new(self.key, AES.MODE_GCM, nonce=self.nonce)
        with open(self.directory, 'rb') as filein, open(self.outdirectory + self.filename, 'wb') as fileout:
            fileout.write(self.nonce)
            while True:
                data = filein.read(1 * 1024 * 1024)
                if not data:
                    break
                self.enc = AES.new(self.key, AES.MODE_GCM, nonce=self.nonce)
                self.enctext = self.enc.encrypt(data)
                fileout.write(self.enctext)
            fileout.write(self.enc.digest())
            print(f'Шифрование файла {self.filename} прошло успешно!')

    def decrypt(self):
        self.directory = self.pathEdit.text()
        if os.path.isfile(self.directory):
            self.basedecrypt(self.directory, False, None)
        elif os.path.isdir(self.directory):
            p = Path(self.directory)
            for file in p.rglob("*"):
                if file.is_file():
                    try:
                        self.tosend = ''
                        file = str(file).replace('\\', '/')
                        self.tosend = str(os.path.dirname(os.path.abspath(__file__))) + "\\output\\decrypted\\"
                        self.basedecrypt(file, True, self.tosend)
                    except Exception as e:
                        print('Файл', str(file), "не был дешифрован. Причина: " + str(e))

    def basedecrypt(self, file, isdir, diroutput):
        password = self.passEdit.text()
        reqdata = self.choosedata('decrypt')
        self.key = formdeckey(password, reqdata)
        self.directory = file
        self.outdirectory = str(os.path.dirname(os.path.abspath(__file__))) + "\\output\\decrypted\\"
        if not isdir:
            if not os.path.isdir(self.outdirectory):
                os.mkdir(self.outdirectory)
            self.filename = self.directory.split('/')[-1]
            outpath = self.outdirectory + self.filename
        else:
            self.filename = self.directory.split('/')[-1]
            outpath = diroutput + self.filename
            if not os.path.isdir(diroutput):
                os.mkdir(diroutput)
        with open(self.directory, 'rb') as filein, open(outpath, 'wb') as fileout:
            file_size = os.path.getsize(self.directory)
            remaining_bytes = file_size - 12 - 16
            self.nonce = filein.read(12)
            try:
                bytes_processed = 0
                while bytes_processed < remaining_bytes:
                    chunk_size = min(1 * 1024 * 1024, remaining_bytes - bytes_processed)
                    chunk = filein.read(chunk_size)
                    if not chunk:
                        break
                    enc = AES.new(self.key, AES.MODE_GCM, nonce=self.nonce)
                    fileout.write(enc.decrypt(chunk))
                    bytes_processed += len(chunk)
                fileout.close()
                print("Файл", self.filename, "был успешно дешифрован.")
            except Exception as e:
                fileout.close()
                if os.path.exists(outpath):
                    os.remove(outpath)
                print(f'Ошибка при дешифровке файла {self.filename}: {e}')

    def getinfo(self):
        data = collectinfo()
        self.macinfoEdit.setText(data[0])
        self.cpuinfoEdit.setText(data[1])
        self.uuidinfoEdit.setText(data[2])
        self.serialinfoEdit.setText(data[3])
        self.gpuserialinfoEdit.setText(data[4])
        self.mbserialinfoEdit.setText(data[5])

    def choosedata(self, datafor):
        mac, cpu_name, system_uuid, disk_serial, gpu_serial, mb_serial = b'', b'', b'', b'', b'', b''
        decdata = []
        if self.macBox.isChecked():
            decdata.append('mac')
            if self.macEdit.text():
                mac = SHA256.new(self.macEdit.text().encode('utf-8')).digest()
        if self.cpuBox.isChecked():
            decdata.append('cpu_name')
            if self.cpuEdit.text():
                cpu_name = SHA256.new(self.cpuEdit.text().encode('utf-8')).digest()
        if self.uuidBox.isChecked():
            decdata.append('system_uuid')
            if self.uuidEdit.text():
                system_uuid = SHA256.new(self.uuidEdit.text().encode('utf-8')).digest()
        if self.diskserialBox.isChecked():
            decdata.append('disk_serial')
            if self.diskserialEdit.text():
                disk_serial = SHA256.new(self.diskserialEdit.text().encode('utf-8')).digest()
        if self.gpuserialBox.isChecked():
            decdata.append('gpu_serial')
            if self.gpuserialEdit.text():
                gpu_serial = SHA256.new(self.gpuserialEdit.text().encode('utf-8')).digest()
        if self.mbserialBox.isChecked():
            decdata.append('mb_serial')
            if self.mbserialEdit.text():
                mb_serial = SHA256.new(self.mbserialEdit.text().encode('utf-8')).digest()
        encdata = [mac, cpu_name, disk_serial, mb_serial, gpu_serial, system_uuid]
        if datafor == 'encrypt':
            return encdata
        elif datafor == 'decrypt':
            return decdata


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('data/icon.ico'))
    window = Workspace()
    window.show()
    sys.exit(app.exec_())
