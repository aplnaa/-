import http.client
import threading
import time
import sys
import os
from urllib.parse import urlparse

class DownloadFileFromUrl:
    def __init__(self):
        self.bytes_received = 0
        self.is_running = True
        self.last_bytes = 0

    def download_file(self, url):
        
        # разбивка url на компоненты
        parsed = urlparse(url)
        
        filename = os.path.basename(parsed.path)
        
        # выбор тип соединения
        if parsed.scheme == 'https':
            conn = http.client.HTTPSConnection(parsed.netloc)
        else:
            conn = http.client.HTTPConnection(parsed.netloc)

        try:
            conn.request('GET', parsed.path)
            response = conn.getresponse()
            
            # проверка ответа
            if response.status != 200:
                print(f"Ошибка: Сервер вернул статус {response.status}")
                return

            total_size = response.getheader('content-length')
            if total_size:
                print(f"Размер файла: {int(total_size):,} байт")
            
            print(f"Начинаем загрузку файла: {filename}")
            
            with open(filename, 'wb') as f:
                while True:
                    chunk = response.read(8192) # чтение файла частями
                    if not chunk:
                        break
                    f.write(chunk)
                    self.bytes_received += len(chunk)
                    
            print(f"\nЗагрузка завершена: {filename}")
                
        except Exception as e:
            print(f"Ошибка при загрузке: {e}")
        finally:
            self.is_running = False
            conn.close()

    def print_progress(self):
        while self.is_running:
            current_speed = self.bytes_received - self.last_bytes
            if current_speed > 0:
                print(f"Получено байт: {self.bytes_received:,} (скорость: {current_speed:,} байт/сек)")
            else:
                print(f"Получено байт: {self.bytes_received:,}")
            self.last_bytes = self.bytes_received
            time.sleep(1)

def main():
    if len(sys.argv) != 2:
        print("Использование: python script.py <URL>")
        return

    url = sys.argv[1]
    downloader = DownloadFileFromUrl()

    # два потока - загрузка и отображение
    download_thread = threading.Thread(target=downloader.download_file, args=(url,))
    progress_thread = threading.Thread(target=downloader.print_progress)

    download_thread.start()
    progress_thread.start()

    download_thread.join()
    progress_thread.join()

if __name__ == "__main__":
    main()
