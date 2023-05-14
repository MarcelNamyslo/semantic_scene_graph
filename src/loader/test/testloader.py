import unittest
import os
import time
from src.loader.src.loader import Loader, Scenario


class TestTaf(unittest.TestCase):
    """Test case for a taf dataset."""

    def setUp(self):
        self.loader_inst = Loader()
        self.csv_path = "./data/taf/vehicle_tracks_000.csv"
        self.pdata_path = "./data/taf/vehicle_tracks_000.pdata"
        tic = time.perf_counter()
        self.loader_inst.load_dataset(self.csv_path)
        toc = time.perf_counter()
        print(f"Ran taf Test Case in {toc- tic:0.4f} seconds")

    def test_scenario_creation_with_correct_data(self):
        self.assertIsInstance(self.loader_inst.return_scenario(self.csv_path), Scenario)

    def test_pdata_creation(self):
        self.assertTrue(os.path.exists(self.pdata_path))

    def tearDown(self):
        if os.path.exists(self.pdata_path):
            os.remove(self.pdata_path)


class TestInd(unittest.TestCase):
    """Test case for a inD dataset."""

    def setUp(self):
        self.loader_inst = Loader()
        self.csv_path = "./data/inD/01_tracks.csv"
        self.pdata_path = "./data/inD/01_tracks.pdata"
        tic = time.perf_counter()
        self.loader_inst.load_dataset(self.csv_path)
        toc = time.perf_counter()
        print(f"Ran inD Test Case in {toc- tic:0.4f} seconds")

    def test_scenario_creation_with_correct_data(self):
        self.assertIsInstance(self.loader_inst.return_scenario(self.csv_path), Scenario)

    def test_pdata_creation(self):
        self.assertTrue(os.path.exists(self.pdata_path))

    def tearDown(self):
        if os.path.exists(self.pdata_path):
            os.remove(self.pdata_path)


class TestBadPath(unittest.TestCase):
    def test_for_non_existent_path(self):
        """Test case for non-existent path."""
        pass


class TestBadDataset(unittest.TestCase):
    pass


if __name__ == "__main__":
    unittest.main()
