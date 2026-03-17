import requests

def kirim_notifikasi_absensi_siswa(nama_siswa, kelas, waktu_absen):
    # Gunakan kelas apa adanya (CAPSLOCK), ganti spasi dan tanda hubung jika perlu
    channel = f"ABSENSI-HARIAN-{kelas.replace(' ', '').replace('-', '')}"  # Contoh: X-RPL → absensi-XRPL
    pesan = f"{nama_siswa} dari kelas {kelas} telah hadir pada pukul {waktu_absen}."
    url = f"https://ntfy.sh/{channel}"

    print(f"[DEBUG] Kirim ke: {url}")
    print(f"[DEBUG] Pesan: {pesan}")

    try:
        response = requests.post(url, data=pesan.encode('utf-8'))
        print(f"[DEBUG] Status: {response.status_code}")
    except Exception as e:
        print(f"[ERROR] Kirim notifikasi gagal:", e)

def kirim_notifikasi_absensi_guru(nama_guru, mapel, waktu_absen):
    channel = "ABSENSI-HARIAN-GURU-SMK-1-TRIPLE-J"  # Channel tetap
    pesan = f"{nama_guru} ({mapel}) telah hadir pada pukul {waktu_absen}."
    url = f"https://ntfy.sh/{channel}"

    print(f"[DEBUG] Kirim ke: {url}")
    print(f"[DEBUG] Pesan: {pesan}")

    try:
        response = requests.post(url, data=pesan.encode('utf-8'))
        print(f"[DEBUG] Status: {response.status_code}")
    except Exception as e:
        print(f"[ERROR] Kirim notifikasi gagal:", e)