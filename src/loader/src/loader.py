import math
import pandas as pd
import numpy as np
import re
from pathlib import Path
import pickle
import sys
from abc import ABC, abstractmethod


class EntityState:
    """The EntityState class contains information about an entity at a single point in time.

    An EntityState represents an Entity at a certain timestamp. It contains information about position, yaw and speed. It can be identified via the frame_id and the entity_id.
    """

    def __init__(
        self,
        entity,
        timestamp: int,
        frame_id: int,
        x: float,
        y: float,
        vx: float,
        vy: float,
        vel: float,
        yaw: float,
    ):
        """Constructs an EntityState.

        Args:
            entity (Entity): the Entity this EntityState is a part of
            timestamp (int): the point in time to which the information in the EntityState corresponds to. Starts at 0. Time in ms TODO: ms?
            frame_id (int): another format for the timestamp
            x (float): the x coordinate
            y (float): the y coordinate
            vx (float): the velocity in the x direction
            vy (float): the velocity in the y direction
            vel (float): the resulting actual velocity
            yaw (float): the direction of the movement in radiant
        """
        self._entity_id = entity.entity_id
        self._length = entity.length
        self._width = entity.width
        self._classification = entity.classification
        self._timestamp = timestamp
        self._frame_id = frame_id
        self._x = x
        self._y = y
        self._vx = vx
        self._vy = vy
        self._vel = vel
        self._yaw = yaw

    @property
    def entity_id(self) -> int:
        """Getter for Entity ID.

        Returns:
            int: the id of the Entity that this EntityState is a part of
        """
        return self._entity_id

    @property
    def length(self) -> float:
        """Getter for the length of the Entity this EntityState belongs to.

        Returns:
            float: the length of the Entity
        """
        return self._length

    @property
    def width(self) -> float:
        """Getter for the width of the Entity this EntityState belongs to.

        Returns:
            float: the width of the Entity
        """
        return self._width

    @property
    def classification(self) -> str:
        """Getter for the classification of the Entity this EntityState belongs to.

        Returns:
            str: the classification of the Entity
        """
        return self._classification

    @property
    def frame_id(self) -> int:
        """Getter for frame ID.

        Returns:
            int: another format for the timestamp
        """
        return self._frame_id

    @property
    def timestamp(self) -> int:
        """Getter for timestamp.

        Returns:
            int: the timestamp
        """
        return self._timestamp

    @property
    def x(self) -> float:
        """Getter for x-coordinate.

        Returns:
            float: the x coordinate
        """
        return self._x

    @property
    def y(self) -> float:
        """Getter for y-coordinate.

        Returns:
            float: the y coordinate
        """
        return self._y

    @property
    def vx(self) -> float:
        """Getter for x-velocity.

        Returns:
            float: the x velocity
        """
        return self._vx

    @property
    def vy(self) -> float:
        """Getter for y-velocity.

        Returns:
            float: the y velocity
        """
        return self._vy

    @property
    def vel(self) -> float:
        """Getter for the total velocity.

        Returns:
            float: the velocity
        """
        return self._vel

    @property
    def yaw(self) -> float:
        """Getter for yaw.

        Returns:
            float: the yaw in radiant
        """
        return self._yaw

    @property
    def attribute_dict(self) -> dict[str, str or int or float]:
        """Dictionary with attribute names and attribute values.

        Returns:
            dict[str, str or int or float]: A dictionary with attribute names as keys and attribute values as values
        """
        return {
            name.replace("_", "").replace("entity", ""): value
            for name, value in self.__dict__.items()
        }


class IndEntityState(EntityState):
    """The IndEntityState class contains information about an entity at a single point in time and also its acceleration."""

    def __init__(
        self,
        entity,
        timestamp: int,
        frame_id: int,
        x: float,
        y: float,
        vx: float,
        vy: float,
        vel: float,
        ax: float,
        ay: float,
        accel: float,
        yaw: float,
    ):
        """Init function for IndEntityState.

        Args:
            see __init__ of EntityState
            ax (float): the acceleration in the x direction
            ay (float): the acceleration in the y direction
            accel (float): the total acceleration
        """
        super().__init__(entity, timestamp, frame_id, x, y, vx, vy, vel, yaw)
        self.__ax = ax
        self.__ay = ay
        self.__accel = accel

    @property
    def ax(self) -> float:
        """Getter for x acceleration.

        Returns:
            float: the x acceleration
        """
        return self.__ax

    @property
    def ay(self) -> float:
        """Getter for y acceleration.

        Returns:
            float: the y acceleration
        """
        return self.__ay

    @property
    def accel(self) -> float:
        """Getter for the total acceleration.

        Returns:
            float: the acceleration
        """
        return self.__accel


