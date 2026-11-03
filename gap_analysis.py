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

gap_lengths = []

for half, first, last in half_video_blocks(GAME):
    current_length = 0

    for frame_number in range(first, last + 1):
        if ball_missing[frame_number]:
            current_length += 1
        elif current_length > 0:
            gap_lengths.append(current_length)
            current_length = 0

    if current_length > 0:
        gap_lengths.append(current_length)

assert sum(gap_lengths) == missing_count

print("Number of gaps:", len(gap_lengths))
print("Longest gap in frames:", max(gap_lengths, default=0))
print("Longest gap in seconds:", max(gap_lengths, default=0) / 25)

gap_seconds = np.array(gap_lengths) / 25

bins = [
    ("Under 0.2 s", 0, 0.2),
    ("0.2 to under 0.5 s", 0.2, 0.5),
    ("0.5 to under 1 s", 0.5, 1),
    ("1 to under 2 s", 1, 2),
    ("2 to under 5 s", 2, 5),
    ("5 s or more", 5, np.inf),
]

for label, lower, upper in bins:
    selected = (gap_seconds >= lower) & (gap_seconds < upper)
    count = int(selected.sum())
    frames = int(np.array(gap_lengths)[selected].sum())
    share = 100 * frames / graded_count
    print(f"{label}: {count} gaps, {frames} frames, {share:.2f}%")

long_gap_frames = sum(length for length in gap_lengths if length > 25)
long_gap_share = 100 * long_gap_frames / graded_count

print(f"Gaps longer than 1 second cover {long_gap_share:.2f}% of graded frames.")

import matplotlib.pyplot as plt

labels = []
counts = []
shares = []
lengths = np.array(gap_lengths)

for label, lower, upper in bins:
    selected = (gap_seconds >= lower) & (gap_seconds < upper)
    labels.append(label)
    counts.append(int(selected.sum()))
    shares.append(100 * lengths[selected].sum() / graded_count)

figure, axes = plt.subplots(1, 2, figsize=(14, 6))

axes[0].bar(labels, counts)
axes[0].set_title("Number of missing-ball gaps")
axes[0].set_ylabel("Number of gaps")

axes[1].bar(labels, shares)
axes[1].set_title("Share of all graded frames")
axes[1].set_ylabel("Graded frames (%)")

for axis in axes:
    axis.set_xlabel("Gap duration")
    axis.tick_params(axis="x", rotation=45)

figure.tight_layout()

plot_path = Path(__file__).resolve().parent / "cache" / "gap_histogram.png"
plot_path.parent.mkdir(exist_ok=True)

figure.savefig(plot_path, dpi=150)
plt.close(figure)

print("Histogram saved:", plot_path)

ball_positions = np.full((total_frames, 2), np.nan)

with tracking_path.open() as tracking_file:
    for line in tracking_file:
        frame_id, players, ball = line.strip().split(":")
        coordinates = ball.split(",")
        frame_number = int(frame_id) - 1
        ball_positions[frame_number] = [
            float(coordinates[0]),
            float(coordinates[1]),
        ]

start_points = []
end_points = []
long_gap_count = 0

for half, first, last in half_video_blocks(GAME):
    missing_in_half = ball_missing[first:last + 1]

    padded = np.concatenate(([False], missing_in_half, [False]))
    changes = np.diff(padded.astype(int))

    starts = np.flatnonzero(changes == 1) + first
    ends = np.flatnonzero(changes == -1) + first - 1

    for start, end in zip(starts, ends):
        length = end - start + 1

        if length <= 25:
            continue

        long_gap_count += 1

        if start > first:
            point = ball_positions[start - 1]
            if np.isfinite(point).all():
                start_points.append(point)

        if end < last:
            point = ball_positions[end + 1]
            if np.isfinite(point).all():
                end_points.append(point)

start_points = np.array(start_points).reshape(-1, 2)
end_points = np.array(end_points).reshape(-1, 2)

print("Long gaps:", long_gap_count)
print("Available positions before long gaps:", len(start_points))
print("Available positions after long gaps:", len(end_points))

figure, axes = plt.subplots(1, 2, figsize=(14, 5))

plots = [
    (axes[0], start_points, "Last known ball position before a long gap"),
    (axes[1], end_points, "First known ball position after a long gap"),
]

for axis, points, title in plots:
    axis.set_facecolor("#dcefd5")

    axis.plot([0, 1, 1, 0, 0], [0, 0, 1, 1, 0], color="black")
    axis.plot([0.5, 0.5], [0, 1], color="black")

    centre_circle = plt.Circle(
        (0.5, 0.5),
        9.15 / 105.3,
        fill=False,
        color="black",
    )

    # Draw the circle in metres so it keeps the correct shape.
    centre_circle = plt.Circle(
        (105.3 / 2, 68 / 2),
        9.15,
        fill=False,
        color="black",
    )

    axis.clear()
    axis.set_facecolor("#dcefd5")
    axis.plot(
        [0, 105.3, 105.3, 0, 0],
        [0, 0, 68, 68, 0],
        color="black",
    )
    axis.plot([105.3 / 2] * 2, [0, 68], color="black")
    axis.add_patch(centre_circle)

    axis.scatter(
        points[:, 0] * 105.3,
        points[:, 1] * 68,
        s=25,
        alpha=0.6,
    )

    axis.set_xlim(-3, 108.3)
    axis.set_ylim(71, -3)
    axis.set_aspect("equal")
    axis.set_title(title)
    axis.set_xlabel("Pitch length (m)")
    axis.set_ylabel("Pitch width (m)")

figure.tight_layout()

pitch_plot_path = plot_path.parent / "long_gap_pitch_positions.png"
figure.savefig(pitch_plot_path, dpi=150)
plt.close(figure)

print("Pitch plot saved:", pitch_plot_path)