# Quadruped Motion Control Architecture Guidance

This document outlines recommended conventions and software structures for controlling the Diamond quadruped's 12 SG90 servos. It covers class design, command interfaces, gait generation, and how to bridge an Xbox controller to leg motion.

## 1. Class and Module Organization

### 1.1 Hardware Abstraction Layer (HAL)
- **`PCA9685Controller`**: Wrap PCA9685 initialization, frequency, and channel management once at the robot level. Reuse the object across legs instead of constructing a new bus/PCA instance per `Leg`.
- **`ServoJoint`**: Represent each physical joint with metadata (home angle, min/max angle, calibration offset). Provide methods `set_angle(angle_deg)` and `set_offset(offset_deg)`.
- **`LegKinematics`**: Keep link lengths, joint order, and coordinate frames. Methods:
  - `forward_kinematics(joint_angles) -> (x, y, z)`
  - `inverse_kinematics(target_pose) -> joint_angles`

### 1.2 Mid-Level Leg API
- `Leg` should hold three `ServoJoint` instances. Provide high-level methods:
  - `move_to(x, y, z, speed=None)` – run IK and send commands to joints.
  - `set_joint_targets(joint_angles, speed=None)` – direct joint commands for scripted motions.
  - `trajectory(points, duration)` – time-parameterized sequence for swing phase.
- Maintain leg state (`current_pose`, `current_joint_angles`) to support gait scheduling and safety checks (e.g., clamp to reachable workspace).

### 1.3 Whole-Body Controller
- **`GaitController`** module coordinates legs. Responsibilities:
  - Maintain gait phase (e.g., trot, crawl, pace) and duty cycle.
  - Generate desired foot trajectories per phase (swing vs stance).
  - Handle body motions (translation/rotation) that shift desired footholds.
- Provide functions such as `command_velocity(vx, vy, wz)` that translate desired body velocity into leg trajectories.

### 1.4 Command Interface Layer
- **`CommandMixer`**: Convert high-level intents (walk forward, strafe, rotate) into velocity commands or gait selections.
- **`XboxControllerAdapter`**: Poll joystick state, map axes/buttons to velocity requests and mode toggles, and send them to the `CommandMixer`.

## 2. Motion Command Conventions

### 2.1 Coordinate Frames
- Use a consistent robot-centric coordinate frame: x forward, y left, z up relative to body center.
- Express leg endpoints in a body frame, then transform to leg-local frames (offset by hip position).
- Store transformations (rotation/translation) for each leg to share IK code by mirroring coordinates.

### 2.2 Pose Representation
- Represent leg targets as `(x, y, z)` offsets from each hip origin.
- For body motion, represent orientation with roll/pitch/yaw (Euler) or quaternions. Keep ground height as separate state (body_z).

### 2.3 Timing and Interpolation
- Run a control loop at a fixed rate (e.g., 100 Hz). Compute desired joint angles for each tick.
- Use spline or cosine interpolation for smooth swing trajectories.
- Maintain phase variable `phi ∈ [0, 1)` per leg for periodic gaits.

## 3. Walking Coordination Strategy

### 3.1 Gait Scheduler
1. Choose gait (crawl for stability, trot for speed, pace/bound for experiments).
2. Assign phase offsets per leg (e.g., trot: front_left and back_right in phase).
3. For each tick, determine whether leg is in stance or swing based on `phi` and duty factor.

### 3.2 Stance Phase Control
- Keep foot stationary relative to ground while adjusting body pose.
- Compute desired joint angles by IK of body-relative target transformed by current body pose.
- Blend velocity commands: `foot_target += R_body * [vx, vy, 0] * dt`.

### 3.3 Swing Phase Control
- Generate swing trajectory (e.g., Bezier curve) from lift-off point to touch-down point.
- Provide clearance height and step length based on commanded velocity.
- Ensure smooth transitions by matching velocity/acceleration at boundaries.

### 3.4 Body Motion Blending
- Implement a `BodyPose` class for desired body translation/rotation.
- Use inverse body kinematics to shift all leg targets when you tilt or raise the chassis.

## 4. Practical Implementation Tips

1. **Calibration First**: Build a configuration file listing neutral angles and offsets for each servo channel.
2. **Safety Guards**: Clamp joint angles to avoid overextending SG90 servos. Monitor IK feasibility and fallback gracefully.
3. **Command Queueing**: Batch PCA9685 writes to update all joints simultaneously. Use `pca.channels[channel].duty_cycle = value` for raw timing when precise speeds needed.
4. **Rate Limiting**: Implement low-pass filtering on joystick inputs to avoid abrupt changes.
5. **Simulation/Test Harness**: Create a pure-software leg model to test IK and gait before running on hardware.
6. **State Machine**: Manage higher-level behaviors (idle, walk, turn, dance) through a simple state machine controlling the `GaitController`.
7. **Logging**: Record commanded angles and controller inputs for debugging.

## 5. Suggested File Layout

```
diamond/
├── diamond.py              # Entry point, instantiates controllers
├── controllers/
│   ├── hal.py              # PCA9685Controller, ServoJoint
│   ├── leg.py              # LegKinematics, Leg
│   ├── gait.py             # GaitController implementations
│   └── body.py             # BodyPose, inverse body kinematics
├── commands/
│   ├── mixer.py            # CommandMixer
│   └── xbox.py             # XboxControllerAdapter
└── configs/
    └── servos.yaml         # Calibration data
```

Following these conventions keeps inverse kinematics logic modular, makes it easier to add new gaits, and provides clear seams between hardware access, kinematics, and user input.

## 6. Recommended Implementation Roadmap

Break the work into focused pull requests so that each layer is validated before the next one depends on it. A sample 6-step plan is:

1. **Servo HAL and Calibration Infrastructure** – Implement `PCA9685Controller`, `ServoJoint`, and load calibration data from `configs/servos.yaml`. Include a CLI or notebook that moves individual joints for verification.
2. **Leg Kinematics Library** – Add `LegKinematics` with forward/inverse kinematics plus unit tests and a simple visualizer/simulation harness that exercises workspace limits.
3. **Leg Wrapper and Safety Guards** – Build the `Leg` class around the HAL and kinematics, adding reachability checks, motion smoothing, and logging utilities.
4. **Gait Controller Skeleton** – Introduce the `GaitController`, define gait descriptors (phase offsets, duty factors), and publish stance/swing trajectories using the leg APIs. Include scripts/tests that drive one full gait cycle in simulation.
5. **Command Mixer and Body Pose Handling** – Implement the `CommandMixer`, `BodyPose`, and velocity-to-foothold mapping. Provide integration tests that translate sample velocity commands into gait controller requests.
6. **Xbox Controller Integration and Teleop Loop** – Add the `XboxControllerAdapter`, rate limiting, and the main control loop in `diamond.py` that ties everything together, gated by safety states (idle/enable/disable). Validate end-to-end on hardware with gradual motion tests.