class Scene:
    """The Scene class encapsulates multiple EntityStates at a common time.

    A scene depicts the scenario at a given timestamp. It encapsules all EntityStates for the scenario that have this timestamp.
    """

    def __init__(self, timestamp: int):
        """Constructs a Scene."""
        self.__timestamp = timestamp
        self.__entity_states_dict = {}

    @property
    def entity_states(self) -> list[EntityState]:
        """Returns all EntityStates contained in the scene in a list.

        Returns:
            list[EntityState]: All EntityStates contained in the scene in a list.
        """
        return list(self.__entity_states_dict.values())

    @property
    def timestamp(self) -> int:
        """Getter for the timestamp of the Scene.

        Returns:
            int: the timestamp of the scene
        """
        return self.__timestamp

    def add_entity_state(self, entity_state: EntityState) -> None:
        """Adds an EntityState to the Scene.

        Args:
            entity_state (EntityState): the EntityState to be added
        """
        self.__entity_states_dict[entity_state.entity_id] = entity_state

    def get_entity_state(self, entity_id: int) -> EntityState:
        """Getter for the EntityState with the given entity_id.

        Args:
            entity_id (int): entity_id of the requested EntityState

        Returns:
            EntityState: EntityState corresponding to the entity_id
        """
        return self.__entity_states_dict[entity_id]


class Entity:
    """This class represents a single traffic participant.

    An Entity is a traffic participant. It contains an EntityState for every timestamp in which the Entity is part of the Scene.
    """

    def __init__(self, entity_id: int, length: float, width: float, classification: str):
        """Constructs an Entity.

        Args:
            entity_id (int): an individual identifier for the entity
            length (float): the length of the Entity in meters
            width (float): the width of the Entity in meters
            classification (str): the type of the Entity. Can be one of the following: [Car, Truck, Bike, Pedestrian]
        """
        self._entity_id = entity_id
        self.__length = length
        self.__width = width
        self.__classification = classification
        self.__entity_states_dict = {}

    @property
    def entity_id(self) -> int:
        """Getter for the ID of the Entity.

        Returns:
            int: the id of the Entity
        """
        return self._entity_id

    @property
    def length(self) -> float:
        """Getter for length.

        Returns:
            float: the length of the Entity in m"""
        return self.__length

    @property
    def width(self) -> float:
        """Getter for the width.

        Returns:
            float the width of the Entity in m"""
        return self.__width

    @property
    def classification(self) -> str:
        """Getter for classification of the Entity.

        Returns:
            str: the type of the Entity as a String"""
        return self.__classification

    def add_entity_state(self, entity_state: EntityState) -> None:
        """Adds an EntityState.

        Args:
            entity_state (EntityState): The EntityState to be added to the Entity
        """
        self.__entity_states_dict[entity_state._timestamp] = entity_state

    def get_entity_state(self, timestamp: int) -> EntityState:
        """Returns the EntityState with the given timestamp.

        Args:
            timestamp (int): the timestamp of the wanted EntityState

        Returns:
            EntityState: the EntityState for the specified timestamp
        """
        return self.__entity_states_dict.get(timestamp)

    @property
    def all_entity_states(self) -> dict[int, EntityState]:
        """Returns all EntityStates of the Entity with their timestamp as key.

        Returns:
            dict[int, EntityState]: a dictionary that contains all EntityStates of the Entity with their timestamp as key.
        """
        timestamp_dict = {}
        for entity_state in self.__entity_states_dict.values():
            timestamp_dict[entity_state.timestamp] = entity_state
        return timestamp_dict


