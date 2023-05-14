import unittest
import computation
import src.loader.src.loader as loader_module
import matplotlib.pyplot as plt
import lanelet2
import os
import igraph


def create_roadgraph_graph(lanelet_map):
    """Creates the igraph graph for the roadgraph.

    Args:
        lanelet_map (lanelet2.core.LaneletMap): The lanelet map created by lanelet2

    Returns:
        igraph.Graph: the roadgraph in the igraph format
    """
    traffic_rules = lanelet2.traffic_rules.create(
        lanelet2.traffic_rules.Locations.Germany, lanelet2.traffic_rules.Participants.Vehicle
    )
    routing_graph = lanelet2.routing.RoutingGraph(lanelet_map, traffic_rules)
    # TODO: Maybe implement stronger hashing function than SHA1 (SHA256?) or maybe encryption?
    # Name collisions should be avoided here as this could later be parallelized.
    file_path = f"./{hash(lanelet_map)}transformed_graph.graphml"
    routing_graph.exportGraphML(file_path)
    graph = igraph.Graph().Read_GraphML(file_path)
    os.remove(file_path)
    return graph


class TestTaf(unittest.TestCase):
    """Test case for the taf dataset"""

    def setUp(self):
        osm_path = "./src/computation/test/data/K733/K733_fix.osm"
        origin = (
            49.005306,
            8.4374089,
        )

        csv_path = "./src/loader/test/data/taf/vehicle_tracks_000.csv"
        loader = loader_module.Loader()
        loader.load_dataset(csv_path)
        scenario = loader.return_scenario(csv_path)
        timestamp = 153300
        scene = scenario.get_scene(timestamp)

        lanelet_map = computation.read_to_lanelet_map(osm_path, origin)

        matching_dict = computation.ProbabilisticMatchingDict(scene, lanelet_map)
        roadgraph = computation.Roadgraph(
            lanelet_map, matching_dict, create_roadgraph_graph(lanelet_map)
        )
        projection_identity_dict = computation.ProjectionIdentityDict(matching_dict)

        self.semantic_scene_graph = computation.SemanticSceneGraph(
            matching_dict, scene, roadgraph, projection_identity_dict, verbose=True
        )

    def test_create_dot_file(self):
        self.semantic_scene_graph.write_dot("./semantic_scene_graph.dot")


class TestShowData(unittest.TestCase):
    """Not really a test. Visualizes data from computation"""

    def setUp(self):
        # using TAF dataset
        osm_path = "./src/computation/test/data/K733/K733_fix.osm"
        origin = (
            49.005306,
            8.4374089,
        )
        csv_path = "./src/loader/test/data/taf/vehicle_tracks_000.csv"
        loader = loader_module.Loader()
        loader.load_dataset(csv_path)
        lanelet_map = computation.read_to_lanelet_map(osm_path, origin)
        self.timestamp = 153300
        self.scenario = loader.return_scenario(csv_path)
        self.entity_id_list = self.scenario.entity_ids
        self.lanelet_list = []
        for lanelet in lanelet_map.laneletLayer:
            self.lanelet_list.append(lanelet)

    def test_print_lanelets(self):
        """Function to print out a list of lanelets from the lanelet_map

        Args:
            lanelet_list (list): list of lanelets to be printed
        """
        for lanelet in self.lanelet_list:
            print(lanelet)

    def test_plot_lanelets(self):
        """Function, which plots a map of the street section"""
        # plot lanelets
        for lanelet in self.lanelet_list:
            for i in range(len(lanelet.leftBound)):
                plt.plot(lanelet.leftBound[i].x, lanelet.leftBound[i].y, "b.-")
            for j in range(len(lanelet.rightBound)):
                plt.plot(lanelet.rightBound[j].x, lanelet.rightBound[j].y, "r.-")

        # plot entities for a certain timestamp
        for entity_id in self.entity_id_list:
            current_entity = self.scenario.get_entity(entity_id)
            current_entity_state = current_entity.get_entity_state(self.timestamp)
            if current_entity_state is not None:
                plt.plot(current_entity_state.x, current_entity_state.y, "g.-")

        plt.axis("equal")
        plt.tight_layout()
        plt.show()


if __name__ == "__main__":
    unittest.main()
