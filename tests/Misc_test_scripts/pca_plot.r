#!/usr/bin/env Rscript

# Load libraries, # Load libraries After generating the wrapper please add clusterProfiler, org.Hs.eg.db and enrichplot packages in import
suppressPackageStartupMessages({
  library(argparse)
  library(ggplot2)
  library(enrichplot)
})

# Argument parser
parser <- ArgumentParser(description='GO Biological Process Enrichment Analysis')

parser$add_argument('-i', '--input', required=TRUE, help='Input gene list (one gene ID per line)')
parser$add_argument('-o', '--output_table', required=TRUE, help='Output CSV file for enrichment results')
parser$add_argument('-p', '--output_plot', required=TRUE, help='Output image file for dotplot')
parser$add_argument('-f', '--output_format', choices=c("pdf", "png", "svg"), default="png", help='Output image format (pdf, png, svg)')
parser$add_argument('-q', '--pvalue_cutoff', type='double', default=0.05, help='Adjusted p-value cutoff (default 0.05)')
parser$add_argument('-n', '--top_n', type='integer', default=20, help='Number of top terms to plot (default 20)')
parser$add_argument('-t', '--height', type='integer', default=1000, help='Plot height (default 1000)')
parser$add_argument('-w', '--width', type='integer', default=800, help='Plot width (default 800)')
parser$add_argument('-k', '--keytype', type="character", default='SYMBOL', help='KeyType parameter (default SYMBOL)')
parser$add_argument( '--ont', type="character", default='BP', help='ont (default BP)')
parser$add_argument('-m', '--pAdjustMethod', type="character", default='BH', help='pAdjustMethod (default BH)')


args <- parser$parse_args()

# Read gene list
gene_list <- read.table(args$input, stringsAsFactors=FALSE)$V1

# Perform GO enrichment (Biological Process)
ego <- enrichGO(gene          = gene_list,
                OrgDb         = org.Hs.eg.db,
                keyType       = args$keytype,
                ont           = args$ont,
                pAdjustMethod = args$pAdjustMethod,
                pvalueCutoff  = args$pvalue_cutoff,
                qvalueCutoff  = args$pvalue_cutoff)

# Save results table
write.csv(as.data.frame(ego), file=args$output_table, row.names=FALSE)

# Open graphics device based on format
if (args$output_format == "pdf") {
  pdf(args$output_plot, width=args$width , height=args$height)
} else if (args$output_format == "png") {
  png(args$output_plot, width=args$width , height=args$height , res=150)
} else if (args$output_format == "svg") {
  svg(args$output_plot, width=args$width , height=args$height )
}

# Plot or message if no enrichment found
if (nrow(as.data.frame(ego)) > 0) {
  print(dotplot(ego, showCategory=args$top_n))
} else {
  plot.new()
  text(0.5, 0.5, "No significant enrichment found", cex=1.5)
}
# Close device
dev.off()
