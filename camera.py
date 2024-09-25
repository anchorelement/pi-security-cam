from picamera2 import Picamera2
from picamera2.encoders import H264Encoder, Quality
from picamera2.outputs import FileOutput, FfmpegOutput
from libcamera import controls
import cv2
import numpy as np
import threading
import time
from notifications import send_mail
from pprint import pprint
import sys
import logging

# TODO: send a few of the first frames of video via email
# TODO: look into automatically converting videos to mpeg
# TODO: look into uploading to a service like S3

logger = logging.getLogger(__name__)

LSIZE = (640, 480)  # size for the lores video config
MSIZE = (1920, 1080)  # size for the main video config
MOTION_SENS_THRESH = 100_000  # threshold for triggering motion capture, higher requires more change between frames
RECORD_AFTER = 5.0  # how long to keep recording after motion passes below threshold


class Camera:

    def __init__(self):
        self.armed = False
        self.camera_thread = None
        self.picam2 = Picamera2()
        video_config = self.picam2.create_video_configuration(
            main={"size": MSIZE, "format": "RGB888"},
            lores={"size": LSIZE, "format": "YUV420"},
            raw=self.picam2.sensor_modes[1],
        )
        self.motion_sense_thresh = MOTION_SENS_THRESH
        self.record_after = RECORD_AFTER
        self.encoder = H264Encoder(bitrate=10000000)
        self.picam2.configure(video_config)
        self.picam2.start()
        # pprint(self.picam2.camera_configuration())
        time.sleep(2)

    def arm(self):
        if not self.armed and not self.camera_thread:
            self.camera_thread = threading.Thread(target=self.run)
        self.armed = True
        logging.info("Camera armed.")
        self.camera_thread.start()

    def disarm(self):
        self.armed = False
        self.camera_thread = None
        logging.info("Camera disarmed.")

    def detect_motion(self, previous, current) -> bool:
        gray1 = cv2.cvtColor(previous, cv2.COLOR_YUV2GRAY_I420)
        gray1 = cv2.GaussianBlur(gray1, (21, 21), 0)
        gray2 = cv2.cvtColor(current, cv2.COLOR_YUV2GRAY_I420)
        gray2 = cv2.GaussianBlur(gray2, (21, 21), 0)
        diff = cv2.absdiff(gray1, gray2)
        cnz = cv2.countNonZero(diff)
        # logging.info(cnz)
        if cnz > MOTION_SENS_THRESH:
            logging.info(cnz)
            return True
        return False

    def send_notification(self):
        attach_name = f"image/{time.strftime('%Y_%m_%d-%H_%M_%S')}.jpeg"
        self.picam2.capture_file(attach_name)
        send_mail(attach_name)

    def run(self):
        previous = None
        encoding = False
        ltime = 0
        motion_frames = 0
        while self.armed:
            current = self.picam2.capture_array("lores")
            if previous is not None:
                if self.detect_motion(current, previous):
                    motion_frames += 1
                    # filter out short spikes of detected motion (usually false positives)
                    if not encoding and motion_frames > 2:
                        pic_thread = threading.Thread(target=self.send_notification)
                        pic_thread.start()
                        self.picam2.start_encoder(
                            encoder=self.encoder,
                            output=FileOutput(
                                f"video/{time.strftime('%Y_%m_%d-%H_%M_%S')}.h264"
                            ),
                            quality=Quality.HIGH,
                            pts="video/timestamps.txt",
                        )
                        encoding = True
                        logging.info("New motion.")
                    ltime = time.time()
                else:
                    if encoding and time.time() - ltime > self.record_after:
                        self.picam2.stop_encoder()
                        encoding = False
                        motion_frames = 0
                        logging.info("Stopped encoding.")
            previous = current
