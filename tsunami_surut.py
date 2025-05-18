import pygame
import sys
import math
import random

# Inisialisasi Pygame
pygame.init()

# Konfigurasi layar
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Simulasi Tsunami - Fenomena Air Surut')

# Warna
BIRU_LAUT = (64, 164, 223)
COKELAT_PANTAI = (194, 178, 128)
HIJAU_TUMBUHAN = (34, 139, 34)
COKLAT_DARATAN = (139, 69, 19)
HITAM = (0, 0, 0)

# Posisi awal permukaan air laut
permukaan_air = height * 0.6
dasar_laut = height * 0.8
garis_pantai = width * 0.8

# Fungsi gambar kondisi normal
def gambar_kondisi_normal():
    screen.fill((135, 206, 235))  # Langit
    
    # Daratan dan pantai
    pygame.draw.rect(screen, COKELAT_PANTAI, (garis_pantai, permukaan_air, width-garis_pantai, height-permukaan_air))
    pygame.draw.rect(screen, HIJAU_TUMBUHAN, (garis_pantai, permukaan_air-10, width-garis_pantai, 15))
    
    # Air laut
    pygame.draw.rect(screen, BIRU_LAUT, (0, permukaan_air, garis_pantai, height-permukaan_air))
    
    # Dasar laut
    pygame.draw.lines(screen, COKLAT_DARATAN, False, 
                     [(0, dasar_laut), (garis_pantai*0.4, dasar_laut-50), 
                      (garis_pantai*0.7, dasar_laut-30), (garis_pantai, permukaan_air)])

# Fungsi tampilkan teks
def tampilkan_teks(text, position):
    font = pygame.font.SysFont('Arial', 20)
    text_surface = font.render(text, True, HITAM)
    screen.blit(text_surface, position)

