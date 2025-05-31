# 🧠 LayerEdge WebSocket Background Client (Async Python)

Script ini adalah implementasi ulang **background.js** dari ekstensi LayerEdge, ditulis ulang dalam **Python asynchronous**, dan dijalankan via **command line interface (CLI)**.

---

## 🚀 Fitur

- ✅ Koneksi ke WebSocket LayerEdge menggunakan token
- ✅ Mendukung custom headers seperti browser
- ✅ Auto reconnect dengan exponential backoff
- ✅ Heartbeat otomatis setiap 25 detik
- ✅ Menyimpan `connectionStatus` dan waktu terakhir disconnect
- ✅ Penyimpanan ringan dengan `storage.json`

---

## 📦 Requirements

- Python 3.8+
- Install dependencies:

```bash
pip install websockets
```

---

## ⚙️ Cara Pakai

1. **Clone / salin file `layeredge.py`**

2. **Jalankan script:**

```bash
python layeredge.py
```

> Jika `wsToken` belum tersedia di `storage.json`, kamu akan diminta memasukkannya lewat terminal.

3. **Script akan:**
   - Terkoneksi ke server WebSocket LayerEdge
   - Menampilkan pesan dari server
   - Mengirim heartbeat otomatis
   - Menyimpan waktu terakhir disconnect ke `storage.json`

---

## 🧠 Format `storage.json` (opsional)

```json
{
  "wsToken": "your_websocket_token_here",
  "connectionStatus": "Connected or Disconnected",
  "lastDisconnected": "2025-05-31T16:20:01.000Z"
}
```

- Token bisa didapat dari WebSocket URL saat kamu login di LayerEdge Extensions.

---