class Scenario:
    """This class represents a bundle of multiple traffic participants over a certain period of time.

    The traffic participants are referred to as Entities.
    Each entity has different EntityStates. EntityStates is information about the Entity like velocity or position.
    A Scenario also contains Scenes depicting several EntityStates at a single point in time.
    """

    def __init__(self):
        """Constructs a Scenario."""
        self.__scene_dict = {}
        self.__entity_dict = {}

    def add_scene(self, scene: Scene) -> None:
        """Adds a Scene.

        Args:
            scene (Scene): the Scene to be added to the Scenario.
        """
        self.__scene_dict[scene.timestamp] = scene

    def add_entity(self, entity: Entity) -> None:
        """Adds an Entity.

        Args:
            entity (Entity): the Entity to be added to the Scenario.
        """
        self.__entity_dict[entity.entity_id] = entity

    def get_scene(self, timestamp: int) -> Scene:
        """Returns the Scene with the corresponding timestamp.

        Args:
            timestamp (int): the timestamp of the wanted Scene

        Return:
            Scene: the Scene with the specified timestamp
        """

        return self.__scene_dict[timestamp]

    def get_entity(self, entity_id: int) -> Entity:
        """Returns the Entity with the correspoding entity_id.

        Args:
            entity_id (int): the id of the wanted entity

        Return:
            Entity: the entity with the specified id"""
        return self.__entity_dict[entity_id]

    @property
    def timestamps(self) -> list[int]:
        """Returns all timestamps in the scenario.

        Returns:
            list[int]: the list with all timestamps in the scenario
        """
        return list(self.__scene_dict.keys())

    @property
    def entity_ids(self) -> list[int]:
        """Returns all IDs of the contained Entities.

        Returns:
            List: all IDs of the contained Entities.
        """
        return list(self.__entity_dict.keys())

    def create_scenes(self) -> None:
        """Creates scenes from the Entities and adds them to the Scenario.

        Iterates over all Entities and adds all of their EntityStates to Scenes the Dictionary __scene_dict with the timestamps as keys. Using Entity.all_entity_states."""
        for entity in self.__entity_dict.values():
            for (timestamp, entity_state) in entity.all_entity_states.items():
                if not self.__scene_dict.keys().__contains__(timestamp):
                    self.__scene_dict[timestamp] = Scene(timestamp)
                self.__scene_dict[timestamp].add_entity_state(entity_state)


