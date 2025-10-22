# 🖼️ Flask Media Selector & Display App

This project is a lightweight Flask web app that lets you **remotely select and display images or videos** on a dedicated display device — perfect for setups where you want to control what’s shown on a screen, such as installations, kiosks, or digital signage.

- ✅ Supports **images** (`.jpg`, `.jpeg`, `.png`, `.gif`)
- ✅ Supports **videos** (`.mp4`, `.mov`, `.webm`)
- 🔁 Automatically loops selected videos
- 🌐 Control page (for selection) and display page can run on **separate devices**
- 🧠 Simple architecture — no database or external dependencies
- 🥧 Designed for use on a **Raspberry Pi 4** (server) with a **remote display** (e.g. iPad or monitor)

---

## 🚀 Overview

The app consists of two main pages:

| Page | URL | Purpose |
|------|-----|----------|
| **Selector** | `/select` | Choose which image or video to display |
| **Display** | `/display` | Fullscreen page that shows the currently selected image or video |

Selections are stored in a shared global variable inside Flask, so the chosen item is instantly reflected on all connected displays.

Example flow:
1. You open `/select` on your laptop → click an image or video.
2. The `/display` page (running on an iPad or Raspberry Pi display) automatically updates and shows that media.

---

## 🧩 Project Structure

```

flask-media-display/
│
├── run.py
├── app/
│   ├── **init**.py
│   ├── routes.py
│   ├── templates/
│   │   ├── select.html
│   │   └── display.html
│   └── static/
│       ├── css/
│       │   └── style.css
│       └── images/
│           ├── example.jpg
│           ├── example2.jpg
│           └── Big_Buck_Bunny_1080p.mp4
└── README.md

````

---

## 🧱 Installation (on Raspberry Pi 4)

### 1. Prerequisites
Make sure your Pi is up to date and has Python 3 and `pip`:

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3 python3-pip -y
````

### 2. Clone the repository

```bash
git clone https://github.com/<yourusername>/flask-media-display.git
cd flask-media-display
```

### 3. Install dependencies

Create a virtual environment (optional but recommended):

```bash
python3 -m venv venv
source venv/bin/activate
```

Install Flask:

```bash
pip install flask
```

### 4. Add your media

Put all your images and videos inside:

```
app/static/images/
```

Supported file types:

* Images: `.jpg`, `.jpeg`, `.png`, `.gif`
* Videos: `.mp4`, `.webm`, `.mov`

### 5. Run the app

```bash
python3 run.py
```

By default, Flask runs on **port 5050** and listens on all interfaces (`0.0.0.0`).

---

## 📱 Usage

### 1. Control panel (selector)

From any device on the same network (your laptop, phone, etc.), open:

```
http://<raspberrypi-ip>:5050/select
```

This shows all available media as thumbnails.
Click an image or video to select it.

---

### 2. Display panel (viewer)

On your iPad (or display device), open:

```
http://<raspberrypi-ip>:5050/display
```

You’ll see the selected image or video in fullscreen.
If you select a different file from `/select`, the display will automatically update within a second.

> 💡 Tip: Add the `/display` page to your iPad’s Home Screen (via “Add to Home Screen” in Safari) for a fullscreen, kiosk-style experience.

---

## ⚙️ Optional: Run on Boot (Raspberry Pi)

You can make the app start automatically when the Pi boots.

1. Create a systemd service:

```bash
sudo nano /etc/systemd/system/media-display.service
```

Paste:

```ini
[Unit]
Description=Flask Media Display
After=network.target

[Service]
User=pi
WorkingDirectory=/home/pi/flask-media-display
Environment="PATH=/home/pi/flask-media-display/venv/bin"
ExecStart=/home/pi/flask-media-display/venv/bin/python run.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Save and enable:

```bash
sudo systemctl daemon-reload
sudo systemctl enable media-display
sudo systemctl start media-display
```

Now the Flask app will automatically run at startup.

---

## 🧠 How It Works

* `routes.py` scans the `app/static/images/` folder for both images and videos.
* The `/select` route renders a grid of all files (with `<img>` for images, `<video>` for video previews).
* When a file is selected, Flask updates a global `selected_image` variable.
* The `/display` page polls the `/current_image` endpoint every 0.5 seconds to check for changes.
* Depending on the file extension, it dynamically loads an `<img>` or `<video>` element.

---

## 🧩 Example Setup

**Hardware**

* Raspberry Pi 4 (running the Flask server)
* iPad or browser-based display (showing `/display`)
* Laptop or phone (to control `/select`)

**Network**
All devices must be on the same Wi-Fi or LAN.
You can find your Pi’s IP using:

```bash
hostname -I
```

Then visit that address (e.g., `http://192.168.0.42:5050/select`).

---

## 🧰 Troubleshooting

| Issue                                        | Cause                                      | Fix                                                                          |
| -------------------------------------------- | ------------------------------------------ | ---------------------------------------------------------------------------- |
| Video doesn’t show / black screen            | Browser autoplay policy                    | Ensure `muted` and `playsinline` are set (already in template). Reload page. |
| `/select` page loads slowly with many videos | Browser loading entire videos as previews  | Consider adding static thumbnails for videos (future enhancement).           |
| Page not updating automatically              | Polling interval too long or browser cache | Try refreshing the `/display` page or increasing `setInterval` frequency.    |
| "Address already in use" on startup          | Flask still running in background          | Kill old process: `sudo lsof -i :5050` then `kill <PID>`                     |
