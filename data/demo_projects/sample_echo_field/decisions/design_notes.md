---

project: echo_field
document_type: design_decision
category: decisions
status: current
dataset_role: demo
------------------

# Echo Field — Design Decisions

## Project aim

Echo Field is a responsive visual installation that explores how visual feedback based on body movement can influence a user’s sense of control and engagement.

The installation uses a webcam to estimate movement intensity. This value controls the speed, density and colour of a generative visual environment.

## Initial interaction idea

The initial concept focused on hand gestures as the main interaction method. Hand movements were intended to provide precise control over the visual response.

## Problem with hand tracking

Early experiments showed that hand-gesture detection was inconsistent. Recognition depended heavily on camera position, lighting conditions, distance and whether the user’s hand remained visible.

The interaction sometimes failed to detect slower gestures and occasionally produced sudden changes that did not match the user’s intention.

## Design decision

The primary interaction was changed from hand gestures to whole-body movement.

Instead of recognising individual gestures, the system measures the overall amount of movement visible in the webcam image. This produces a continuous `movement_strength` value.

## Rationale

Whole-body movement was selected because it was more stable and easier for users to understand without learning a gesture vocabulary. It also allowed the installation to respond to different movement styles rather than requiring one correct gesture.

The decision changed the project from gesture recognition to an exploration of responsive feedback and perceived control.

## Current status

Whole-body movement remains the current interaction method.

The earlier hand-gesture approach is considered superseded and should not be presented as the current design direction.
