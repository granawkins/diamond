from controllers.servo import Servo

# Leg configuration mapping leg names to servo channels
LEG_CONFIG = {
    "front_left": {
        "lower_hip": 0,
        "upper_hip": 1,
        "shoulder": 2,
    },
    "back_left": {
        "lower_hip": 4,
        "upper_hip": 5,
        "shoulder": 6,
    },
    "back_right": {
        "lower_hip": 8,
        "upper_hip": 9,
        "shoulder": 10,
    },
    "front_right": {
        "lower_hip": 12,
        "upper_hip": 13,
        "shoulder": 14,
    },
}

class Leg:
    def __init__(self, name, pca):
        if name not in LEG_CONFIG:
            raise ValueError(f"Invalid leg name: {name}. Must be one of {list(LEG_CONFIG.keys())}")

        self.name = name
        self.config = LEG_CONFIG[name]
        self.shoulder = Servo(self.config["shoulder"], pca)
        self.upper_hip = Servo(self.config["upper_hip"], pca)
        self.lower_hip = Servo(self.config["lower_hip"], pca)

        self.reset()

    @property
    def angles(self):
        return self.lower_hip.angle, self.upper_hip.angle, self.shoulder.angle

    @angles.setter
    def angles(self, angles):
        self.lower_hip.angle = angles[0]
        self.upper_hip.angle = angles[1]
        self.shoulder.angle = angles[2]

    def reset(self):
        self.angles = (90, 90, 90)

    def up(self):
        x, y, z = self.angles
        value = -5 if "right" in self.name else 5
        self.angles = (x+value, y-value, z)

    def down(self):
        x, y, z = self.angles
        value = -5 if "right" in self.name else 5
        self.angles = (x-value, y+value, z)

    def forward_kinematics(self, shoulder_angle, upper_hip_angle, lower_hip_angle):
        pass

    def inverse_kinematics(self, x, y, z):
        pass

'''
Great video: https://www.youtube.com/watch?v=rA9tm0gTln8

# Define the 4x4 matrix type for clarity
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

def forward_kinematics(dh_params: List[Tuple[float, float, float, float]]) -> Matrix4x4:
    """
    Calculates the cumulative end-effector transformation matrix 
    from a list of D-H parameter sets.

    Args:
        dh_params: A list of (alpha, a, d, theta) tuples for each joint/link.

    Returns:
        The 4x4 transformation matrix T_base_to_end_effector.
    """
    # Start with the identity matrix (T_0_0)
    T_total = np.eye(4)
    
    # Chain the transformations: T_0_n = T_0_1 * T_1_2 * ... * T_{n-1}_n
    for params in dh_params:
        T_link = create_dh_matrix(*params)
        T_total = T_total @ T_link  # Matrix multiplication
        
    return T_total

# -------------------------------------------------------------

def inverse_kinematics_planar(target_xy: Union[Tuple[float, float], np.ndarray], 
                              L1: float, L2: float) -> Union[Tuple[float, float], None]:
    """
    A lightweight, analytical Inverse Kinematics solver for a simple 2-link 
    planar (RR) manipulator. 
    
    This is an analytical method specific to a common 2-DOF structure. 
    General IK for complex robots requires more involved methods 
    (e.g., iterative/Jacobian-based).
    
    Args:
        target_xy: (x, y) coordinates of the desired end-effector position.
        L1: Length of the first link.
        L2: Length of the second link.

    Returns:
        (theta1, theta2) in radians, or None if the target is unreachable.
    """
    x, y = target_xy
    D = (x**2 + y**2 - L1**2 - L2**2) / (2 * L1 * L2)

    # Check for reachability
    if D > 1.0 or D < -1.0:
        return None # Target unreachable

    # theta2 (Elbow-up configuration)
    theta2 = np.arctan2(np.sqrt(1 - D**2), D) 
    
    # theta1
    beta = np.arctan2(L2 * np.sin(theta2), L1 + L2 * np.cos(theta2))
    theta1 = np.arctan2(y, x) - beta
    
    # Can also return the 'Elbow-down' solution: theta2 = np.arctan2(-np.sqrt(1 - D**2), D)
    return theta1, theta2

# -------------------------------------------------------------

def get_inverse_transformation(T: Matrix4x4) -> Matrix4x4:
    """
    Calculates the inverse of a 4x4 Homogeneous Transformation Matrix (T).
    
    T_inv is structured such that: 
        R_inv = R_T (Rotation matrix is orthogonal)
        p_inv = -R_T * p
    
    This avoids a full, computationally expensive matrix inversion (np.linalg.inv)
    by exploiting the properties of a transformation matrix.
    
    Args:
        T: The 4x4 transformation matrix.
        
    Returns:
        The inverse 4x4 transformation matrix T_inv.
    """
    R = T[:3, :3]
    p = T[:3, 3]
    
    R_T = R.T       # Transpose of rotation matrix is its inverse
    p_inv = -R_T @ p # Inverse position vector
    
    T_inv = np.eye(4)
    T_inv[:3, :3] = R_T
    T_inv[:3, 3] = p_inv
    
    return T_inv

# -------------------------------------------------------------
'''