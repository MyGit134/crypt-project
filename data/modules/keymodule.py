import uuid
import platform
import subprocess
import psutil
from Crypto.Hash import SHA256


def formdeckey(passwd: str, data: list):
    if passwd:
        password = SHA256.new(passwd.encode('utf-8')).digest()
    else:
        password = b''
    mac, cpu, cpu_name, disk, system_uuid, disk_serial, gpu_serial, mb_serial = b'', b'', b'', b'', b'', b'', b'', b''
    for i in data:
        if i == 'mac':
            try:
                mac = SHA256.new(':'.join(f'{b:02x}' for b in uuid.getnode().to_bytes(6, 'big')).encode('utf-8')) \
                    .digest()
            except Exception as e:
                print(f'Ошибка при попытке получения MAC адреса: {str(e)}')
        if i == 'cpu_name':
            try:
                if platform.system() == "Windows":
                    cpu = platform.processor()
                elif platform.system() == 'Darwin':
                    cpu = subprocess.check_output("sysctl -n machdep.cpu.brand_string", shell=True).decode().strip()
                else:
                    with open('/proc/cpuinfo', 'r') as f:
                        for line in f:
                            if 'model name' in line:
                                cpu = line.split(':')[1].strip()
                cpu_name = SHA256.new(cpu.encode('utf-8')).digest()
            except Exception as e:
                print(f'Ошибка при попытке получения данных о процессоре: {str(e)}')
        if i == 'disk_serial':
            try:
                if platform.system() == "Windows":
                    disk = \
                        subprocess.check_output("wmic diskdrive get serialnumber", shell=True).decode().split("\n")[
                            1].strip()
                elif platform.system() == 'Darwin':
                    disk = subprocess.check_output("diskutil info disk0 | grep 'Serial Number'",
                                                   shell=True, timeout=5).decode().split(
                        ':')[1].strip()
                else:
                    for item in psutil.disk_partitions():
                        try:
                            cmd = ""
                            if item.device.startswith('/dev/sd') or item.device.startswith('/dev/nvme'):
                                cmd = f"sudo smartctl -i {item.device} | grep 'Serial Number'" if 'nvme' in item.device \
                                    else f"sudo hdparm -I {item.device} | grep 'Serial Number'"
                            disk = subprocess.check_output(cmd, shell=True, timeout=5).decode().split(':')[1].strip()
                            break
                        except Exception as e:
                            print(f'Ошибка при попытке получения данных о диске: {str(e)}')
                            continue
                disk = disk.replace('.', '')
                disk_serial = SHA256.new(disk.encode('utf-8')).digest()
            except Exception as e:
                print(f'Ошибка при попытке получения данных о диске: {str(e)}')
        if i == 'system_uuid':
            try:
                if platform.system() == "Windows":
                    sys_uuid = subprocess.check_output("wmic csproduct get uuid", shell=True). \
                        decode().split('\n')[1].strip()
                else:
                    sys_uuid = subprocess.check_output("sudo dmidecode -s system-uuid", shell=True).decode().strip()
                system_uuid = SHA256.new(str(sys_uuid).encode('utf-8')).digest()
            except Exception as e:
                print(f'Ошибка при попытке получения BIOS UUID: {str(e)}')
        if i == 'mb_serial':
            try:
                if platform.system() == "Windows":
                    serial = subprocess.check_output("wmic baseboard get serialnumber", shell=True).decode() \
                        .split('\n')[1].strip()
                else:
                    serial = subprocess.check_output("sudo dmidecode -s baseboard-serial-number", shell=True). \
                        decode().strip()
                mb_serial = SHA256.new(serial.encode('utf-8')).digest()
            except Exception as e:
                print(f'Ошибка при попытке получения данных о материнской плате: {str(e)}')
        if i == 'gpu_serial':
            try:
                if platform.system() == "Windows":
                    gpu = subprocess.check_output(
                        "wmic path win32_videocontroller get pnpdeviceid", shell=True). \
                        decode().split('\n')[1].strip().split("\\")[-1]
                elif platform.system() == 'Darwin':
                    gpu = subprocess.check_output(
                        "system_profiler SPDisplaysDataType | grep -i 'device id'", shell=True) \
                        .decode().split(':')[1].strip()
                else:
                    cmd = "lspci -v -s $(lspci | grep -i 'vga\\|3d\\|display' | cut -d' ' -f1) | grep -i 'serial'"
                    gpu = subprocess.check_output(cmd, shell=True).decode().split(':')[1].strip()
                if len(gpu) < 3:
                    print('Ошибка при попытке получения данных о GPU: Процессор отказал в выдаче серийного номера.')
                gpu_serial = SHA256.new(gpu.encode('utf-8')).digest()
            except Exception as e:
                print(f'Ошибка при попытке получения данных о GPU: {str(e)}')
    deckey = SHA256.new(
        b'<KS>' + password + mac + cpu_name + disk_serial + mb_serial + gpu_serial + system_uuid + b'<KE>').digest()
    return deckey


def formenckey(passwd: bytes, data: list):
    password = passwd
    mac = data[0]
    cpu_name = data[1]
    disk_serial = data[2]
    mb_serial = data[3]
    gpu_serial = data[4]
    system_uuid = data[5]
    enckey = SHA256.new(
        b'<KS>' + password + mac + cpu_name + disk_serial + mb_serial + gpu_serial + system_uuid + b'<KE>').digest()
    return enckey