class Loader:
    """This class is responsible for creating and handling multiple Scenarios consisting of Entities and Scenes from inD or taf csv dataset.

    The load_dataset(csv_path) function in the Loader class is called to load the csv file at the given location. It then constructs one Scenario with its Entities etc. per csv file."""

    def __init__(self):
        """Constructs a Loader."""
        self.scenarios = {}

    def check_path(self, csv_path: str) -> Path:
        """Checks if csv_path is an actual filesystem path.

        Args:
            csv_path (str): the path to a csv file e.g. /home/user/Documents/vehicle_tracks.csv

        Returns:
            PathObject: A path object. The details depend on the OS, see pathlib.Path(str)
        """
        assert isinstance(csv_path, str)
        csv_path = Path(csv_path)
        return csv_path

    def check_for_processed_data(self, csv_path: str) -> tuple[bool, Path]:
        """Checks if there is already processed data for the given csv file.

        Args:
            csv_path (str): the path to a csv file

        Returns:
            boolean: whether this path exists
            path object: the path to the processed data. See pathlib.Path(str)
        """
        processed_dataset_path = Path(csv_path).with_suffix(".pdata")
        return processed_dataset_path.exists(), processed_dataset_path

    def load_dataset(self, csv_path: str, clean_load=False, verbose=False) -> None:
        """Load dataset and save to a Scenario in Loader and as a pickle.

        Args:
            csv_path (str): the path to the csv file that is supposed to be loaded.

        Loads the csv file and constructs a Scenario with Entities etc. It is then saved as a pickle.
        """
        # checking if the dataset at csv_path has already been preprocessed
        preprocessed = self.check_for_processed_data(csv_path)
        if preprocessed[0] and not clean_load:
            if verbose:
                print("Found preprocessed dataset. Loading from {}".format(preprocessed[1]))
            self.load(csv_path, preprocessed[1])
            return

        # reads the dataset and checks if the dataset format is supported
        df = pd.read_csv(self.check_path(csv_path), delimiter=",")
        identifier = df.columns[0]
        scenario = None
        if identifier != "recordingId" and identifier != "track_id":
            sys.exit("No supported dataset format was found.")

        # checks if the dataset is in the inD format
        if identifier == "recordingId":
            if verbose:
                print("inD dataset was found!")
            delta_t = self.read_recording_meta_data(csv_path)

            classification_dict = self.read_classification_meta_data(csv_path)
            length_dict = df.copy(deep=True).set_index("trackId").to_dict()["length"]
            width_dict = df.copy(deep=True).set_index("trackId").to_dict()["width"]

            entity_id_col = df.pop("trackId")
            frame_id_col = df.pop("frame")
            timestamp_col = frame_id_col.copy(deep=True).multiply(delta_t)
            x_col = df.pop("xCenter")
            y_col = df.pop("yCenter")
            vx_col = df.pop("xVelocity")
            vy_col = df.pop("yVelocity")
            yaw_col = df.pop("heading").multiply(math.pi / 180)

            ax_col = df.pop("xAcceleration")
            ay_col = df.pop("yAcceleration")

            scenario = IndScenarioCreator(
                classification_dict,
                length_dict,
                width_dict,
                entity_id_col,
                timestamp_col,
                frame_id_col,
                x_col,
                y_col,
                vx_col,
                vy_col,
                yaw_col,
                ax_col,
                ay_col,
            ).create_scenario()
            scenario.create_scenes()

        # if the dataset is an Interaction/TAF dataset
        else:
            if verbose:
                print("Interaction/TAF dataset was found!")

            classification_dict = df.copy(deep=True).set_index("track_id").to_dict()["agent_type"]
            length_dict = df.copy(deep=True).set_index("track_id").to_dict()["length"]
            width_dict = df.copy(deep=True).set_index("track_id").to_dict()["width"]

            entity_id_col = df.pop("track_id")
            frame_id_col = df.pop("frame_id")
            timestamp_col = df.pop("timestamp_ms")
            x_col = df.pop("x")
            y_col = df.pop("y")
            vx_col = df.pop("vx")
            vy_col = df.pop("vy")
            yaw_col = df.pop("psi_rad")

            scenario = ScenarioCreator(
                classification_dict,
                length_dict,
                width_dict,
                entity_id_col,
                timestamp_col,
                frame_id_col,
                x_col,
                y_col,
                vx_col,
                vy_col,
                yaw_col,
            ).create_scenario()
            scenario.create_scenes()

        # Adds the scenario to the list of scenarios and saves the pickle file
        self.add_scenario(csv_path, scenario)
        self.save(csv_path)

    def save(self, csv_path: str) -> None:
        """Saves a Scenario to a pickle .pdata file.

        Args:
            csv_path (str): the path to which the finished Scenario is saved.
        """
        with open(str(Path(csv_path).with_suffix(".pdata")), "wb") as scenario_pickle:
            pickle.dump(self.scenarios[self.strip_number(csv_path)], scenario_pickle, 2)

    def load(self, csv_path: str, processed_dataset_path: str):
        """Loads a Scenario from preprocessed .pdata file and adds it to the Loader.

        Args:
            csv_path (str): the path of the unprocessed csv version of the dataset
            processed_dataset_path (str): the path of the processed dataset
        """
        with open(str(processed_dataset_path), "rb") as scenario_pickle:
            scenario = pickle.load(scenario_pickle)
            self.add_scenario(csv_path, scenario)

    def add_scenario(self, csv_path: str, scenario: Scenario):
        """Adds a Scenario to the list of Scenarios in Loader.

        Args:
            csv_path (str): the path to the unprocessed csv dataset.
            scenario (Scenario): the constructed scenario to be added to the scenario list.
        """
        self.scenarios[self.strip_number(csv_path)] = scenario

    def return_scenario(self, csv_path: str) -> Scenario:
        """Returns the Scenario to the dataset at the path from the Scenario list in the Loader.

        Args:
            csv_path (str): the path to the csv file of the scenario

        Returns:
            Scenario: the constructed scenario to the csv dataset
        """
        return self.scenarios[(self.strip_number(csv_path))]

    def strip_number(self, csv_path: str) -> str:
        """Returns the number from the dataset name.

        Args:
            csv_path (str): the path to the dataset that contains its number

        Returns:
            str: the number of the dataset from the file name
        """
        return re.sub("tracks.csv$", "", csv_path)

    def read_classification_meta_data(self, csv_path: str) -> dict:
        """Reads metadata of the dataset in order to obtain the classification in an inD dataset.

        Returns a dictionary of the trackId and its corresponding classification.
        """
        csv_path = self.strip_number(csv_path) + "tracksMeta.csv"
        df = pd.read_csv(
            self.check_path(csv_path),
            skipinitialspace=True,
            delimiter=",",
            usecols=["trackId", "class"],
        )
        df.set_index("trackId")
        return df.to_dict()["class"]

    def read_recording_meta_data(self, csv_path: str) -> float:
        """Reads metadata of the dataset in order to obtain the framerate of the inD dataset.

        Args:
            csv_paths (str): the path to the inD dataset

        Returns:
            float: the time between frames in milliseconds.
        """
        csv_path = self.strip_number(csv_path) + "recordingMeta.csv"
        frame_rate = pd.read_csv(
            self.check_path(csv_path),
            skipinitialspace=True,
            delimiter=",",
            usecols=["frameRate"],
            nrows=1,
        ).loc[0][0]
        delta_t = 1.0 / frame_rate * 1000.0
        return delta_t


