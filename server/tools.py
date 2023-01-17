import numpy as np
import quaternion
import matplotlib.pyplot as plt
import scipy
import scipy.optimize

def generate_random_transform():
    # Create random 4x4 affine transformation matrix with random rotation and translation
    # Rotation is a random quaternion
    # Translation is a random vector
    # Scale will be 1
    # Shear will be 0

    # Create random rotation matrix
    R = scipy.spatial.transform.Rotation.random().as_matrix()

    # Create random translation vector
    t = (np.random.rand(3) - 0.5) * 2

    # Scale is 1
    s = 1

    # Create matrix
    M = np.eye(4)
    M[:3, :3] = R
    M[:3, 3] = t
    M[3, 3] = s
    return M

def visualize_transform(T: list[np.ndarray]):
    # 3D plot
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    # Plot the three axes
    ax.plot([0, 1], [0, 0], [0, 0], color="gray")
    ax.plot([0, 0], [0, 1], [0, 0], color="gray")
    ax.plot([0, 0], [0, 0], [0, 1], color="gray")
    # Plot the transform
    # Original axes
    x = np.array([1, 0, 0, 1])
    y = np.array([0, 1, 0, 1])
    z = np.array([0, 0, 1, 1])
    o = np.array([0, 0, 0, 1])
    # Plot the axes
    ax.plot([o[0], x[0]], [o[1], x[1]], [o[2], x[2]], color="gray")
    ax.plot([o[0], y[0]], [o[1], y[1]], [o[2], y[2]], color="gray")
    ax.plot([o[0], z[0]], [o[1], z[1]], [o[2], z[2]], color="gray")
    for transform in T:
        # New axes
        x_new = transform @ x
        y_new = transform @ y
        z_new = transform @ z
        o_new = transform @ o
        # Plot the new axes
        ax.plot([o_new[0], x_new[0]], [o_new[1], x_new[1]], [o_new[2], x_new[2]], color="red")
        ax.plot([o_new[0], y_new[0]], [o_new[1], y_new[1]], [o_new[2], y_new[2]], color="green")
        ax.plot([o_new[0], z_new[0]], [o_new[1], z_new[1]], [o_new[2], z_new[2]], color="blue")
        # Label the number
        ax.text(o_new[0], o_new[1], o_new[2], str(T.index(transform)))
    # Set the limits
    ax.set_xlim(-1, 1)
    ax.set_ylim(-1, 1)
    ax.set_zlim(-1, 1)
    # Set the labels
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    # Show the plot
    plt.show()

def calc_relative_transform(from_transform: np.ndarray, to_transform: np.ndarray):
    # Calculate the relative transform from one transform to another
    # from_transform is the transform that we are starting from
    # to_transform is the transform that we are ending at
    # Returns the relative transform
    return np.linalg.inv(from_transform) @ to_transform