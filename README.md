# Utilities
A collection of utility scripts used in multiple projects.

## Creating a virtual environment

There are two scripts that will install anaconda and set up a virtual environment called `tensorflow-CS`: `create_environment.sge` creates an environment that uses tensorflow with GPU support. If you want to use this variant, please make sure that CUDA, CuDNN, etc. are properly installed on your machine. The alternative `create_environment_cpu.sge` installs tensorflow with CPU support only. This can be considerably slower than the GPU variant, but can be run on any machine. Both scripts are prepared for being run on a Sun grid engine, but can be executed on a local machine as well by simply typing `./create_environment.sge` and `./create_environment_cpu.sge`, respectively.

The following dependencies are currently part of the environment:
* Python 3.5
* TensorFlow 1.4.1
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
