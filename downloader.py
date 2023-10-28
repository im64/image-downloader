import os
import requests
import logging
import sys
import concurrent.futures
import threading


class ImageDownloader:
    def __init__(self, output_dir="images"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.init_logger()
        self.executor = concurrent.futures.ThreadPoolExecutor()

    def init_logger(self) -> None:
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.logfile_path = 'img-downloader.log'

        file_handler = logging.FileHandler(self.logfile_path)
        file_handler.setLevel(logging.DEBUG)

        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.setLevel(logging.DEBUG)

        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        stdout_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(stdout_handler)

    # Task for thread pool
    def download_img_task(self, url, filename):
        id = threading.current_thread().ident
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            full_path = os.path.join(self.output_dir, filename)

            with open(full_path, 'wb') as image_file:
                for chunk in response.iter_content(8192):
                    image_file.write(chunk)

            self.logger.info(f"[{id}] Downloaded: {url}; {filename}")

        except Exception as e:
            self.logger.error(f"[{id}] Failed. URL: {url}; Exception: {e}")

    def download(self, url, filename):
        self.executor.submit(self.download_img_task, url, filename)


if __name__ == "__main__":
    downloader = ImageDownloader()
    with open('urls.txt', 'r') as file:
        urls = [i.strip() for i in file.readlines()]

    for i, url in enumerate(urls):
        downloader.download(url, f'{i}.jpg')
