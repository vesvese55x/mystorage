#!/bin/bash

# Rclone'u kontrol et ve yüklü değilse yükle
if ! command -v rclone &> /dev/null
then
    echo "Rclone yüklü değil. Yükleniyor..."
    sudo apt update
    sudo apt install -y rclone
    echo "Rclone başarıyla yüklendi."
else
    echo "Rclone zaten yüklü."
fi

# Bulut hizmetini seçin
echo "Hangi bulut hizmetini bağlamak istiyorsunuz?"
echo "1) Google Drive"
echo "2) Dropbox"
read -p "Seçiminizi yapın (1 veya 2): " choice

if [ "$choice" == "1" ]; then
    # Google Drive konfigürasyonu
    rclone config create gdrive drive scope drive.file \
    --config /root/.config/rclone/rclone.conf
    echo "Google Drive konfigürasyonu oluşturuldu."

    # Google Drive yetkilendirmesi için tarayıcıyı aç
    echo "Google Drive için yetkilendirme işlemini başlatıyorum..."
    rclone config reconnect gdrive: --config /root/.config/rclone/rclone.conf

    # Klasör oluşturma ve mount işlemi
    mkdir -p ~/gdrive
    rclone mount gdrive: ~/gdrive --vfs-cache-mode writes &
    echo "Google Drive başarıyla bağlandı: ~/gdrive"

elif [ "$choice" == "2" ]; then
    # Dropbox konfigürasyonu
    rclone config create dropbox dropbox \
    --config /root/.config/rclone/rclone.conf
    echo "Dropbox konfigürasyonu oluşturuldu."

    # Dropbox yetkilendirmesi için tarayıcıyı aç
    echo "Dropbox için yetkilendirme işlemini başlatıyorum..."
    rclone config reconnect dropbox: --config /root/.config/rclone/rclone.conf

    # Klasör oluşturma ve mount işlemi
    mkdir -p ~/dropbox
    rclone mount dropbox: ~/dropbox --vfs-cache-mode writes &
    echo "Dropbox başarıyla bağlandı: ~/dropbox"

else
    echo "Geçersiz seçim!"
    exit
fi

echo "Bağlantı için tarayıcıyı açıyorum..."
