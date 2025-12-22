library(argparse)

# Create the main parser
parser <- ArgumentParser(description = "Demo R script with subcommands")

# Global argument
parser$add_argument("--verbose", action="store_true", help="Enable verbose output")

# Create subparsers object
subparsers <- parser$add_subparsers(dest = "command", help = "Subcommand to run")

# Add a "train" subcommand
train_parser <- subparsers$add_parser(
  "train", 
  help = "Train the model"
)
train_parser$add_argument("--epochs", type="integer", default=10, help="Number of epochs")
train_parser$add_argument("--lr", type="double", default=0.001, help="Learning rate")

# Add a "predict" subcommand
predict_parser <- subparsers$add_parser(
  "predict", 
  help = "Make predictions"
)
predict_parser$add_argument("--input-file", type="character", help="Input CSV file")
predict_parser$add_argument("--output-file", type="character", help="Output CSV file")

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
