from pathlib import Path
import cv2

video_path = Path(
    "/Users/nicolasgonzalezerales/Downloads/"
    "More Than A Hack 2027 - Initial Challenge - Dataset/"
    "tactical/BAR-ATH_tactical-001.mp4"
)

video = cv2.VideoCapture(str(video_path))

if not video.isOpened():
    raise RuntimeError(f"Could not open the video: {video_path}")

frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
fps = video.get(cv2.CAP_PROP_FPS)

print("Frame count:", frame_count)
print("Frames per second:", fps)
print("Expected frame count:", frame_count == 199319)

video.release()