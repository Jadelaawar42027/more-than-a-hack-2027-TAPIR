from pathlib import Path
import numpy as np
from games import GAME, half_video_blocks, source_frames

data_folder = Path(
    "/Users/nicolasgonzalezerales/Downloads/"
    "More Than A Hack 2027 - Initial Challenge - Dataset"
)

tracking_path = data_folder / "tactical/BAR-ATH_tactical_atd.txt"
total_frames = source_frames()

ball_missing = np.ones(total_frames, dtype=bool)
graded = np.zeros(total_frames, dtype=bool)

for half, first, last in half_video_blocks(GAME):
    graded[first:last + 1] = True

records_read = 0

with tracking_path.open() as tracking_file:
    for row_number, line in enumerate(tracking_file):
        frame_id, players, ball = line.strip().split(":")

        if int(frame_id) != row_number + 1:
            raise RuntimeError("Tracking frames are not in the expected order.")

        coordinates = ball.split(",")
        x, y = float(coordinates[0]), float(coordinates[1])
        ball_missing[row_number] = not np.isfinite([x, y]).all()
        records_read += 1

if records_read != total_frames:
    raise RuntimeError("Tracking and video frame counts do not match.")

graded_count = int(graded.sum())
missing_count = int((ball_missing & graded).sum())

print("Graded frames:", graded_count)
print("Graded frames without ball:", missing_count)
print(f"Missing ball percentage: {100 * missing_count / graded_count:.2f}%")