library(argparse)
library(dplyr)
library(readr)
library(tibble)
library(DEP)
library(ggplot2)

# Create argument parser
parser <- ArgumentParser(description = 'Preprocessing and quality control for proteomics data')

# Input file arguments
parser$add_argument('--data-unique', dest='data_unique', required=TRUE,
                    help='Path to data unique CSV file')
parser$add_argument('--experimental-design', dest='experimental_design', required=TRUE,
                    help='Path to experimental design CSV file')

# LFQ column prefix argument
parser$add_argument('--lfq-prefix', dest='lfq_prefix', default='LFQ.',
                    help='Prefix for LFQ columns (default: LFQ.)')

# Plot dimensions arguments
parser$add_argument('--plot-width', dest='plot_width', type='double', default=6,
                    help='Width of output plots in inches (default: 6)')
parser$add_argument('--plot-height', dest='plot_height', type='double', default=5,
                    help='Height of output plots in inches (default: 5)')
parser$add_argument('--plot-dpi', dest='plot_dpi', type='integer', default=300,
                    help='DPI for output plots (default: 300)')

# Filtering arguments
parser$add_argument('--filter-threshold', dest='filter_threshold', type='double', default=0,
                    help='Missingness threshold for filtering (default: 0)')

# Normalization method argument
parser$add_argument('--normalization-method', dest='norm_method', default='vsn',
                    choices=c('vsn', 'quantiles', 'none'),
                    help='Normalization method: vsn, quantiles, or none (default: vsn)')

# Imputation method argument
parser$add_argument('--imputation-method', dest='imp_method', default='MinProb',
                    choices=c('MinProb', 'man', 'MinDet', 'knn', 'QRILC', 'MLE', 'bpca'),
                    help='Imputation method (default: MinProb)')


# Output filenames for imputed data
parser$add_argument('--output-rds', dest='output_rds', default='data_imp.rds',
                    help='Filename for the imputed data R object (default: data_imp.rds)')
parser$add_argument('--output-csv', dest='output_csv', default='data_imp.csv',
                    help='Filename for the imputed data CSV (default: data_imp.csv)')

parser$add_argument('--combine-pdf', dest='combine_pdf', default='combined_plots.pdf',
                    help='Filename for the combined PDF of plots (default: combined_plots.pdf)')

# Parse arguments
args <- parser$parse_args()

# Read input files using parsed arguments
data_unique <- read_csv(args$data_unique, show_col_types = FALSE, na = character(0))
experimental_design <- read_csv(args$experimental_design, show_col_types = FALSE, na = character(0))
dim(data_unique)
dim(experimental_design)

# Use parsed LFQ prefix argument
LFQ_columns <- grep(args$lfq_prefix, colnames(data_unique))
data_se <- make_se(data_unique, LFQ_columns, experimental_design)
LFQ_columns <- grep(args$lfq_prefix, colnames(data_unique)) 
data_se_parsed <- make_se_parse(data_unique, LFQ_columns)



# Frequency plot
f <- plot_frequency(data_se)
ggsave(file.path( "freq_plot.png"), plot = f, 
       width = args$plot_width, height = args$plot_height, dpi = args$plot_dpi)

# Filter for proteins that are identified in all replicates of at least one condition
data_filt <- filter_missval(data_se, thr = args$filter_threshold)

ft <-  plot_numbers(data_filt)
ggsave(file.path( "filter_plot.png"), plot = ft, 
       width = args$plot_width, height = args$plot_height, dpi = args$plot_dpi)

c <- plot_coverage(data_filt)
ggsave(file.path( "coverage_plot.png"), plot = c, 
       width = args$plot_width, height = args$plot_height, dpi = args$plot_dpi)

# Normalize the data based on method argument
if (args$norm_method == 'vsn') {
  data_norm <- normalize_vsn(data_filt)
} else if (args$norm_method == 'quantiles') {
  data_norm <- normalize_quantiles(data_filt)
} else {
  data_norm <- data_filt
}

# Visualize normalization by boxplots for all samples before and after normalization
norm <-  plot_normalization(data_filt, data_norm)
ggsave(file.path("norm_plot.png"), plot = norm, 
       width = args$plot_width, height = args$plot_height, dpi = args$plot_dpi)

pre_imp <- plot_detect(data_filt)
ggsave(file.path("pre_imp_plot.png"), plot = pre_imp, 
       width = args$plot_width, height = args$plot_height, dpi = args$plot_dpi)

mis <- plot_missval(data_filt)

png(file.path( "miss_plot_1.png"),
    width = 1800, height = 1500, res = 300)

ComplexHeatmap::draw(mis)

dev.off()

# Impute data using method argument
data_imp <- impute(data_norm, fun = args$imp_method)

# Save imputed data as R object and CSV
saveRDS(data_imp, file = file.path( args$output_rds))
write.csv(get_df_wide(data_imp), file = file.path( args$output_csv), row.names = FALSE)

post_imp <- plot_imputation(data_norm, data_imp)
ggsave(file.path( "post_imp_plot.png"), plot = post_imp, 
       width = args$plot_width, height = args$plot_height, dpi = args$plot_dpi)

# Generate combined PDF if requested
if (TRUE) {
  library(gridExtra)
  
  pdf(file.path( args$combine_pdf), 
      width = args$plot_width, height = args$plot_height)
  
  print(f)
  print(ft)
  print(c)
  print(norm)
  print(pre_imp)
  
  # Print the ComplexHeatmap
  ComplexHeatmap::draw(mis)
  
  print(post_imp)
  
  dev.off()
  
  message("Combined PDF saved to: ", file.path( args$combine_pdf))
}

