from pathlib import Path
import cv2

video_path = Path(
    "/Users/nicolasgonzalezerales/Downloads/"
    "More Than A Hack 2027 - Initial Challenge - Dataset/"
    "tactical/BAR-ATH_tactical-001.mp4"
)

frame_number = 11185
video = cv2.VideoCapture(str(video_path))

if not video.isOpened():
    raise RuntimeError("Could not open the video.")

video.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
success, frame = video.read()
video.release()

if not success:
    raise RuntimeError(f"Could not read frame {frame_number}.")

output = Path(__file__).resolve().parent / "cache" / "frame_11185.jpg"
output.parent.mkdir(exist_ok=True)

if not cv2.imwrite(str(output), frame):
    raise RuntimeError("Could not save the image.")

print("Saved:", output)
print("Image size:", frame.shape)

import numpy as np
from starter.load_homography import load, project

data_folder = video_path.parent.parent

matrices, errors, valid = load(data_dir=str(data_folder))

if not valid[frame_number]:
    raise RuntimeError("No valid homography for this frame.")

tracking_path = video_path.parent / "BAR-ATH_tactical_atd.txt"
tracking_id = frame_number + 1

tracking_row = None

with tracking_path.open() as tracking_file:
    for line in tracking_file:
        if int(line.split(":", 1)[0]) == tracking_id:
            tracking_row = line.strip().split(":")
            break

if tracking_row is None:
    raise RuntimeError("Tracking row not found.")

matrix = matrices[frame_number]
overlay = frame.copy()


def draw_position(values, colour, label):
    coordinates = values.split(",")
    x, y = float(coordinates[0]), float(coordinates[1])

    if not np.isfinite([x, y]).all():
        return False

    u, v = project(matrix, x, y)

    if not np.isfinite([u, v]).all():
        return False

    u, v = round(float(u)), round(float(v))
    height, width = overlay.shape[:2]

    if not (0 <= u < width and 0 <= v < height):
        return False

    cv2.circle(overlay, (u, v), 10, colour, 2)
    cv2.putText(
        overlay, label, (u + 12, v - 12),
        cv2.FONT_HERSHEY_SIMPLEX, 0.5, colour, 1
    )
    return True


players_drawn = 0

for slot, player in enumerate(tracking_row[1].split(";")):
    if not player.strip():
        continue

    if draw_position(player, (0, 255, 0), f"Slot {slot + 1}"):
        players_drawn += 1

ball_drawn = draw_position(tracking_row[2], (0, 0, 255), "Ball")

overlay_path = output.parent / "frame_11185_tracking.jpg"

if not cv2.imwrite(str(overlay_path), overlay):
    raise RuntimeError("Could not save the overlay.")

print("Players drawn:", players_drawn)
print("Ball drawn:", ball_drawn)
print("Saved:", overlay_path)

ball_values = tracking_row[2].split(",")
ball_x, ball_y = float(ball_values[0]), float(ball_values[1])

if not np.isfinite([ball_x, ball_y]).all():
    print("Ball check: tracking position is missing.")
else:
    u, v = project(matrix, ball_x, ball_y)

    if not np.isfinite([u, v]).all():
        print("Ball check: projection is invalid.")
    else:
        print("Ball check: projected position is outside the image.")