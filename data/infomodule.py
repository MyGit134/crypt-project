import uuid
import platform
import subprocess
import psutil


def collectinfo():
    mac, cpu_name, system_uuid, disk_serial, gpu_serial, mb_serial = "N/A", "N/A", "N/A", "N/A", "N/A", "N/A"
    try:
        mac = ':'.join(f'{b:02x}' for b in uuid.getnode().to_bytes(6, 'big'))
    except Exception as e:
        print(f'Ошибка при попытке получения MAC адреса: {str(e)}')
    try:
        if platform.system() == "Windows":
            cpu_name = platform.processor()
        elif platform.system() == 'Darwin':
            cpu_name = subprocess.check_output("sysctl -n machdep.cpu.brand_string", shell=True).decode().strip()
        else:
            with open('/proc/cpuinfo', 'r') as f:
                for line in f:
                    if 'model name' in line:
                        cpu_name = line.split(':')[1].strip()
    except Exception as e:
        print(f'Ошибка при попытке получения данных о процессоре: {str(e)}')
    try:
        if platform.system() == "Windows":
            disk_serial = subprocess.check_output("wmic diskdrive get serialnumber", shell=True).decode().split("\n")[
                1].strip()
        elif platform.system() == 'Darwin':
            disk_serial = subprocess.check_output("diskutil info disk0 | grep 'Serial Number'",
                                                  shell=True, timeout=5).decode().split(':')[1].strip()
        else:
            for item in psutil.disk_partitions():
                try:
                    cmd = ""
                    if item.device.startswith('/dev/sd') or item.device.startswith('/dev/nvme'):
                        cmd = f"sudo smartctl -i {item.device} | grep 'Serial Number'" if 'nvme' in item.device \
                            else f"sudo hdparm -I {item.device} | grep 'Serial Number'"
                    disk_serial = subprocess.check_output(cmd, shell=True, timeout=5).decode().split(':')[1].strip()
                    break
                except Exception as e:
                    print(f'Ошибка при попытке получения данных о диске: {str(e)}')
                    continue
        disk_serial = disk_serial.replace('.', '')
    except Exception as e:
        print(f'Ошибка при попытке получения данных о диске: {str(e)}')
    try:
        if platform.system() == "Windows":
            system_uuid = subprocess.check_output("wmic csproduct get uuid", shell=True). \
                decode().split('\n')[1].strip()
        else:
            system_uuid = subprocess.check_output("sudo dmidecode -s system-uuid", shell=True).decode().strip()
    except Exception as e:
        print(f'Ошибка при попытке получения BIOS UUID: {str(e)}')
    try:
        if platform.system() == "Windows":
            mb_serial = subprocess.check_output("wmic baseboard get serialnumber", shell=True).decode().split('\n')[1] \
                .strip()
        else:
            mb_serial = subprocess.check_output("sudo dmidecode -s baseboard-serial-number",
                                                shell=True).decode().strip()
    except Exception as e:
        print(f'Ошибка при попытке получения данных о материнской плате: {str(e)}')
    try:
        if platform.system() == "Windows":
            gpu_serial = subprocess.check_output("wmic path win32_videocontroller get pnpdeviceid", shell=True). \
                decode().split('\n')[1].strip().split("\\")[-1]
        elif platform.system() == 'Darwin':
            gpu_serial = subprocess.check_output("system_profiler SPDisplaysDataType | grep -i 'device id'",
                                                 shell=True) \
                .decode().split(':')[1].strip()
        else:
            cmd = "lspci -v -s $(lspci | grep -i 'vga\\|3d\\|display' | cut -d' ' -f1) | grep -i 'serial'"
            gpu_serial = subprocess.check_output(cmd, shell=True).decode().split(':')[1].strip()
        if len(gpu_serial) < 3:
            print('Ошибка при попытке получения данных о GPU: Процессор отказал в выдаче серийного номера.')
    except Exception as e:
        print(f'Ошибка при попытке получения данных о GPU: {str(e)}')
    return [mac, cpu_name, system_uuid, disk_serial, gpu_serial, mb_serial]
