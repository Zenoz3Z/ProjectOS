---

project: echo_field
document_type: current_state
category: current_state
status: current
dataset_role: demo
------------------

# Echo Field — Current State

## Current goal

The current goal is to investigate how visual feedback driven by whole-body movement influences users’ sense of control and engagement.

## Current interaction

The webcam detects changes across the full image rather than recognising specific hand gestures.

The resulting `movement_strength` value controls:

* visual speed;
* pattern density;
* colour transition;
* overall visual intensity.

## Completed work

* Webcam movement detection is functioning.
* The raw movement value has been smoothed.
* Extreme values have been clamped.
* Colour changes have been linked to movement intensity.
* The interface explains that overall body movement is being detected.
* Informal testing has been completed with five participants.

## Current blockers

* Slow movement does not always produce sufficiently clear feedback.
* Sudden value changes can still occur under unstable lighting.
* Long viewing sessions may cause visual fatigue.
* The current system cannot distinguish between one participant and multiple participants.

## Next steps

1. Test whether the low-movement visual state is sufficiently visible.
2. Compare the intended response with the actual movement value.
3. Record any sudden jumps caused by lighting changes.
4. Decide whether multi-person interaction belongs in the current scope or future work.

## Superseded direction

Hand-gesture recognition is no longer the current interaction method. It should only be discussed as an earlier experiment that informed the whole-body movement design.