# Loop utama
tahap = 1
clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                tahap += 1
                if tahap > 4:
                    tahap = 1
    
    screen.fill((255, 255, 255))
    
    if tahap == 1:
        gambar_kondisi_normal()
        tampilkan_teks("Tahap 1: Kondisi Awal Pantai dan Air Laut", (20, 20))
        tampilkan_teks("Tekan SPACE untuk tahap selanjutnya", (20, 50))
    
    elif tahap == 2:
        gambar_kondisi_normal()
        
        # Visualisasi patahan tektonik
        patahan_x = garis_pantai * 0.5
        patahan_width = 150
        
        # Gambar patahan yang bergerak
        waktu = pygame.time.get_ticks() / 1000
        gerak_patahan = 20 * math.sin(waktu * 2)
        
        pygame.draw.polygon(screen, COKLAT_DARATAN, [
            (patahan_x - patahan_width/2, dasar_laut + gerak_patahan),
            (patahan_x + patahan_width/2, dasar_laut + gerak_patahan),
            (patahan_x + patahan_width/2 - 20, dasar_laut + gerak_patahan - 40),
            (patahan_x - patahan_width/2 + 20, dasar_laut + gerak_patahan - 40)
        ])
        
        # Visualisasi gaya/energi
        for i in range(10):
            angle = waktu * 10 + i * 36
            radius = 20 + i * 5
            pos_x = patahan_x + radius * math.cos(math.radians(angle))
            pos_y = dasar_laut - 20 + gerak_patahan + radius * math.sin(math.radians(angle))
            pygame.draw.circle(screen, (255, 255, 0, 128), (int(pos_x), int(pos_y)), 2)
                
        tampilkan_teks("Tahap 2: Gaya pada Dasar Laut", (20, 20))
        tampilkan_teks("Tekan SPACE untuk tahap selanjutnya", (20, 50))
        tampilkan_teks("Patahan tektonik di dasar laut", (patahan_x - 80, dasar_laut - 80))
        
    elif tahap == 3:
        # Dasar variabel simulasi
        waktu = pygame.time.get_ticks() / 1000
        patahan_x = garis_pantai * 0.5
        
        # Kondisi dasar laut setelah patahan
        screen.fill((135, 206, 235))  # Langit
        
        # Air laut yang surut
        surut_factor = min(1.0, waktu / 3)
        garis_pantai_baru = garis_pantai + (width * 0.1) * surut_factor
        permukaan_air_tengah = permukaan_air - 40 * surut_factor
        
        # Gambar daratan dan pantai yang lebih terlihat karena air surut
        pygame.draw.rect(screen, COKELAT_PANTAI, (garis_pantai-100*surut_factor, permukaan_air, 
                                                width-(garis_pantai-100*surut_factor), height-permukaan_air))
        pygame.draw.rect(screen, HIJAU_TUMBUHAN, (garis_pantai-100*surut_factor, permukaan_air-10, 
                                               width-(garis_pantai-100*surut_factor), 15))
        
        # Dasar laut yang terlihat saat air surut
        pygame.draw.polygon(screen, (150, 130, 110), [
            (garis_pantai-100*surut_factor, permukaan_air),
            (garis_pantai, permukaan_air+20),
            (garis_pantai, height),
            (garis_pantai-100*surut_factor, height)
        ])
        
        # Gambar air laut yang surut
        titik_air = []
        for x in range(0, int(garis_pantai - 100 * surut_factor)):
            if x < patahan_x - 100:
                # Air normal di sebelah kiri
                y = permukaan_air + 5 * math.sin(x/30 + waktu*2)
                titik_air.append((x, y))
            elif x < patahan_x + 100:
                # Air turun di sekitar patahan
                jarak_ke_patahan = abs(x - patahan_x)
                penurunan = 40 * (1 - jarak_ke_patahan/100) * surut_factor
                y = permukaan_air - penurunan + 5 * math.sin(x/30 + waktu*2)
                titik_air.append((x, y))
            else:
                # Air surut mendekati pantai
                jarak_ke_pantai = garis_pantai - x
                penurunan = 20 * (1 - jarak_ke_pantai/(garis_pantai-patahan_x-100)) * surut_factor
                y = permukaan_air - penurunan + 5 * math.sin(x/30 + waktu*2)
                titik_air.append((x, y))
        
        # Menyelesaikan polygon air
        titik_air.append((int(garis_pantai - 100 * surut_factor), height))
        titik_air.append((0, height))
        
        pygame.draw.polygon(screen, BIRU_LAUT, titik_air)
        
        # Visualisasi patahan yang telah terjadi
        pygame.draw.polygon(screen, COKLAT_DARATAN, [
            (patahan_x - 75, dasar_laut - 40 * surut_factor),
            (patahan_x + 75, dasar_laut - 40 * surut_factor),
            (patahan_x + 55, dasar_laut - 80 * surut_factor),
            (patahan_x - 55, dasar_laut - 80 * surut_factor)
        ])
        
        tampilkan_teks("Tahap 3: Air Laut Mengisi Patahan dan Surut dari Pantai", (20, 20))
        tampilkan_teks("Air laut surut menuju patahan dasar laut", (patahan_x - 100, permukaan_air - 80))
        tampilkan_teks("Garis pantai tertarik ke laut", (garis_pantai - 150, permukaan_air + 30))
        tampilkan_teks("Tekan SPACE untuk tahap selanjutnya", (20, 50))
        
    elif tahap == 4:
        # Dasar variabel simulasi
        waktu = pygame.time.get_ticks() / 1000
        patahan_x = garis_pantai * 0.5
        
        # Langit dan latar belakang
        screen.fill((135, 206, 235))  # Langit
        
        # Parameter gelombang tsunami
        tsunami_progress = min(1.0, (waktu - 3) / 4) if waktu > 3 else 0
        amplitude_tsunami = 80 * tsunami_progress
        kecepatan_tsunami = 3.0
        
        # Gambar daratan dan pantai
        pygame.draw.rect(screen, COKELAT_PANTAI, (garis_pantai, permukaan_air, 
                                                width-garis_pantai, height-permukaan_air))
        pygame.draw.rect(screen, HIJAU_TUMBUHAN, (garis_pantai, permukaan_air-10, 
                                               width-garis_pantai, 15))
        
        # Proses gelombang tsunami menuju pantai
        titik_air = []
        tsunami_peak_x = patahan_x + (garis_pantai - patahan_x) * tsunami_progress
        
        # Membentuk titik-titik gelombang air
        for x in range(0, width):
            if x < tsunami_peak_x - 120:
                # Air di belakang tsunami - lebih tinggi dari normal
                y = permukaan_air - 20 * tsunami_progress + 5 * math.sin(x/30 + waktu*2)
                titik_air.append((x, y))
            elif x < tsunami_peak_x + 50:
                # Puncak gelombang tsunami
                jarak_ke_puncak = abs(x - tsunami_peak_x)
                if jarak_ke_puncak < 50:
                    # Bagian puncak
                    tinggi = amplitude_tsunami * (1 - jarak_ke_puncak/50)
                    y = permukaan_air - tinggi + 2 * math.sin(x/10 + waktu*3)
                    titik_air.append((x, y))
                else:
                    # Bagian belakang puncak
                    y = permukaan_air + 5 * math.sin(x/20 + waktu*2)
                    titik_air.append((x, y))
            elif x < garis_pantai:
                # Air di depan tsunami
                y = permukaan_air + 5 * math.sin(x/30 + waktu*2)
                titik_air.append((x, y))
            else:
                # Garis pantai dan setelahnya
                if tsunami_progress > 0.7:
                    # Air mulai menggenangi pantai
                    banjir_jarak = (tsunami_progress - 0.7) * 300
                    if x < garis_pantai + banjir_jarak:
                        y = permukaan_air - 10 * (1 - (x - garis_pantai) / banjir_jarak) + 2 * math.sin(x/10 + waktu*3)
                        titik_air.append((x, y))
        
        # Menyelesaikan polygon air
        if tsunami_progress > 0.7:
            banjir_jarak = (tsunami_progress - 0.7) * 300
            titik_air.append((min(width, garis_pantai + banjir_jarak), height))
        else:
            titik_air.append((garis_pantai, height))
        
        titik_air.append((0, height))
        
        # Gambar air laut dan tsunami
        pygame.draw.polygon(screen, BIRU_LAUT, titik_air)
        
        # Efek busa di puncak tsunami
        if tsunami_progress > 0:
            for i in range(30):
                pos_x = tsunami_peak_x - 30 + random.randint(-40, 40) 
                pos_y = permukaan_air - amplitude_tsunami + random.randint(-10, 20)
                radius = random.randint(2, 8)
                pygame.draw.circle(screen, (255, 255, 255), (int(pos_x), int(pos_y)), radius)
        
        # Efek cipratan air saat tsunami mendekati pantai
        if tsunami_progress > 0.7:
            for i in range(20):
                splash_x = garis_pantai + random.randint(-30, 50)
                splash_y = permukaan_air - 40 + random.randint(-20, 10)
                pygame.draw.circle(screen, (200, 230, 255), (int(splash_x), int(splash_y)), random.randint(1, 4))
        
        # Visualisasi kekuatan dan energi tsunami
        if tsunami_progress > 0.3 and tsunami_progress < 0.9:
            for i in range(5):
                kekuatan_x = tsunami_peak_x + random.randint(-50, 0)
                kekuatan_y = permukaan_air - amplitude_tsunami/2 + random.randint(-20, 20)
                ukuran = random.randint(5, 15)
                pygame.draw.circle(screen, (60, 130, 200, 128), (int(kekuatan_x), int(kekuatan_y)), ukuran)
        
        tampilkan_teks("Tahap 4: Air Masuk ke Arah Pantai", (20, 20))
        tampilkan_teks(f"Tinggi Gelombang: {int(amplitude_tsunami)} meter", (20, 50))
        tampilkan_teks("Tekan SPACE untuk kembali ke tahap awal", (20, 80))
        
        # Peringatan bahaya tsunami saat gelombang semakin dekat
        if tsunami_progress > 0.5:
            peringatan = "PERINGATAN! TSUNAMI MENDEKATI PANTAI"
            font_warning = pygame.font.SysFont('Arial', 30, bold=True)
            text_warning = font_warning.render(peringatan, True, (255, 0, 0))
            screen.blit(text_warning, (width/2 - text_warning.get_width()/2, 100))
    
    pygame.display.flip()
    clock.tick(30)

pygame.quit()
sys.exit()
