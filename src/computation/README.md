# semantic_scene_graph_computation

This is a part of [semantic_scene_graph](https://git.scc.kit.edu/uyfwd/semantic_scene_graph_ws).

Computes a graph that describes the relation between entities in a traffic scene for each of several scenes. A scenario constructed by [semantic_scene_graph_loader](https://git.scc.kit.edu/uyfwd/semantic_scene_graph_loader) is used.

![computation class diagram](docs/computation_uml_class.svg)

The graph is then outputted as a .dot graph. This graph can then be displayed by [semantic_scene_graph_visualization](https://git.scc.kit.edu/uyfwd/semantic_scene_graph_visualization).

## Documentation

See the [documentation](https://student.kit.edu/~ulmcn/ssg_docs) of the whole [semantic_scene_graph](https://git.scc.kit.edu/uyfwd/semantic_scene_graph_ws) project.

## Usage

1. initialize an object of the Coordinator class with the wanted parameters
2. run `your_coordinator_object.coordinate()`
3. wait

### Example

The main function in [controller.py](https://git.scc.kit.edu/uyfwd/semantic_scene_graph_ws/-/blob/main/controller.py) shows how it is done.

```python
def main(self, csv_path, osm_path, origin, timestamp_list, clean_load, verbose):
        """Runs the core modules one after another"""
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
        coordinator.coordinate()
        # computes the semantic scene graphs
```
