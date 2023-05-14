# semantic_scene_graph_ws

![an example of a Semantic Scene Graph](docs/SemanticSceneGraph.png)

The Semantic Scene Graph model is utilized to describe traffic scenes in relation to road topology and to compare different scenes with each other, independent of the location. The relations between traffic participants are described by semantically classified edges.  
This abstract description facilitates machine readability and makes it practical to apply machine learning methods to traffic scenes.

## Documentation

Either look at the documentation [here](https://student.kit.edu/~ulmcn/ssg_docs)

...or download the documentation in a .zip archive [here](https://bwsyncandshare.kit.edu/s/WoEwA9oDWykxswq).

## Structure

This Project is split up into this main repository and three submodules:

- [Loader](https://git.scc.kit.edu/uyfwd/semantic_scene_graph_loader)
- [Computation](https://git.scc.kit.edu/uyfwd/semantic_scene_graph_computation)
- [Visualization](https://git.scc.kit.edu/uyfwd/semantic_scene_graph_visualization)

To use this main repository and the CLI functionality you need to at least pull both the Loader and the Computation module.

### Architecture Overview

![overview of the architecture](docs/Architecture Overview - rough.svg)

See a more detailed view <details><summary>here</summary>
![detailed architecture overview](docs/Architecture Overview - detailed.svg)

</details> or in the separate submodules.

## Development

For Lanelet2 development we recommend using our [lanelet2 docker container](https://github.com/tuschla/kamaro-container) running the latest version of Lanelet2 from the Lanelet2 git repository. See the linked repository for building instructions.  
Pull submodules for the first time with

```sh
./init.sh
```

and pull the latest commit of main of the submodules with

```sh
./update_submodules.sh
```

and lastly install dev dependencies with

```sh
pip3 install -r requirements-dev.txt
```

## Dependencies

- [Lanelet2](https://github.com/fzi-forschungszentrum-informatik/Lanelet2) for computation submodule
- Python 3.9 for computation and loader
  - Python dependencies can be installed with `pip3 install -r requirements.txt`. See [requirements.txt](https://git.scc.kit.edu/uyfwd/semantic_scene_graph_ws/-/blob/main/requirements.txt). This will install the [Loader](https://git.scc.kit.edu/uyfwd/semantic_scene_graph_computation/-/blob/main/requirements.txt) and [Computation](https://git.scc.kit.edu/uyfwd/semantic_scene_graph_loader/-/blob/main/requirements.txt) requirements as well.
- nodejs and npm for [Visualization](https://git.scc.kit.edu/uyfwd/semantic_scene_graph_visualization#install-dependencies).

## Usage

Run `python cli.py [OPTIONS]`. The calculated Semantic Scene Graphs are being written to the folder `dotGraphOutput`.

```none
usage: cli.py [-h] [-v] [--list_aliases] [--save_alias ALIAS] [-c] [-a ALIAS [timestamps ...]] csv_path osm_path x_origin y_origin [timestamps ...]

Create a Semantic Scene Graph from a dataset in the TAF or the inD format.

positional arguments:
  csv_path              the csv file location. The csv file can either be formatted in the TAF format or in the inD format.
  osm_path              the osm file location. The osm file describes the map of the traffic scenario
  x_origin              the x value of the origin of the provided dataset
  y_origin              the y value of the origin of the provided dataset
  timestamps            all timestamps that are supposed to be calculated. Default if left empty is all timestamps in the csv file.

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         activates verbose cli feedback
  --list_aliases        lists all saved locations and their aliases
  --save_alias ALIAS    save the given csv, osm and origin information so it can be used with the alias later
  -c, --clean_load      loads the csv file again if it already has been loaded
  -a ALIAS [timestamps ...], --alias ALIAS [timestamps ...]
                        loads the dataset of the given alias and creates its Semantic Scene Graphs for either the provided timestamps
                        or the whole scenario. This option has to be the last option if it is used.

```

### Example usage

```none
python cli.py ./src/loader/test/data/taf/vehicle_tracks_000.csv ./src/computation/test/data/K733/K733_fix.osm 49.005306 8.4374089 --save_alias taf000
```

Loads the Loader, runs the computation and saves the Semantic Scene Graphs for all timestamps in the dataset. Saves the csv and osm paths along the origin coordinates into cli_aliases.csv.

```none
python cli.py -a taf000 153300
```

Loads the information (csv_path, osm_path, origin) saved on the alias `taf000` and runs the program with it but only on timestamp `153300`.

## Troubleshooting during development

### Can't find installed Lanelet2

Run `source devel/setup.bash` from the directory in which Lanelet is installed.

### Can't find parent module

Run `export PYTHONPATH=path/to/parent/module/` to register the parent module as a python module. Adding relative paths does not work as well because it actually writes the relative path into the variable.
