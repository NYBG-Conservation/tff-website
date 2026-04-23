import type { PageServerLoad } from './$types';

interface PressItem {
	title: string;
	publication?: string;
	date?: string;
	description?: string;
	link?: string;
}

function parseCSVLine(line: string): string[] {
	const values: string[] = [];
	let current = '';
	let inQuotes = false;

	for (let i = 0; i < line.length; i++) {
		const char = line[i];
		const nextChar = line[i + 1];

		if (char === '"') {
			if (inQuotes && nextChar === '"') {
				// Escaped quote
				current += '"';
				i++; // Skip next quote
			} else {
				// Toggle quote state
				inQuotes = !inQuotes;
			}
		} else if (char === ',' && !inQuotes) {
			// End of field
			values.push(current.trim());
			current = '';
		} else {
			current += char;
		}
	}

	// Add the last field
	values.push(current.trim());

	return values;
}

function parsePressCSV(csvText: string): PressItem[] {
	const lines = csvText.trim().split(/\r?\n/);
	if (lines.length < 2) return [];

	// Parse header
	const headers = parseCSVLine(lines[0]).map((h) => h.trim().toLowerCase().replace(/^"|"$/g, ''));

	// Parse data rows
	const pressItems: PressItem[] = [];
	for (let i = 1; i < lines.length; i++) {
		const line = lines[i].trim();
		if (!line) continue;

		const values = parseCSVLine(line).map((v) => v.replace(/^"|"$/g, ''));
		if (values.length === 0 || !values[0]) continue;

		const pressItem: PressItem = {
			title: ''
		};

		headers.forEach((header, index) => {
			const value = values[index] || '';
			switch (header) {
				case 'title':
					pressItem.title = value;
					break;
				case 'publication':
					if (value) {
						pressItem.publication = value;
					}
					break;
				case 'date':
					if (value) {
						pressItem.date = value;
					}
					break;
				case 'description':
					if (value) {
						pressItem.description = value;
					}
					break;
				case 'link':
					if (value) {
						pressItem.link = value;
					}
					break;
			}
		});

		if (pressItem.title) {
			pressItems.push(pressItem);
		}
	}

	return pressItems;
}

/** Parse date string (e.g. "10-15-2025", "6-2-2025") as month-day-year. Returns timestamp for sorting; invalid/missing → 0. */
function parsePressDate(dateString?: string): number {
	if (!dateString?.trim()) return 0;
	const parts = dateString.trim().split(/[-\/]/).map((p) => parseInt(p, 10));
	if (parts.length < 3) return 0;
	const [month, day, year] = parts;
	if (!month || !day || !year) return 0;
	const date = new Date(year, month - 1, day);
	return isNaN(date.getTime()) ? 0 : date.getTime();
}

export const load: PageServerLoad = async ({ fetch }) => {
	let pressItems: PressItem[] = [];

	try {
		// Try to load press items from CSV file
		const response = await fetch('/press.csv');
		if (response.ok) {
			const csvText = await response.text();
			pressItems = parsePressCSV(csvText);
			// Sort by date descending (most recent first); items without date go to the end
			pressItems.sort((a, b) => parsePressDate(b.date) - parsePressDate(a.date));
		}
	} catch (error) {
		console.error('Error loading press CSV:', error);
	}

	return {
		pressItems
	};
};

