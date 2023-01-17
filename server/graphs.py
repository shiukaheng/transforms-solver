# Abstract graph of 3D transformations through time
# Has a list of nodes and a list of edges
# Allows getting transforms (edges) for a given node in a given time (frame)
# Edge could be:
#   - rigid and known (so its pre-calibrated and given)
#   - rigid and unknown (needs solving, and can use multiple frames for better results)
#   - non-rigid and known (live tracking, so its given)
#   - non-rigid and unknown (needs solving, only possible if it is a loop)

# Abstract class for the above, we will implement a test class and a real class
# Transformations are 4x4 matrices
# The whole transformation graph can be solved by solving each node's transformation

# In the future we can use networkx to perform graph operations, but for now we use matrices for representation

# We will first need to define the type of each edge: "rigid-unknown", "rigid-known", "non-rigid-unknown", "non-rigid-known"
# We will also need to define the noise of each edge
# Then, we create a empty matrix of matrices, where each matrix is a 4x4 transformation matrix

# === Implementation ===
# We will create a custom class for the matrix of matrices, we will implement so that it can be indexed by a tuple (node, node)
# Each edge will also be associated with a type and a noise
# Also, setting a value will also set the inverse of the value in the other direction

# We will wrap around the matrix of matrices to create a graph class, which will have a list of nodes and a list of edges
# We model the transformation noise as a gaussian distribution

# ======================

# Then, we populate the matrix with the known transformations (rigid and known, non-rigid and known)

# Then, we estimate the non-rigid and unknown transformations, which will only work if the graph is a loop
# We combine multiple potential paths and use weighted least squares to estimate the transformation. The optimal weight will be the one that minimizes the error.
# The unsolvable nodes will be marked as such

# Next, we estimate the rigid and unknown transformations with a time window of n frames
# We can then similarly use weighted least squares to estimate the transformation. The optimal weight will be the one that minimizes the error.
# The unsolvable nodes will be marked as such
# This will also allow for potentially solving problems where the graph is not a loop, like AX = XB, where X is unknown

# Finally, we can use the graph to solve for the transformations of any node in any frame

from typing import Literal
import numpy as np
from tools import *

# These implementations are used for testing mostly, and online variants will be implemented later that uses only an iterative interface for solving; since in the online case, we will not know the whole graph at once

