# Utilities
A collection of utility scripts used in multiple projects.

## Creating a virtual environment

There are two scripts that will install anaconda and set up a virtual environment called `tensorflow-CS`: `create_environment_gpu.sge` creates an environment that uses tensorflow with GPU support. If you want to use this variant, please make sure that CUDA, CuDNN, etc. are properly installed on your machine. The alternative `create_environment_cpu.sge` installs tensorflow with CPU support only. This can be considerably slower than the GPU variant, but can be run on any machine. Both scripts are prepared for being run on a Sun grid engine, but can be executed on a local machine as well by simply typing `./create_environment_gpu.sge` and `./create_environment_cpu.sge`, respectively.

The following dependencies are currently part of the environment:
* Python 3.5
* TensorFlow 1.10
* matplotlib
* scikit-learn
* Shapely
* imgaug

After installing the environment, you can activate it by typing `source activate tensorflow-CS`.


## Preparing grid search configurations

The python script `grid_search.py` can be used to create the individual configurations for a grid search. It should be invoked as follows:

`python grid_search.py template_file_name template_configuration`

The first parameter needs to point to a configuration file containing the parameters for the grid search and the second parameter must be the same of a section in this file. An example for such a file is given by `test.cfg`:

```
[default]
first = '/path/to/file'
second = 42
third = 0.9
fourth = ['one', 'two', 'three']
fifth = [1, 2, 3]
sixth = [0.2, 0.4]
seventh = '[7, 8, 9]'
```

If a parameter has only a single value (as e.g., first, second, and third in the example above), this value will be copied to all generated configurations. If a parameter has a list of values (such as fourth, fifth, and sixth), the script will iterate over all possible combinations of these values (so from "one-1-0.2" over "one-1-0.4" and "one-2-0.2" all the way to "three-3-0.4") and create one configuration for each combination. If you want to pass a list of values through unmodified (i.e., you want that the same list of values is copied to all generated configurations), you need to surround it with quotation marks (see seventh).
The script will create a new configuration file named `grid_search.cfg` as well as a text file named `params.txt`. The configuration file will contain all possible combinations of parameter settings and the text file will contain all names for the individual configurations. 

## Submitting an array job to the Sun grid engine

The script `submit_array_job.sge` can be used to submit a job to the Sun grid engine. Invoke it as follows:

`./submit_array_job.sh job params_file n c`

The first argument `job` is an sge script that will be submitted via `qsub`. The second argument `params_file` is the path to a file with parameters (e.g., the one created by the grid search script). The third argument `n` determines the number of times each configuration inside `params_file` will be run and the last argument `c` determines the number of configurations to be handled by a single task.

## compress_results.py

This script is to be used on the CSV file output of the `LearningConceptualDimensions` or the `LTN-in-Conceptual-Spaces` projects in order to average across multiple runs of the same configuration. It can be invoked as follows:
```python compress_results.py input_file_name output_file_name```

The script also takes an additional parameter `-g` or `--grouping`. If `--grouping` is not set, the script will aggregate all lines with the same configuration name into a single line by averaging across their values. This can be used to get a more robust estimation of a configuration's performance by averaging over a certain number of independent runs.

If `--grouping` is set for example to `la`, there will be as many groups as the `la` hyperparameter takes different values. If we have three possible values of `la`, namely 1.0, 2.0, and 3.0, then this script will aggregate all lines containing `la1.0` in their configuration name into a single line, all configurations containing `la2.0` into another row, and all configurations containing `la3.0` into a third row. This can be used to get a first idea about the overall influence of a given hyperparameter.


## statistical_analysis.py

The script `statistical_analysis` conducts some statistical analyses on the individual hyperparameters with respect to a set of given metrics. In short, it analyzes whether there are any statistically significant differences between the results obtained for different values of a given hyperparameter. After having printed out the respective statistics, some box plots are generated in order to illustrate the findings. The script can be run as follows, where `input_file_name` contains the path to the CSV file containing all data from the individual runs:
```python statistical_analysis.py input_file_name config_file_name data_set```
The parameter `config_file_name` refers to the config file storing the hyperparameters and metrics to use for the analysis. By default, the configurations `all_hyperparams` and `all_metrics` from this file are used. The parameter `data_set` indicates which of the data sets in the csv input file should be used. Lines belonging to a different data set will be skipped. The script also takes four optional arguments:
- `-t` or `--threshold`: The significance threshold to use for deciding on statistical significance (default: 0.01).
- `-o` or `--output_folder`: Output folder where the box plots are stored (default: current working directory).
- `-p` or `--parameters`: Name of the configuration within `config_file_name` that contains the hyperparameters to analyze (default: `all_hyperparams`).
- `-m` or `--metrics`: Name of the configuration within `config_file_name` that contains the metrics to analyze (default: `all_metrics`).
