library(argparse)
library(DEP)
library(readr)
library(dplyr)
library(ggplot2)


print("OK")

# Create argument parser
parser <- ArgumentParser(description = 'Differential Expression Analysis and Plotting')

# Global arguments (Input/Output and Analysis parameters)
parser$add_argument('--input', dest='input', required=TRUE, help='Input RDS file containing imputed data')
parser$add_argument('--control', dest='control', required=TRUE, help='Control condition for differential testing')
parser$add_argument('--alpha', dest='alpha', type='double', default=0.05, help='Significance threshold (alpha) (default: 0.05)')
parser$add_argument('--lfc', dest='lfc', type='double', default=0.585, help='Log2 fold change threshold (default: log2(1.5) approx 0.585)')
parser$add_argument('--output-csv', dest='output_csv', default='dep_results.csv', help='Output filename for DE results CSV (default: dep_results.csv)')
parser$add_argument('--output-plot', dest='filename', default='plot.png', help='Output filename for the generated plot (default: plot.png)')

# Subparsers for plots
subparsers <- parser$add_subparsers(dest='plot_type', help='Type of plot to generate')

# PCA subparser
pca_parser <- subparsers$add_parser('pca', help='Generate PCA plot')
pca_parser$add_argument('--x', dest='pca_x', type='integer', default=1, help='Principal component for X axis (default: 1)')
pca_parser$add_argument('--y', dest='pca_y', type='integer', default=2, help='Principal component for Y axis (default: 2)')
pca_parser$add_argument('--n', dest='pca_n', type='integer', default=500, help='Number of top variable proteins to use (default: 500)')
pca_parser$add_argument('--point-size', dest='point_size', type='double', default=4, help='Point size (default: 4)')

# Volcano subparser
volcano_parser <- subparsers$add_parser('volcano', help='Generate Volcano plot')
volcano_parser$add_argument('--contrast', dest='contrast', required=TRUE, help='Contrast to plot (e.g. "Ubi1_vs_Ctrl")')
volcano_parser$add_argument('--label-size', dest='label_size', type='double', default=2, help='Label size (default: 2)')
volcano_parser$add_argument('--add-names', dest='add_names', action='store_true', default=TRUE, help='Add protein names to plot (default: TRUE)')

# Parse arguments
args <- parser$parse_args()



# Load data
if (!file.exists(args$input)) {
  stop(paste("Input file not found:", args$input))
}
data_imp <- readRDS(args$input)


# Differential Expression Analysis
# Test for differential expression relative to control
data_diff <- test_diff(data_imp, type = "control", control = args$control)

# Add rejection annotations
dep <- add_rejections(data_diff, alpha = args$alpha, lfc = args$lfc)

# Save DE results
write.csv(get_results(dep), file = file.path( args$output_csv), row.names = FALSE)
message(paste("DE results saved to", file.path(args$output_dir, args$output_csv)))

# Generate Plots based on subcommand
if (args$plot_type == 'pca') {
  p <- plot_pca(dep, x = args$pca_x, y = args$pca_y, n = args$pca_n, point_size = args$point_size)
} else if (args$plot_type == 'volcano') {
  p <- plot_volcano(dep, contrast = args$contrast, label_size = args$label_size, add_names = args$add_names)
}

# Save the plot
if (exists("p")) {
  ggsave(file.path(args$output_dir, args$filename), plot = p)
  message(paste("Plot saved to", file.path(args$output_dir, args$filename)))
}