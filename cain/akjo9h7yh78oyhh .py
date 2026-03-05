import pygame
import threading
import requests
from pathlib import Path
import libtorrent as lt
from urllib.parse import urlparse
import time

class FileDownloader:
    def __init__(self):
        pygame.init()
        self.WIDTH, self.HEIGHT = 800, 600
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("File Downloader")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        self.url_input = ""
        self.progress = 0
        self.status = "Ready"
        self.downloading = False
        self.session = lt.session()
        self.handle = None
        
    def download_magnet(self, magnet_uri):
        try:
            self.status = "Downloading magnet..."
            params = {'url': magnet_uri, 'save_path': str(Path.home() / "Downloads")}
            self.handle = self.session.add_torrent(params)
            
            # Wait for metadata
            while not self.handle.has_metadata():
                time.sleep(0.1)
            
            # Then download
            while not self.handle.is_seed():
                s = self.handle.status()
                self.progress = int(s.progress * 100)
                self.status = f"Downloading: {self.progress}%"
                time.sleep(0.5)
            
            self.status = "Seeding..."
            for _ in range(60):
                time.sleep(1)
            self.status = "Complete!"
            
        except Exception as e:
            self.status = f"Error: {str(e)}"
        finally:
            self.downloading = False
    
    def download_torrent(self, torrent_path):
        try:
            self.status = "Loading torrent..."
            params = {'ti': lt.torrent_info(torrent_path), 'save_path': str(Path.home() / "Downloads")}
            self.handle = self.session.add_torrent(params)
            
            while not self.handle.is_seed():
                s = self.handle.status()
                self.progress = int(s.progress * 100)
                self.status = f"Downloading: {self.progress}%"
                time.sleep(0.5)
            
            self.status = "Seeding..."
            for _ in range(60):
                time.sleep(1)
            self.status = "Complete!"
            
        except Exception as e:
            self.status = f"Error: {str(e)}"
        finally:
            self.downloading = False
    
    def download_file(self, url):
        try:
            self.status = "Downloading..."
            response = requests.get(url, stream=True)
            total_size = int(response.headers.get('content-length', 0))
            
            filename = urlparse(url).path.split('/')[-1] or "download"
            filepath = Path.home() / "Downloads" / filename
            
            downloaded = 0
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        self.progress = int((downloaded / total_size) * 100) if total_size else 0
            
            self.status = "Complete!"
        except Exception as e:
            self.status = f"Error: {str(e)}"
        finally:
            self.downloading = False
    
    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.unicode.isprintable():
                        self.url_input += event.unicode
                    elif event.key == pygame.K_BACKSPACE:
                        self.url_input = self.url_input[:-1]
                    elif event.key == pygame.K_RETURN and not self.downloading:
                        self.downloading = True
                        self.progress = 0
                        if self.url_input.startswith('magnet:'):
                            t = threading.Thread(target=self.download_magnet, args=(self.url_input,))
                        elif self.url_input.endswith('.torrent'):
                            if self.url_input.startswith(('http://', 'https://')):
                                # Download torrent file first
                                try:
                                    response = requests.get(self.url_input)
                                    temp_torrent = Path.home() / "Downloads" / "temp.torrent"
                                    with open(temp_torrent, 'wb') as f:
                                        f.write(response.content)
                                    t = threading.Thread(target=self.download_torrent, args=(str(temp_torrent),))
                                except Exception as e:
                                    self.status = f"Error downloading torrent: {str(e)}"
                                    self.downloading = False
                                    continue
                            else:
                                # Assume local torrent file
                                t = threading.Thread(target=self.download_torrent, args=(self.url_input,))
                        else:
                            t = threading.Thread(target=self.download_file, args=(self.url_input,))
                        t.daemon = True
                        t.start()
            
            self.screen.fill((30, 30, 30))
            
            title = self.font.render("File Downloader", True, (255, 255, 255))
            self.screen.blit(title, (20, 20))
            
            url_text = self.small_font.render("URL/Torrent:", True, (200, 200, 200))
            self.screen.blit(url_text, (20, 100))
            
            input_rect = pygame.Rect(20, 140, 760, 40)
            pygame.draw.rect(self.screen, (60, 60, 60), input_rect)
            pygame.draw.rect(self.screen, (100, 100, 100), input_rect, 2)
            input_surf = self.small_font.render(self.url_input, True, (255, 255, 255))
            self.screen.blit(input_surf, (30, 150))
            
            status_text = self.small_font.render(self.status, True, (100, 200, 100))
            self.screen.blit(status_text, (20, 220))
            
            progress_rect = pygame.Rect(20, 280, 760, 30)
            pygame.draw.rect(self.screen, (60, 60, 60), progress_rect)
            pygame.draw.rect(self.screen, (100, 100, 100), progress_rect, 2)
            filled_width = int((self.progress / 100) * 760)
            pygame.draw.rect(self.screen, (100, 200, 100), (20, 280, filled_width, 30))
            
            progress_text = self.small_font.render(f"{self.progress}%", True, (255, 255, 255))
            self.screen.blit(progress_text, (380, 290))
            
            hint = self.small_font.render("Press ENTER to download", True, (150, 150, 150))
            self.screen.blit(hint, (20, 350))
            
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()

if __name__ == "__main__":
    app = FileDownloader()
    app.run()