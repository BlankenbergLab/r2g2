 ### Installation Instructions and Requirements
 
```
conda create  -n r2g2 -c conda-forge rpy2=3.6.2 r-base=4.4.3 python=3.12.11 r-r6=2.6.1 r-argparse=2.2.5 r-r6=2.6.1 r-argparse=2.2.5
conda activate r2g2
pip install r2g2==0.1.1

```


# R2-G2 Automatically Generates Galaxy tools on a per-function basis from any R Library

```
usage: r2g2-package [-h] --name NAME [--package_name PACKAGE_NAME] [--package_version PACKAGE_VERSION] [--out OUT] [--create_load_matrix_tool]
                    [--galaxy_tool_version GALAXY_TOOL_VERSION]

options:
  -h, --help            show this help message and exit
  --name NAME           Package Name
  --package_name PACKAGE_NAME
                        [Conda] Package Name
  --package_version PACKAGE_VERSION
                        [Conda] Package Version
  --out OUT             Output directory
  --create_load_matrix_tool
                        Output a tool that will create an RDS from a tabular matrix
  --galaxy_tool_version GALAXY_TOOL_VERSION
                        Additional Galaxy Tool Version
```

# R2-G2 Automatically Generates Galaxy tools on R-Script based on argument parsing

```
usage: r2g2-script [-h] [-r R_SCRIPT_NAME] [-f R_SCRIPTS] [-o OUTPUT_DIR] [-p PROFILE] [-d DESCRIPTION] [-s DEPENDENCIES] [-v TOOL_VERSION] [-c CITATION_DOI]
                   [-u USER_DEFINE_OUTPUT_PARAM] [-i USER_DEFINE_INPUT_PARAM]

options:
  -h, --help            show this help message and exit
  -r R_SCRIPT_NAME, --r_script_name R_SCRIPT_NAME
                        Provide the path of an R script...
  -f R_SCRIPTS, --r_scripts R_SCRIPTS
                        A path of a text file containing full path of R scripts.
  -o OUTPUT_DIR, --output_dir OUTPUT_DIR
  -p PROFILE, --profile PROFILE
  -d DESCRIPTION, --description DESCRIPTION
                        tool based on R script
  -s DEPENDENCIES, --dependencies DEPENDENCIES
                        Extract dependency information..
  -v TOOL_VERSION, --tool_version TOOL_VERSION
                        Galaxy tool version..
  -c CITATION_DOI, --citation_doi CITATION_DOI
                        Comma separated Citation DOI.
  -u USER_DEFINE_OUTPUT_PARAM, --user_define_output_param USER_DEFINE_OUTPUT_PARAM
                        Rather guessing output params, user can define output params in specific format. Ex. 'name:protein,format:pdb,label:protein
                        file,from_work_directory;name:ligand,format:pdb,label:ligand file,from_work_directory'
  -i USER_DEFINE_INPUT_PARAM, --user_define_input_param USER_DEFINE_INPUT_PARAM
                        List of input parameters to be treated as data inputs, comma separated. Ex. 'input_file,reference_data'
```


### Examples

For a complete example of using R2G2 with the DEP Analysis package, please see the [DEP Analysis Scripts README](tests/DEP_Analysis_Scripts/README.md).