class TransformationGraph:
    def __init__(self, num_nodes: int, edges: list[tuple[int, int, Literal["rigid-unknown", "rigid-known", "non-rigid-unknown", "non-rigid-known"], float]], frames: int=1):
        """Initialize the transformation graph

        Parameters:
        num_nodes (int): Number of nodes in the graph
        edges (list[tuple[int, int, Literal["rigid-unknown", "rigid-known", "non-rigid-unknown", "non-rigid-known"], float]]): List of edges, where each edge is a tuple of (node1, node2, type, noise)
        frames (int): Number of frames in the graph
        """
        if frames < 1:
            raise Exception("Number of frames must be at least 1")
        # TODO: Have better representation of noise. Look into Kalman filters.

        # Create a matrix of matrices
        self._matrix = np.nan * np.ones((num_nodes, num_nodes, frames, 4, 4))

        # Create a seperate np object matrix for the edge types, set to None (not np.nan) initially
        self._types = np.empty((num_nodes, num_nodes), dtype=object)

        # Create a seperate matrix for the noise of each edge
        self._noise = np.nan * np.ones((num_nodes, num_nodes))

        # Set the matrix edge types and noise
        for edge in edges:
            # Set edge type
            self._types[edge[0], edge[1]] = edge[2]
            self._types[edge[1], edge[0]] = edge[2]
            # Set noise
            self._noise[edge[0], edge[1]] = edge[3]
            self._noise[edge[1], edge[0]] = edge[3]

        # TODO: This should be in test class instead
        # # Validate intra-group edges are rigid
        # for group in self._groups:
        #     for node1 in group:
        #         for node2 in group:
        #             if self._types[node1, node2, 0] != "rigid-known" and self._types[node1, node2, 0] != "rigid-unknown":
        #                 raise Exception("Inconsistent edge type in group")

        # Fill the identity matrices
        for i in range(num_nodes):
            for j in range(frames):
                self._matrix[i, i, j] = np.eye(4)

    def __getitem__(self, key: tuple[int, int, int]) -> np.ndarray:
        """Get the transformation matrix for a given edge and frame

        Parameters:
        key (tuple[int, int, int]): Tuple of (node1, node2, frame)

        Returns:
        np.ndarray: Transformation matrix
        """
        # Throw an error if there is no connection type
        if self._types[key[0], key[1]] == None:
            raise Exception("No connection type defined for edge")
        return self._matrix[key[0], key[1], key[2]]

    def __setitem__(self, key: tuple[int, int, int], value: np.ndarray):
        """Set the transformation matrix for a given edge and frame

        Parameters:
        key (tuple[int, int, int]): Tuple of (node1, node2, frame)
        value (np.ndarray): Transformation matrix
        """
        # Throw an error if there is no connection type
        if self._types[key[0], key[1]] == None:
            raise Exception("No connection type defined for edge")

        # Set the value
        self._matrix[key[0], key[1], key[2]] = value

        # Set the inverse
        self._matrix[key[1], key[0], key[2]] = np.linalg.inv(value)

    def get_type(self, key: tuple[int, int]) -> Literal["rigid-unknown", "rigid-known", "non-rigid-unknown", "non-rigid-known"]:
        """Get the type of a given edge

        Parameters:
        key (tuple[int, int]): Tuple of (node1, node2)

        Returns:
        Literal["rigid-unknown", "rigid-known", "non-rigid-unknown", "non-rigid-known"]: Type of the edge
        """
        return self._types[key[0], key[1]]

    def get_noise(self, key: tuple[int, int]) -> float:
        """Get the noise of a given edge

        Parameters:
        key (tuple[int, int]): Tuple of (node1, node2)

        Returns:
        float: Noise of the edge
        """
        return self._noise[key[0], key[1]]

    def get_nodes(self) -> list[int]:
        """Get the list of nodes in the graph

        Returns:
        list[int]: List of nodes
        """
        return list(range(self._matrix.shape[0]))

    def get_edges(self, node:int) -> list[tuple[int, Literal["rigid-unknown", "rigid-known", "non-rigid-unknown", "non-rigid-known"], float]]:
        """Get the list of edges for a given node

        Parameters:
        node (int): Node

        Returns:
        list[tuple[int, Literal["rigid-unknown", "rigid-known", "non-rigid-unknown", "non-rigid-known"], float]]: List of edges, where each edge is a tuple of (node, type, noise)
        """
        # print(f'Checking edges for node {node}')
        edges = []
        for i in range(self._matrix.shape[0]):
            edge_type = self._types[node, i]
            if edge_type != None:
                edges.append((i, self._types[node, i], self._noise[node, i]))
        # print(f'Found edges {edges}')
        return edges

    @property
    def num_nodes(self) -> int:
        """Get the number of nodes in the graph

        Returns:
        int: Number of nodes
        """
        return self._matrix.shape[0]

    @property
    def num_frames(self) -> int:
        """Get the number of frames in the graph

        Returns:
        int: Number of frames
        """
        return self._matrix.shape[2]

