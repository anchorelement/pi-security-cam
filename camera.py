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
import logging

logger = logging.getLogger(__name__)

LSIZE = (640, 480)  # size for the lores video config
MSIZE = (1920, 1080)  # size for the main video config
MOTION_SENS_THRESH = 0.6  # threshold for triggering motion capture, higher requires more change between frames
RECORD_TAIL = 5.0  # how long to keep recording after motion passes below threshold
RECORD_MAX = 30.0  # maximum length of individual video files
NOTIFY_AFTER = 10  # how many motion frames before sending notification


class Camera:

    def __init__(self) -> None:
        self.armed = False
        self.camera_thread = None
        self.picam2 = Picamera2()
        video_config = self.picam2.create_video_configuration(
            main={"size": MSIZE, "format": "RGB888"},
            lores={"size": LSIZE, "format": "YUV420"},
            raw=self.picam2.sensor_modes[1],
        )
        self.encoder = H264Encoder(bitrate=10000000)
        self.encoding = False
        self.picam2.configure(video_config)
        self.picam2.start()
        logging.debug(self.picam2.camera_configuration())
        time.sleep(2)

    def arm(self) -> None:
        if not self.armed and not self.camera_thread:
            self.camera_thread = threading.Thread(target=self.run)
        self.armed = True
        logging.info("Camera armed.")
        self.camera_thread.start()

    def disarm(self) -> None:
        self.armed = False
        self.camera_thread = None
        logging.info("Camera disarmed.")

    def detect_motion(self, previous, current) -> bool:
        gray1 = cv2.cvtColor(previous, cv2.COLOR_YUV2GRAY_I420)
        gray1 = cv2.GaussianBlur(gray1, (21, 21), 0)
        gray2 = cv2.cvtColor(current, cv2.COLOR_YUV2GRAY_I420)
        gray2 = cv2.GaussianBlur(gray2, (21, 21), 0)
        mse = np.square(np.subtract(gray2, gray1)).mean()
        # logging.debug(f"MSE: {mse}.")
        if mse > MOTION_SENS_THRESH:
            logging.debug(f"MSE: {mse}.")
            return True
        return False

    def send_notification(self) -> None:
        attach_name = f"image/{time.strftime('%Y_%m_%d-%H_%M_%S')}.jpeg"
        self.picam2.capture_file(attach_name)
        logging.info(type(attach_name))
        send_mail(attach_name)

    def run(self) -> None:
        previous = None
        self.encoding = False
        start_time = 0
        motion_frames = 0
        while self.armed:
            current = self.picam2.capture_array("lores")
            if previous is not None:
                if self.detect_motion(current, previous):
                    motion_frames += 1
                    # filter out short spikes of detected motion (usually false positives)
                    if not self.encoding and motion_frames > 2:
                        self.start_video()
                        start_time = time.time()
                    # mark last time of detected motion
                    ltime = time.time()
                    # check if video is over the max length
                    if self.encoding:
                        encoding_length = ltime - start_time
                        if motion_frames == NOTIFY_AFTER:
                            notification_thread = threading.Thread(
                                target=self.send_notification
                            )
                            notification_thread.start()
                        logging.debug(f"Video recording for: {encoding_length:.3}s.")
                        if encoding_length > RECORD_MAX:
                            logging.info(
                                f"Stopping video due to max length: {encoding_length:.3}s."
                            )
                            self.stop_video()
                            motion_frames = 0
                # check if video is still recording and we are over the tail length with no motion detected
                elif self.encoding and time.time() - ltime > RECORD_TAIL:
                    logging.info(
                        f"Stopping video since no motion has been detected after: {time.time() - ltime:.3}s."
                    )
                    self.stop_video()
                    motion_frames = 0
            previous = current

    def start_video(self) -> None:
        # notification_thread = threading.Thread(target=self.send_notification)
        # notification_thread.start()
        self.picam2.start_encoder(
            encoder=self.encoder,
            output=FileOutput(f"video/{time.strftime('%Y_%m_%d-%H_%M_%S')}.h264"),
            quality=Quality.HIGH,
        )
        self.encoding = True
        logging.info("New motion.")

    def stop_video(self) -> None:
        self.picam2.stop_encoder()
        self.encoding = False
        logging.info("Stopped encoding.")
