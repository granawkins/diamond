import numpy as np
from typing import List, Tuple, Union

Matrix4x4 = np.ndarray

def create_dh_matrix(alpha: float, a: float, d: float, theta: float) -> Matrix4x4:
    """
    Creates a 4x4 Homogeneous Transformation Matrix (T) based on standard 
    Denavit-Hartenberg (D-H) parameters.
    
    T(i-1, i) = Rot(x, alpha) * Trans(x, a) * Trans(z, d) * Rot(z, theta)
    
    Args:
        alpha: Link twist (rotation about the X-axis).
        a: Link length (translation along the X-axis).
        d: Link offset (translation along the Z-axis).
        theta: Joint angle (rotation about the Z-axis).
        
    Returns:
        The 4x4 homogeneous transformation matrix.
    """
    c_a, s_a = np.cos(alpha), np.sin(alpha)
    c_t, s_t = np.cos(theta), np.sin(theta)
    
    # Standard D-H Matrix Structure
    T = np.array([
        [c_t,               -s_t,              0.0,             a],
        [s_t * c_a,         c_t * c_a,         -s_a,            -s_a * d],
        [s_t * s_a,         c_t * s_a,         c_a,             c_a * d],
        [0.0,               0.0,               0.0,             1.0]
    ])
    
    # Note: The second and third rows are sometimes swapped depending on the D-H convention (Standard vs. Modified)
    # This implementation uses the 'Standard' D-H convention for simplicity.
    return T

# -------------------------------------------------------------

def forward_kinematics(dh_params: List[Tuple[float, float, float, float]]) -> List[np.ndarray]:
    """
    Calculates the position of each joint in the kinematic chain
    from a list of D-H parameter sets.

    Args:
        dh_params: A list of (alpha, a, d, theta) tuples for each joint/link.

    Returns:
        A list of 3D position vectors [x, y, z] for each joint, including
        the base (origin) and end-effector. Length is len(dh_params) + 1.
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

    return positions

# -------------------------------------------------------------

# def inverse_kinematics_planar(target_xy: Union[Tuple[float, float], np.ndarray], 
#                               L1: float, L2: float) -> Union[Tuple[float, float], None]:
#     """
#     A lightweight, analytical Inverse Kinematics solver for a simple 2-link 
#     planar (RR) manipulator. 
    
#     This is an analytical method specific to a common 2-DOF structure. 
#     General IK for complex robots requires more involved methods 
#     (e.g., iterative/Jacobian-based).
    
#     Args:
#         target_xy: (x, y) coordinates of the desired end-effector position.
#         L1: Length of the first link.
#         L2: Length of the second link.

#     Returns:
#         (theta1, theta2) in radians, or None if the target is unreachable.
#     """
#     x, y = target_xy
#     D = (x**2 + y**2 - L1**2 - L2**2) / (2 * L1 * L2)

#     # Check for reachability
#     if D > 1.0 or D < -1.0:
#         return None # Target unreachable

#     # theta2 (Elbow-up configuration)
#     theta2 = np.arctan2(np.sqrt(1 - D**2), D) 
    
#     # theta1
#     beta = np.arctan2(L2 * np.sin(theta2), L1 + L2 * np.cos(theta2))
#     theta1 = np.arctan2(y, x) - beta
    
#     # Can also return the 'Elbow-down' solution: theta2 = np.arctan2(-np.sqrt(1 - D**2), D)
#     return theta1, theta2

# # -------------------------------------------------------------

# def get_inverse_transformation(T: Matrix4x4) -> Matrix4x4:
#     """
#     Calculates the inverse of a 4x4 Homogeneous Transformation Matrix (T).
    
#     T_inv is structured such that: 
#         R_inv = R_T (Rotation matrix is orthogonal)
#         p_inv = -R_T * p
    
#     This avoids a full, computationally expensive matrix inversion (np.linalg.inv)
#     by exploiting the properties of a transformation matrix.
    
#     Args:
#         T: The 4x4 transformation matrix.
        
#     Returns:
#         The inverse 4x4 transformation matrix T_inv.
#     """
#     R = T[:3, :3]
#     p = T[:3, 3]
    
#     R_T = R.T       # Transpose of rotation matrix is its inverse
#     p_inv = -R_T @ p # Inverse position vector
    
#     T_inv = np.eye(4)
#     T_inv[:3, :3] = R_T
#     T_inv[:3, 3] = p_inv
    
#     return T_inv
