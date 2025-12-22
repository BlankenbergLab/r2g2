library(argparse)

# Create the main parser
parser <- ArgumentParser(description = "Demo R script with subcommands")

# Global argument
parser$add_argument("--verbose", action="store_true", help="Enable verbose output")

# Create subparsers object
subparsers <- parser$add_subparsers(dest = "command", help = "Subcommand to run")

# Add a "train" subcommand
train_parser <- subparsers$add_parser( "train",  help = "Train the model")
train_parser$add_argument("--epochs", type="integer", default=10, help="Number of epochs")
train_parser$add_argument("--lr", type="double", default=0.001, help="Learning rate")

# Add a "predict" subcommand
predict_parser <- subparsers$add_parser( "predict", help = "Make predictions")
predict_parser$add_argument("--input-file", type="character", help="Input CSV file")
predict_parser$add_argument("--output-file", type="character", help="Output CSV file")

# Create a subgroup for input options
input_group <- parser$add_argument_group("Input Options")
input_group$add_argument("--input_file", type="character", help="Path to input file")
input_group$add_argument("--format", type="character", choices=c("csv", "tsv", "json"), 
                         default="csv", help="Format of input file (default: csv)")

# Create a subgroup for processing options
processing_group <- parser$add_argument_group("Processing Options")
processing_group$add_argument("--threads", type="integer", default=4, help="Number of threads to use (default: 4)") # Create a subgroup for input options
processing_group$add_argument("--normalize", action="store_true", help="Enable data normalization")
processing_group$add_argument("--threshold", type="double", default=0.5, help="Threshold value for filtering (default: 0.5)")
processing_group$add_argument("--categories", nargs="+", type="character",help="A list of category names (e.g., A B C)")

# Mutually exclusive group (Cannot use these together)
exclusive_group <- parser$add_mutually_exclusive_group()
exclusive_group$add_argument("--enable_feature", action="store_true", help="Enable a specific feature")
exclusive_group$add_argument("--disable_feature", action="store_true",help="Disable a specific feature")

exclusive_group_1 <- parser$add_mutually_exclusive_group()
exclusive_group_1$add_argument("--enable_feature_1", action="store_true", help="Enable a specific feature")
exclusive_group_1$add_argument("--disable_feature_2", action="store_true",help="Disable a specific feature")

# Create a subgroup for output options
output_group <- parser$add_argument_group("Output Options")
output_group$add_argument("--output_file", type="character", help="Path to output file")# Create a subgroup for input options
output_group$add_argument("--log_level", type="character", choices=c("DEBUG", "INFO", "WARNING", "ERROR"), default="INFO", help="Set logging level (default: INFO)")

# Parse the arguments
args <- parser$parse_args()

# Handle logic based on subcommand
if (args$command == "train") {
  cat("Training model for", args$epochs, "epochs with lr =", args$lr, "\n")
} else if (args$command == "predict") {
  cat("Predicting using", args$input_file, "and saving to", args$output_file, "\n")
} else {
  parser$print_help()
}
