const FILE_TYPE_LABELS: Record<string, string> = {
	csv: 'CSV file',
	tsv: 'TSV file',
	txt: 'Text file',
	pdf: 'PDF document',
	json: 'JSON file',
	geojson: 'GeoJSON file',
	zip: 'ZIP archive',
	gz: 'Compressed archive',
	tar: 'Archive file',
	xlsx: 'Excel spreadsheet',
	xls: 'Excel spreadsheet',
	doc: 'Word document',
	docx: 'Word document',
	png: 'Image file',
	jpg: 'Image file',
	jpeg: 'Image file',
	gif: 'Image file',
	webp: 'Image file',
	tif: 'Image file',
	tiff: 'Image file',
	shp: 'Shapefile',
	gpkg: 'GeoPackage',
	kml: 'KML file',
	kmz: 'KMZ file',
	parquet: 'Parquet file',
	nc: 'NetCDF file',
	netcdf: 'NetCDF file',
	xml: 'XML file',
	html: 'HTML file',
	htm: 'HTML file',
	md: 'Markdown file',
	r: 'R script',
	rds: 'R data file',
	py: 'Python script',
	ipynb: 'Jupyter notebook',
	sql: 'SQL file',
};

export function fileExtension(fileName: string): string {
	const match = fileName.trim().match(/\.([^.]+)$/);
	return match ? match[1].toLowerCase() : '';
}

export function fileTypeLabel(fileName: string): string {
	const extension = fileExtension(fileName);
	if (!extension) return 'File';
	return FILE_TYPE_LABELS[extension] ?? `${extension.toUpperCase()} file`;
}
