from dataclasses import asdict, dataclass
from pprint import pprint
import draccus

from lerobot.cameras.opencv.configuration_opencv import OpenCVCameraConfig  # noqa: F401
from lerobot.cameras.realsense.configuration_realsense import RealSenseCameraConfig  # noqa: F401
from lerobot.configs import parser
from lerobot.processor import (
    make_default_processors,
)
from lerobot.robots import (  # noqa: F401
    Robot,
    RobotConfig,
    bi_so100_follower,
    hope_jr,
    koch_follower,
    make_robot_from_config,
    so100_follower,
    so101_follower,
)
from lerobot.teleoperators import (  # noqa: F401
    Teleoperator,
    TeleoperatorConfig,
    bi_so100_leader,
    gamepad,
    homunculus,
    koch_leader,
    make_teleoperator_from_config,
    so100_leader,
    so101_leader,
)

@dataclass
class TeleoperateConfig:
    robot: RobotConfig
    # Limit the maximum frames per second.
    fps: int = 60
    teleop_time_s: float | None = None
    # Display all cameras on screen

PORT = "/dev/serial/by-id/usb-1a86_USB_Single_Serial_5A7A058116-if00"

def commands(bus):
    # Show all models known by the bus
    print("Models:", list(bus.model_ctrl_table.keys()))

    # Show every data name available for sts3215
    pprint(sorted(bus.model_ctrl_table['sts3215'].keys()))

    # If you just want to search for candidates related to "return" or "status":
    pprint([k for k in bus.model_ctrl_table['sts3215'].keys()
            if 'return' in k.lower() or 'status' in k.lower()])


def get_robot():
    with open('config/test.yaml') as fp:
        cfg = draccus.load(TeleoperateConfig, fp)
    robot = make_robot_from_config(cfg.robot)
    teleop_action_processor, robot_action_processor, robot_observation_processor = make_default_processors()
    robot.connect()
    return robot

def test_read(r: Robot):
    for m in r.bus.motors:
        print("Present_Position:", m, r.bus.read("Present_Position", m))


def ping(robot: Robot, cnt):
    bus = robot.bus
    for i in range(cnt):
     #   for m in bus.motors:
        m = "wrist_roll"
        for cnt in range(1, 10):
            try:
                print(f"ping({m}):", bus.ping(m))
                bus.write("Goal_Position", "shoulder_pan", 2)  # blind write: enable replies
            except Exception as e: print("write SRL:", e)
            try:
                print("Model_Number:", bus.read("Model_Number", m))
                pp = bus.read("Present_Position", m)
                print("Present_Position:", pp)
            except Exception as e:
                print(f"read {cnt} failed:", e)
            try:
                bus.write("Goal_Position", m, pp - 1)
            except Exception as e:
                print("write failed:", e)
            try:
                print("Goal_Position:", bus.read("Goal_Position", m))
            except Exception as e:
                print(f"read {cnt} failed:", e)
            print("present_position:", bus.read("Present_Position", m))

