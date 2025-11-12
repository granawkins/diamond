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
