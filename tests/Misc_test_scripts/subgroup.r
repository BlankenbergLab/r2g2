library(argparse)
library(ggplot2)

#Create the main parser
parser <- ArgumentParser(description = "Example script with all possible argument types")

# Positional argument (Required)
parser$add_argument("positional_arg", type="character", help="A required positional argument")

# Create a subgroup for input options
input_group <- parser$add_argument_group("Input Options")
input_group$add_argument("--input_file", type="character", help="Path to input file")
input_group$add_argument("--format", type="character", choices=c("csv", "tsv", "json"), 
                         default="csv", help="Format of input file (default: csv)")

# Create a subgroup for processing options
processing_group <- parser$add_argument_group("Processing Options")
processing_group$add_argument("--threads", type="integer", default=4, 
                              help="Number of threads to use (default: 4)") # Create a subgroup for input options
processing_group$add_argument("--normalize", action="store_true", # Create a subgroup for input options
                              help="Enable data normalization")
processing_group$add_argument("--threshold", type="double", default=0.5, 
                              help="Threshold value for filtering (default: 0.5)")
processing_group$add_argument("--categories", nargs="+", type="character",# Create a subgroup for input options
                              help="A list of category names (e.g., A B C)")

# Mutually exclusive group (Cannot use these together)
exclusive_group <- parser$add_mutually_exclusive_group()
exclusive_group$add_argument("--enable_feature", action="store_true", # Create a subgroup for input options
                             help="Enable a specific feature")
exclusive_group$add_argument("--disable_feature", action="store_true", 
                             help="Disable a specific feature")

# Create a subgroup for output options
output_group <- parser$add_argument_group("Output Options")
output_group$add_argument("--output_file", type="character", help="Path to output file")# Create a subgroup for input options
output_group$add_argument("--verbose", action="store_true", help="Enable verbose mode")# Create a subgroup for input options
output_group$add_argument("--log_level", type="character", choices=c("DEBUG", "INFO", "WARNING", "ERROR"),
                           default="INFO", help="Set logging level (default: INFO)")


print(parser)

# #Parse the arguments
args <- parser$parse_args()

# # Print parsed arguments
print(args)