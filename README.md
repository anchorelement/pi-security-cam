# Raspberry Pi Security Camera

This software will turn a Raspberry Pi with camera module into a motion-detecting security camera with email notifications.  It's been tested on a Raspberry Pi 3b+ with the official [Raspberry Pi Camera Module V2](https://www.raspberrypi.com/products/camera-module-v2/).  There is a basic web interface to enable/disable the system.  



- Install Raspbian Bookworm and configure networking
- Update Raspbian: `sudo apt update` `sudo apt full-upgrade`
- Install pip3: `sudo apt install python3-pip`
- Install git: `sudo apt install git`
- Clone the repository: `git clone https://github.com/anchorelement/pi-security-cam.git`
- Install pip3, picamera2, opencv, sqlite3 with apt
- Create a virtual environment using --system-site-packages: `python3 -m venv .venv --system-site-packages`
- Install flask, sqlalchemy, flask-sqlalchemy, flask-bcrypt, flask-login, flask-migrate in a Python virtual environment
- Initialize the database: `python manage.py`
- 