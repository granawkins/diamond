import numpy as np
from numpy.typing import NDArray
from typing import Annotated, List, Tuple

DHParams = Tuple[float, float, float, float]  # (alpha, a, d, theta)
DHMatrix = Annotated[NDArray[np.float64], "shape[4, 4]"]
Vec3 = Annotated[NDArray[np.float64], "shape[3]"]

def degree_to_radians(degrees: float) -> float:
    return degrees * np.pi / 180.0

def radians_to_degrees(radians: float) -> float:
    return radians * 180.0 / np.pi

def create_dh_matrix(alpha: float, a: float, d: float, theta: float) -> DHMatrix:
    """
    Creates a 4x4 Homogeneous Transformation Matrix (T) based on standard 
    Denavit-Hartenberg (D-H) parameters.    
    """
    c_a, s_a = np.cos(alpha), np.sin(alpha)
    c_t, s_t = np.cos(theta), np.sin(theta)
    T = np.array([
        [c_t,               -s_t,              0.0,             a],
        [s_t * c_a,         c_t * c_a,         -s_a,            -s_a * d],
        [s_t * s_a,         c_t * s_a,         c_a,             c_a * d],
        [0.0,               0.0,               0.0,             1.0]
    ])
    return T

def forward_kinematics(dh_params: List[DHParams]) -> List[Vec3]:
    """
    Calculates the position of each joint in the kinematic chain
    from a list of D-H parameter sets.
    """
    positions = [np.array([0.0, 0.0, 0.0])]  # Start at origin
    T_accumulated = np.eye(4)

    # Chain the transformations and track positions after each link
    for params in dh_params:
        T_link = create_dh_matrix(*params)
        T_accumulated = T_accumulated @ T_link

        # Extract position from transformation matrix
        position = T_accumulated[:3, 3]
        positions.append(position)

    return [p.tolist() for p in positions]

def inverse_kinematics(target: Tuple[float, float, float],
                       dh_base: List[dict],
                       initial_angles: Tuple[float, float, float] = None,
                       max_iter: int = 100,
                       tolerance: float = 1e-3) -> Tuple[float, float, float] | None:
    """
    Numerical IK using Jacobian pseudoinverse method.
    Works with any DH parameter configuration.

    Args:
        target: (x, y, z) end-effector position
        dh_base: Base DH parameters (list of dicts with alpha, a, d, theta)
        initial_angles: Starting guess for joint angles in radians (for joints 1-3)
        max_iter: Maximum iterations
        tolerance: Position error threshold in mm

    Returns:
        (theta1, theta2, theta3) in radians, or None if no solution found
    """
    target_pos = np.array(target)

    # Initialize with default angles if not provided (joints 1-3)
    if initial_angles is None:
        angles = np.array([dh_base[i]["theta"] for i in range(1, 4)])
    else:
        angles = np.array(initial_angles)

    for _ in range(max_iter):
        # Compute forward kinematics with current angles
        dh_params = [
            (dh_base[i]["alpha"], dh_base[i]["a"], dh_base[i]["d"],
             angles[i-1] if 1 <= i <= 3 else dh_base[i]["theta"])
            for i in range(len(dh_base))
        ]
        positions = forward_kinematics(dh_params)
        current_pos = np.array(positions[-1])

        # Check if we've reached the target
        error = target_pos - current_pos
        if np.linalg.norm(error) < tolerance:
            return tuple(angles)

        # Compute Jacobian numerically
        J = np.zeros((3, 3))
        delta = 1e-6
        for i in range(3):
            angles_plus = angles.copy()
            angles_plus[i] += delta
            dh_params_plus = [
                (dh_base[j]["alpha"], dh_base[j]["a"], dh_base[j]["d"],
                 angles_plus[j-1] if 1 <= j <= 3 else dh_base[j]["theta"])
                for j in range(len(dh_base))
            ]
            pos_plus = np.array(forward_kinematics(dh_params_plus)[-1])
            J[:, i] = (pos_plus - current_pos) / delta

        # Compute pseudoinverse and update angles
        try:
            J_pinv = np.linalg.pinv(J)
            angles += J_pinv @ error * 0.5  # Damping factor for stability
        except np.linalg.LinAlgError:
            return None

    return None  # Failed to converge

if __name__ == "__main__":
    # Test IK/FK roundtrip for back-left leg configuration
    import math

    # Back-left leg DH params (from leg.py)
    dh_base = [
        {"alpha": 0, "a": 0, "d": 15.5, "theta": math.pi / 2},
        {"alpha": -math.pi / 2, "a": -9.3, "d": 21.1, "theta": -2.1},
        {"alpha": 0, "a": 63.25, "d": 0, "theta": -2},
        {"alpha": 0, "a": 82.5, "d": 0, "theta": 0},
    ]

    print("Testing IK/FK roundtrip:\n")

    test_angles = [(90, -120, -114), (90, -90, -90), (120, -60, -120)]

    for i, angles_deg in enumerate(test_angles, 1):
        print(f"Test {i}: angles = {angles_deg} deg")

        # Forward kinematics
        angles_rad = [degree_to_radians(a) for a in angles_deg]
        dh_params = [
            (dh_base[j]["alpha"], dh_base[j]["a"], dh_base[j]["d"],
             angles_rad[j] if j < 3 else dh_base[j]["theta"])
            for j in range(4)
        ]
        positions = forward_kinematics(dh_params)
        target = positions[-1]
        print(f"  FK -> position = ({target[0]:.2f}, {target[1]:.2f}, {target[2]:.2f})")

        # Inverse kinematics
        result = inverse_kinematics(tuple(target), dh_base, initial_angles=angles_rad[:3])
        if result is None:
            print("  IK -> FAILED TO CONVERGE\n")
            continue

        solved_deg = tuple(radians_to_degrees(a) for a in result)
        print(f"  IK -> angles = ({solved_deg[0]:.1f}, {solved_deg[1]:.1f}, {solved_deg[2]:.1f}) deg")

        # Check error
        error = [abs(solved_deg[j] - angles_deg[j]) for j in range(3)]
        max_error = max(error)
        status = "PASS" if max_error < 1.0 else "FAIL"
        print(f"  Error: {max_error:.3f} deg [{status}]\n")
