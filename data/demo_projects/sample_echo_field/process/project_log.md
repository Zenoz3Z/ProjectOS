---

project: echo_field
document_type: process_log
category: process
status: ongoing
dataset_role: demo
------------------

# Echo Field — Project Log

## Initial prototype

The first prototype used webcam frame differencing to detect changes between consecutive images. The difference image was analysed to produce an average brightness value representing movement intensity.

The initial movement value was unstable and reacted strongly to small lighting changes.

## Smoothing and calibration

A Filter CHOP was added to smooth the raw movement signal. The value was also clamped to prevent extreme changes.

During calibration, the approximate movement values were:

* stillness: 0.18–0.20;
* slow movement: around 0.60;
* medium or fast movement: approximately 1.00 or above.

These values were treated as practical observations rather than universal thresholds because camera position and lighting affected the result.

## Informal testing

The prototype was informally tested with five people. Participants generally understood that faster or larger movement produced a stronger visual response.

However, several recurring problems were observed:

* the low-movement state was not always visually clear;
* the movement value occasionally jumped unexpectedly;
* the experience could become visually tiring during extended use;
* detection remained sensitive to lighting and distance.

## Changes made

The movement signal was smoothed to reduce sudden jumps. Colour was connected to movement intensity so that lower movement produced blue tones and stronger movement shifted towards green or yellow-green.

An instruction explaining that the system detects overall body movement was also added.

## Unresolved questions

It is still unclear whether the low-movement state provides enough feedback for users to recognise that the system is responding.

The difference between one-person and multi-person interaction has not been investigated.

The effect of prolonged exposure on comfort and visual fatigue also remains unresolved.
