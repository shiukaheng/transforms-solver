from server.graphs import TransformationGraph


class BaseSolver(object):
    """Base class for solvers that provides common functionality.
    """

    def __init__(self, graph:TransformationGraph):
        """Initialize the solver with a graph.
        """
        self.graph = graph

    # def solve(start_frame:int=0, end_frame:int=-1):
    #     """Solve the graph for the given frame range.
    #     """
    #     raise NotImplementedError

    def _encode_graph(self, frame:int=None):
        """Encode the graph as a JSON compatible dictionary, for use in the viewer.
        """
        # Get the graph as a dictionary
        graph_dict = self.graph.to_dict(frame=frame)
        