class TestTransformationGraph(TransformationGraph):
    """
    Specialized transformation graph for testing. Generates random ground truth transformations for each node and frame.
    """

    def __init__(self, num_nodes: int, edges: list[tuple[int, int, Literal["rigid-unknown", "rigid-known", "non-rigid-unknown", "non-rigid-known"], float]], frames: int):
        """Initialize the transformation graph

        Parameters:
        num_nodes (int): Number of nodes in the graph
        edges (list[tuple[int, int, Literal["rigid-unknown", "rigid-known", "non-rigid-unknown", "non-rigid-known"], float]]): List of edges, where each edge is a tuple of (node1, node2, type, noise)
        frames (int): Number of frames in the graph
        """
        super().__init__(num_nodes, edges, frames)
        # Identify node groups that are rigidly connected
        nodes = set(range(num_nodes))
        self._groups = []
        self._groupMap = dict()
        # For each node, use BFS to find all nodes that are rigidly connected. After that, remove all those nodes from the set. Repeat until all nodes are removed.
        while len(nodes) > 0:
            # Get a random node
            node = nodes.pop()

            # Add the node to the group
            group = set([node])

            # Add all rigidly connected nodes to the group
            queue = [node]
            while len(queue) > 0:
                # Get the next node
                node = queue.pop(0)

                # Add all rigidly connected nodes to the group
                for i in range(num_nodes):
                    if self._types[node, i] == "rigid-known" or self._types[node, i] == "rigid-unknown":
                        if i not in group:
                            group.add(i)
                            queue.append(i)

            # Remove all nodes in the group from the set
            nodes = nodes - group
            self._groups.append(group)
            for node in group:
                self._groupMap[node] = len(self._groups) - 1

        # Generate ground truth transformations        
        self._worldTransforms = np.zeros((num_nodes, frames, 4, 4))
        # Generate random transformations within groups, which stays the same for all frames
        # Since we assume a node can only be in one group, we can generate a random transform for every node
        # Individual nodes can be considered as a group of size 1
        intra_group_transforms = []
        for node in range(num_nodes):
            intra_group_transforms.append(generate_random_transform())
        # Generate random group transforms per frame
        group_transforms = []
        for i in range(frames):
            group_transforms.append([]) # Add a new frame
            for group in self.groups:
                group_transforms[i].append(generate_random_transform())
        # Now we can generate per node transforms for each frame
        for frame in range(frames):
            for node in range(num_nodes):
                group_id = self.get_group_id(node)
                # Set the ground truth transform
                self._worldTransforms[node, frame] = group_transforms[frame][group_id] @ intra_group_transforms[node]
                # print(f'Ground truth transform for node {node} in frame {frame}:')
                # print(self._worldTransforms[node, frame])
        # Second pass to generate relative transforms
        for frame in range(frames):
            for node in range(num_nodes):
                # For each edge, derive the relative transform from the ground truth
                for (neighbor, edge_type, noise) in self.get_edges(node):
                    # print(f'Calculating relative transform for edge ({node}, {neighbor}) in frame {frame}')
                    # Skip if edge is not known
                    if edge_type == "rigid-unknown" or edge_type == "non-rigid-unknown":
                        continue
                    # Get the relative transform using calc_relative_transform(from, to)
                    # print(node, neighbor, frame)
                    # print(self._worldTransforms[node, frame], self._worldTransforms[neighbor, frame])
                    relative_transform = calc_relative_transform(self._worldTransforms[node, frame], self._worldTransforms[neighbor, frame])
                    # print(relative_transform)
                    self[node, neighbor, frame] = relative_transform
        # Now we should be done!
        # Note, mentally we can think of the world origin as a separate node with an unknown non-rigid transformation to every other node

    def get_group_id(self, node: int) -> int:
        """Get the group id of a node

        Parameters:
        node (int): Node

        Returns:
        int: Group id
        """
        return self._groupMap[node]

    def get_group(self, group_id: int) -> set[int]:
        """Get the group of a node

        Parameters:
        group_id (int): Group id

        Returns:
        set[int]: Group
        """
        return self._groups[group_id]

    @property
    def groups(self) -> list[set[int]]:
        """Gets a copy of the list of groups

        Returns:
        list[set[int]]: List of groups
        """
        return self._groups.copy()

    def world_transform_to_dict(self) -> dict[int, dict[int, np.ndarray]]:
        """Converts the world transforms to a json compatible dictionary

        Returns:
        dict[int, dict[int, np.ndarray]]: Dictionary of world transforms
        """
        world_transforms = dict()
        for node in range(self.num_nodes):
            world_transforms[node] = dict()
            for frame in range(self.num_frames):
                world_transforms[node][frame] = self._worldTransforms[node, frame].tolist()
        return world_transforms
        # Local transform matrix and world transforms could be merged into a single matrix if we treat the world origin as a node

    def local_transforms_to_dict(self) -> dict[int, dict[int, dict[int, np.ndarray]]]:
        """Converts the local transforms to a json compatible dictionary

        Returns:
        dict[int, dict[int, dict[int, np.ndarray]]]: Dictionary of local transforms
        """
        local_transforms = dict()
        for node in range(self.num_nodes):
            local_transforms[node] = dict()
            for neighbor in range(self.num_nodes):
                local_transforms[node][neighbor] = dict()
                for frame in range(self.num_frames):
                    try:
                        local_transforms[node][neighbor][frame] = self[node, neighbor, frame].tolist()
                    except Exception:
                        # No connection
                        pass
        return local_transforms

    # def edges_to_dict(self) -> dict[int, dict[int, dict[str, str]]]:
    #     """Converts the edges to a json compatible dictionary

    #     Returns:
    #     dict[int, dict[int, dict[str, str]]]: Dictionary of edges
    #     """
    #     edges = dict()
    #     for node in range(self.num_nodes):
    #         edges[node] = dict()
    #         for neighbor in range(self.num_nodes):
    #             edges[node][neighbor] = dict()
    #             edges[node][neighbor]["type"] = self._types[node, neighbor, 0]
    #             edges[node][neighbor]["noise"] = self._types[node, neighbor, 1]
    #     return edges

    def to_dict(self) -> dict[str, dict]:
        """Converts the graph to a json compatible dictionary

        Returns:
        dict[str, dict]: Dictionary of graph
        """
        graph = dict()
        graph["world_transforms"] = self.world_transform_to_dict()
        graph["local_transforms"] = self.local_transforms_to_dict()
        # graph["edges"] = self.edges_to_dict()
        return graph

# TODO: Reimplement TransformationGraphs using iterators so that we can use the same solvers for real time and offline