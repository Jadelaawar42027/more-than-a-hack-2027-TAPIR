## Experiment 3 — Ball-tracking gaps

- Question: Are missing-ball gaps short enough for interpolation, or should we investigate a detector?
- Method: Analysed consecutive missing-ball runs separately within each graded half, using video_frame = frame_id - 1.
- Results: Of 158,857 graded frames, 64,643 (40.69%) have no ball position. There are 150 gaps; the longest lasts 5,537 frames (221.48 seconds). The 133 gaps longer than one second cover 40.65% of graded frames.
- Evidence: Generated cache/gap_histogram.png and cache/long_gap_pitch_positions.png. The pitch plots contain 133 observed positions before long gaps and 131 after them; unavailable endpoints were omitted.
- Decision: Long gaps exceed the guide's 15% threshold, so detector investigation is justified. First build the interpolation baseline in Step 3, investigate the longest gaps, and later test whether a detector improves recovery.