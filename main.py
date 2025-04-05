import sys
import os
from pathlib import Path
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto.Random import get_random_bytes
from PyQt5.QtWidgets import QApplication, QWidget, QFileDialog
from static.workspace import Ui_Workspace


class Workspace(QWidget, Ui_Workspace):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.fileButton.clicked.connect(self.choosefile)
        self.encryptButton.clicked.connect(self.encrypt)
        self.decryptButton.clicked.connect(self.decrypt)

    def choosefile(self):
        self.directory = QFileDialog.getOpenFileName(self, "Выберите файл")[0]
        self.pathEdit.setText(self.directory)

    def encrypt(self):
        self.directory = self.pathEdit.text()
        directorylist = self.directory.split('/')[0:-1]
        self.outdirectory = ''
        for i in directorylist:
            self.outdirectory += i
            self.outdirectory += '/'
        self.outdirectory += 'output/'
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
        self.key = self.passEdit.text().encode('utf-8')
        self.key = SHA256.new(self.key).digest()
        self.nonce = get_random_bytes(12)
        self.filename = filename
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
            print('Шифрование прошло успешно!')

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
                        for i in file.split('/')[0:-2]:
                            self.tosend += i
                            self.tosend += '/'
                        self.tosend += 'output/'
                        self.basedecrypt(file, True, self.tosend)
                    except Exception as e:
                        print('Файл', str(file), "не был дешифрован. Причина: " + str(e))

    def basedecrypt(self, file, isdir, diroutput):
        self.key = self.passEdit.text().encode('utf-8')
        self.key = SHA256.new(self.key).digest()
        self.directory = file
        with open(self.directory, 'rb') as filein:
            self.nonce = filein.read(12)
            enc = AES.new(self.key, AES.MODE_GCM, nonce=self.nonce)
            file_size = os.path.getsize(self.directory)
            remaining_bytes = file_size - 12 - 16
            directorylist = self.directory.split('/')[0:-1]
            self.filename = self.directory.split('/')[-1]
            self.outdirectory = ''
            for i in directorylist:
                self.outdirectory += i
                self.outdirectory += '/'
            self.outdirectory += 'output/'
            if not isdir:
                if not os.path.isdir(self.outdirectory):
                    os.mkdir(self.outdirectory)
                temp_path = self.outdirectory + self.filename + '.tmp'
            else:
                temp_path = diroutput + self.filename + '.tmp'
                if not os.path.isdir(diroutput):
                    os.mkdir(diroutput)
            try:
                with open(temp_path, 'wb') as fileout:
                    bytes_processed = 0
                    while bytes_processed < remaining_bytes:
                        chunk_size = min(1 * 1024 * 1024, remaining_bytes - bytes_processed)
                        chunk = filein.read(chunk_size)
                        if not chunk:
                            break
                        fileout.write(enc.decrypt(chunk))
                        bytes_processed += len(chunk)
                        fileout.close()
                        if os.path.isfile(temp_path.replace('.tmp', '')):
                            os.remove(temp_path.replace('.tmp', ''))
                        os.rename(temp_path, temp_path.replace('.tmp', ''))
                print("Файл", self.filename, "был успешно дешифрован.")
            except Exception as e:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                print(f'Ошибка при дешифровке файла {self.filename}: {e}')


def main():
    app = QApplication(sys.argv)
    window = Workspace()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
