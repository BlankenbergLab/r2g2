## Installation Instructions and Requirements
 

```
conda create  -n r2g2 -c conda-forge rpy2=3.6.2 r-base=4.4.3 python=3.12.11 r-r6=2.6.1 r-argparse=2.2.5 r-r6=2.6.1 r-argparse=2.2.5
conda activate r2g2
pip install r2g2==0.1.1 

```

### Example commands to generate wrappers for DEP Analysis Rscripts 


```

 r2g2-script -r ./DEP_preprocessing.r -o RRR -i 'name:data-unique,format:csv,label:Input data with LFQ values;name:experimental-design,format:csv,label:Experiment Design' --user_define_output_param 'name:output_rds,format:rds,label: Results,output_argument:--output-rds;name:output-csv,format:csv,label:Result CSV,output_argument:--output-csv;name:combine-pdf,format:pdf,label:Analysis Plots,output_argument:--combine_pdf'

```

```

r2g2-script -r ./DE_analysis.r -o RRR -i 'name:input,format:rds,label:My Custom Input Label' --user_define_output_param 'name:output_csv,format:csv,label:Path to input proteomics data file,output_argument:--output-csv;name:output-plot,format:png,label:Analysis plot,output_argument:--output-plot'

```


### Example Commands to run DEP Analysis using command line 


```
Rscript ./DEP_preprocessing.r  --data-unique ./tests/test_data/data_unique.csv   --experimental-design ./tests/test_data/data_unique.csv

```

```
Rscript ./DE_analysis.r --input ./tests/test_data/data_imp.rds --control Ctrl --output-dir new  volcano --contrast Ubi1_vs_Ctrl

Rscript ./DE_analysis.r --input ./tests/test_data/data_imp.rds --control Ctrl --output-dir testout pca

```


