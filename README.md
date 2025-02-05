# Raspberry Pi Security Camera

This software will turn a Raspberry Pi with camera module into a motion-detecting security camera with email notifications.  It's been tested on a Raspberry Pi 3b+ with the official [Raspberry Pi Camera Module V2](https://www.raspberrypi.com/products/camera-module-v2/).  There is a basic web interface to enable/disable the system.  

- Install Raspbian Bookworm and configure networking
- Update Raspbian: `sudo apt update && sudo apt full-upgrade -y`
- Clone the repository: `git clone https://github.com/anchorelement/pi-security-cam.git`
- Install pip3, sqlite3, git, python3-picamera2, python3-opencv, python3-email-validator, python3-flask, python3-flask-sql-alchemy, python3-flask-bcrypt, python3-flask-login, python3-flask-migrate, with `apt install ...`
- Create a virtual environment using --system-site-packages: `python3 -m venv .venv --system-site-packages`
- Activate: `source .venv/bin/activate`
- Install flask-wtf and gunicorn with pip: `python -m pip install flask-wtf gunicorn`
- Initialize the database: `python manage.py`
- Run the flask app
- Go to the website and register yourself as a user
- Use sqlite3 to connect to the database in instace/pi-camera.db and update the is_admin value in your user record to true, e.g.: `update user set is_admin = true where id == 1`
- Set the following environment variables to configure notifications: MOTIONCAM_SENDER (a gmail address), MOTIONCAM_PW (your gmail password), MOTIONCAM_RECIPIENT (any email address).  You should have a dedicated, separate gmail account for the purpose of sending email with this program.  
- configure gunicorn, ngnix (not really needed), ssl, system service, environment variables and anything else you'd like in your production environment.  