class AbstractScenarioCreator(ABC):
    """Abstract class for Scenario creation from pandas columns.

    This exists to avoid code duplication because of the two actual ScenarioCreators
    """

    @abstractmethod
    def __init__(
        self,
        classification_dict: dict,
        length_dict: dict,
        width_dict: dict,
        entity_id_col: pd.core.series.Series,
        timestamp_col: pd.core.series.Series,
        frame_id_col: pd.core.series.Series,
        x_col: pd.core.series.Series,
        y_col: pd.core.series.Series,
        vx_col: pd.core.series.Series,
        vy_col: pd.core.series.Series,
        yaw_col: pd.core.series.Series,
    ):
        """Abstract constructor. Should not be called directly. Is called by the subclasses of AbstractScenarioCreator."""
        self._classification_dict = classification_dict
        self._length_dict = length_dict
        self._width_dict = width_dict
        self._entity_id_col = entity_id_col.tolist()
        self._timestamp_col = timestamp_col.tolist()
        self._frame_id_col = frame_id_col.tolist()
        self._x_col = x_col.tolist()
        self._y_col = y_col.tolist()
        self._vx_col = vx_col.tolist()
        self._vy_col = vy_col.tolist()
        self._vel_col = np.sqrt(np.add(np.square(vx_col), np.square(vy_col))).tolist()
        self._yaw_col = yaw_col.tolist()

    def create_scenario(self) -> Scenario:
        """Creates a Scenario and returns it.

        Creates a Scenario by adding all the Entities and then adding the EntityStates of those Entities
        """
        scenario = Scenario()
        for (key, value) in self._classification_dict.items():
            classification = value.lower()
            if classification == "bicycle":
                classification = "bike"
            scenario.add_entity(
                Entity(key, self._length_dict[key], self._width_dict[key], classification)
            )
        self.add_entity_states(scenario)
        return scenario

    @abstractmethod
    def add_entity_states(self, scenario: Scenario) -> None:
        """Adds EntityStates to the Entities of the given Scenario. Should only be defined in lower classes."""
        pass


