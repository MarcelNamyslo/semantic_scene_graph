from src.loader.src.loader import Loader
import src.computation.coordination as computation_interface


class Controller:
    """Is supposed to act as a Controller as in MVC. Gets initiated and called by the cli module or a gui in the future."""

    def main(self, csv_path, osm_path, origin, timestamp_list, clean_load, verbose):
        """Runs the core modules loader and computation one after another.

        Args:
            csv_path (str): The path of the csv file containing the traffic data.
            osm_path (str): The path of the osm file containing the street data.
            origin (tuple(float)): The coordinates of the origin of the used dataset.
            timestamp_list (list(int)): The timestamps to be computed. If an empty list is provided, all timestamps of the dataset are computed.
            clean_load (bool): If the Loader module should reload the object structure from the csv file if there is an existing pickle.
            verbose (bool, optional): If verbose feedback is wanted. Defaults to False.

        Raises:
            e: a SystemExit which can be raised in the loader module
        """
        loader = Loader()
        try:
            loader.load_dataset(csv_path, clean_load=clean_load, verbose=verbose)
        except SystemExit as e:
            print("Dataset " + str(csv_path) + ": " + repr(e))
            raise e
        scenario = loader.return_scenario(csv_path)
        if not timestamp_list:
            timestamp_list = scenario.timestamps

        coordinator = computation_interface.Coordinator(
            scenario, osm_path, origin, timestamp_list, verbose
        )
        # computes the semantic scene graphs
        coordinator.coordinate()
