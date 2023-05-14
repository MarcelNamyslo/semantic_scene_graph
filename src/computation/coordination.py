import time
import ray
import lanelet2
import igraph
import os
import src.computation.computation as computation

MAX_SERIAL_TIMESTAMPS = 40


# Print iterations progress. source: greenstick on stackoverflow.com
def progress_bar(iterable, prefix="", suffix="", decimals=1, length=100, fill="█", print_end="\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iterable    - Required  : iterable object (Iterable)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    total = len(iterable)

    # Progress Bar Printing Function
    def print_progress_bar(iteration):
        percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
        filled_length = int(length * iteration // total)
        bar = fill * filled_length + "-" * (length - filled_length)
        print(f"\r{prefix} |{bar}| {percent}% {suffix}", end=print_end)

    # Initial Call
    print_progress_bar(0)
    # Update Progress Bar
    for i, item in enumerate(iterable):
        yield item
        print_progress_bar(i + 1)
    # Print New Line on Complete
    print()


def progress_iterable(iterable, verbose=False):
    """Calls progress_bar if not verbose and otherwise just returns the iterable.
    Outputting a progress bar and having verbose output at the same time caused some problems.

    Args:
        iterable (iterable): An iterable for the progress bar to iterate over
        verbose (bool, optional): if verbose output is wanted. Defaults to False.

    Returns:
        iterable: the same iterable that has been provided
    """
    if verbose:
        return iterable
    else:
        return progress_bar(iterable, prefix="Progress:", suffix="Complete", length=50)


class Coordinator:
    def __init__(
        self, scenario, osm_path, origin, timestamp_list, verbose, output_dir="./dotGraphOutput"
    ):
        self.scenario = scenario
        self.osm_path = osm_path
        self.origin = origin
        self.verbose = verbose
        self.timestamp_list = timestamp_list
        self.output_dir = output_dir
        self.results = []

    def coordinate(self):
        lanelet_map = computation.read_to_lanelet_map(self.osm_path, self.origin)

        traffic_rules = lanelet2.traffic_rules.create(
            lanelet2.traffic_rules.Locations.Germany, lanelet2.traffic_rules.Participants.Vehicle
        )
        routing_graph = lanelet2.routing.RoutingGraph(lanelet_map, traffic_rules)
        file_path = f"./{hash(lanelet_map)}transformed_graph.graphml"
        routing_graph.exportGraphML(file_path)
        graph = igraph.Graph().Read_GraphML(file_path)
        os.remove(file_path)

        if not os.path.exists(self.output_dir):
            os.mkdir(self.output_dir)

        if len(self.timestamp_list) < MAX_SERIAL_TIMESTAMPS:
            for timestamp in progress_iterable(self.timestamp_list, self.verbose):
                self.compute(timestamp, graph)
        else:
            # Start Ray
            tic = time.perf_counter()
            ray.init()
            toc = time.perf_counter()
            if self.verbose:
                print(f"STARTING RAY TOOK {toc-tic:0.4f} seconds")
            for timestamp in progress_iterable(self.timestamp_list, self.verbose):
                self.compute_in_parallel.remote(self, timestamp, graph)

    @ray.remote
    def compute_in_parallel(self, timestamp, graph):
        """Runs the compute function in parallel

        Args:
            timestamp (int): the timestamp to compute
            graph (igraph.Graph): the routing graph of the scenario
        """
        self.compute(timestamp, graph)

    def compute(self, timestamp, graph):
        """Takes all the necessary steps to compute a Semantic Scene Graph. Writes the finished graph to the specified output directory

        Args:
            timestamp (int): the timestamp to compute
            graph (igraph.Graph): the routing graph of the scenario
        """
        scene = self.scenario.get_scene(timestamp)

        lanelet_map = computation.read_to_lanelet_map(self.osm_path, self.origin)
        matching_dict = computation.ProbabilisticMatchingDict(scene, lanelet_map)
        roadgraph = computation.Roadgraph(lanelet_map, matching_dict, graph, self.verbose)
        projection_identity_dict = computation.ProjectionIdentityDict(matching_dict, self.verbose)

        semantic_scene_graph = computation.SemanticSceneGraph(
            matching_dict, scene, roadgraph, projection_identity_dict
        )
        semantic_scene_graph.write_dot(f"{self.output_dir}/semantic_scene_graph{timestamp}.dot")