class ScenarioCreator(AbstractScenarioCreator):
    """Creates a Scenario from pandas columns of a TAF dataset.

    Uses the columns of the TAF dataset to create a scenario using the super class AbstractScenario Creator
    """

    def __init__(
        self,
        classification_dict: dict,
        length_dict: dict,
        width_dict: dict,
        entity_id_col: pd.core.series.Series,
        timestamp_col: pd.core.series.Series,
        frame_id_col: pd.core.series.Series,
        x_col: pd.core.series.Series,
        y_col: pd.core.series.Series,
        vx_col: pd.core.series.Series,
        vy_col: pd.core.series.Series,
        yaw_col: pd.core.series.Series,
    ):
        """Constructor for the ScenarioCreator class.

        Args:
            classification_dict (dict): the dict that holds the information about the type of Entities
            length_dict (dict): the lengths of the Entities
            width_dict (dict): the widths of the Entities
            entity_id_col (pd.core.series.Series): the ids of the Entities
            timestamp_col (pd.core.series.Series): the timestamps of the EntityStates
            frame_id_col (pd.core.series.Series): the frame_ids of the EntityStates
            x_col (pd.core.series.Series): the x coordinates
            y_col (pd.core.series.Series): the y coordinates
            vx_col (pd.core.series.Series): the velocities in the x direction
            vy_col (pd.core.series.Series): the velocities in the y direction
            yaw_col (pd.core.series.Series): the yaw of the EntityStates
        """
        super().__init__(
            classification_dict,
            length_dict,
            width_dict,
            entity_id_col,
            timestamp_col,
            frame_id_col,
            x_col,
            y_col,
            vx_col,
            vy_col,
            yaw_col,
        )

    def add_entity_states(self, scenario: Scenario) -> None:
        """Iterates over the Entities in the provided scenario and adds their EntityStates.

        Args:
            scenario (Scenario): the scenario which the EntityStates are supposed to be added to
        """
        for i in range(0, len(self._entity_id_col)):
            entity = scenario.get_entity(self._entity_id_col[i])
            entity.add_entity_state(
                EntityState(
                    entity,
                    self._timestamp_col[i],
                    self._frame_id_col[i],
                    self._x_col[i],
                    self._y_col[i],
                    self._vx_col[i],
                    self._vy_col[i],
                    self._vel_col[i],
                    self._yaw_col[i],
                )
            )


class IndScenarioCreator(AbstractScenarioCreator):
    """Creates a Scenario from pandas columns of a inD dataset.

    Uses the columns of the inD dataset to create a scenario using the super class AbstractScenario Creator
    """

    def __init__(
        self,
        classification_dict: dict,
        length_dict: dict,
        width_dict: dict,
        entity_id_col: pd.core.series.Series,
        timestamp_col: pd.core.series.Series,
        frame_id_col: pd.core.series.Series,
        x_col: pd.core.series.Series,
        y_col: pd.core.series.Series,
        vx_col: pd.core.series.Series,
        vy_col: pd.core.series.Series,
        yaw_col: pd.core.series.Series,
        ax_col: pd.core.series.Series,
        ay_col: pd.core.series.Series,
    ):
        """The Constructor for the IndScenarioCreator.

        Assigns the values by calling the super constructor and assigning the acceleration variables

        Args:
            classification_dict (dict): the dict that holds the information about the type of Entities
            length_dict (dict): the lengths of the Entities
            width_dict (dict): the widths of the Entities
            entity_id_col (pd.core.series.Series): the ids of the Entities
            timestamp_col (pd.core.series.Series): the timestamps of the EntityStates
            frame_id_col (pd.core.series.Series): the frame_ids of the EntityStates
            x_col (pd.core.series.Series): the x coordinates
            y_col (pd.core.series.Series): the y coordinates
            vx_col (pd.core.series.Series): the velocities in the x direction
            vy_col (pd.core.series.Series): the velocities in the y direction
            yaw_col (pd.core.series.Series): the yaw of the EntityStates
            ax_col (pd.core.series.Series): the accelerations of the EntityStates
            ay_col (pd.core.series.Series): the accelerations of the EntityStates
        """
        super().__init__(
            classification_dict,
            length_dict,
            width_dict,
            entity_id_col,
            timestamp_col,
            frame_id_col,
            x_col,
            y_col,
            vx_col,
            vy_col,
            yaw_col,
        )
        self.__ax_col = ax_col.tolist()
        self.__ay_col = ay_col.tolist()
        self.__accel_col = np.sqrt(np.add(np.square(ax_col), np.square(ay_col))).tolist()

    def add_entity_states(self, scenario: Scenario) -> None:
        """Iterates over the Entities in the provided scenario and adds their EntityStates.

        Args:
            scenario (Scenario): the scenario which the EntityStates are supposed to be added to
        """
        for i in range(0, len(self._entity_id_col)):
            entity = scenario.get_entity(self._entity_id_col[i])
            entity.add_entity_state(
                IndEntityState(
                    entity,
                    self._timestamp_col[i],
                    self._frame_id_col[i],
                    self._x_col[i],
                    self._y_col[i],
                    self._vx_col[i],
                    self._vy_col[i],
                    self._vel_col[i],
                    self.__ax_col[i],
                    self.__ay_col[i],
                    self.__accel_col[i],
                    self._yaw_col[i],
                )
            )
