import type { PageServerLoad } from './$types';

interface Event {
	title: string;
	dates: string[];
	startTime?: string;
	endTime?: string;
	location?: string;
	description?: string;
	link?: string;
	action?: string;
}

interface Announcement {
	title: string;
	description: string;
	image?: string;
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

function parseCSV(csvText: string): Event[] {
	const lines = csvText.trim().split(/\r?\n/);
	if (lines.length < 2) return [];

	// Parse header
	const headers = parseCSVLine(lines[0]).map((h) => h.trim().toLowerCase().replace(/^"|"$/g, ''));

	// Parse data rows
	const events: Event[] = [];
	for (let i = 1; i < lines.length; i++) {
		const line = lines[i].trim();
		if (!line) continue;

		const values = parseCSVLine(line).map((v) => v.replace(/^"|"$/g, ''));
		if (values.length === 0 || !values[0]) continue;

		const event: Event = {
			title: '',
			dates: []
		};

		headers.forEach((header, index) => {
			const value = values[index] || '';
			switch (header) {
				case 'title':
					event.title = value;
					break;
				case 'date':
				case 'dates':
					// Support both single date and multiple dates (comma or semicolon separated)
					const dateValues = value.split(/[,;]/).map((d) => d.trim()).filter((d) => d);
					event.dates = dateValues.length > 0 ? dateValues : [];
					break;
				case 'starttime':
				case 'start_time':
				case 'start time':
					event.startTime = value;
					break;
				case 'endtime':
				case 'end_time':
				case 'end time':
					event.endTime = value;
					break;
				case 'time':
					// Legacy support: if only 'time' is provided, treat as startTime
					if (!event.startTime) {
						event.startTime = value;
					}
					break;
				case 'location':
					event.location = value;
					break;
				case 'description':
					event.description = value;
					break;
				case 'link':
					event.link = value;
					break;
				case 'action':
					if (value) {
						event.action = value.toLowerCase().trim();
					}
					break;
			}
		});

		if (event.title && event.dates.length > 0) {
			events.push(event);
		}
	}

	return events;
}

function parseAnnouncementsCSV(csvText: string): Announcement[] {
	const lines = csvText.trim().split(/\r?\n/);
	if (lines.length < 2) return [];

	// Parse header
	const headers = parseCSVLine(lines[0]).map((h) => h.trim().toLowerCase().replace(/^"|"$/g, ''));

	// Parse data rows
	const announcements: Announcement[] = [];
	for (let i = 1; i < lines.length; i++) {
		const line = lines[i].trim();
		if (!line) continue;

		const values = parseCSVLine(line).map((v) => v.replace(/^"|"$/g, ''));
		if (values.length === 0 || !values[0]) continue;

		const announcement: Announcement = {
			title: '',
			description: ''
		};

		headers.forEach((header, index) => {
			const value = values[index] || '';
			switch (header) {
				case 'title':
					announcement.title = value;
					break;
				case 'description':
					announcement.description = value;
					break;
				case 'image':
					if (value) {
						announcement.image = value;
					}
					break;
				case 'link':
					if (value) {
						announcement.link = value;
					}
					break;
			}
		});

		if (announcement.title && announcement.description) {
			announcements.push(announcement);
		}
	}

	return announcements;
}

export const load: PageServerLoad = async ({ fetch }) => {
	let events: Event[] = [];
	let announcements: Announcement[] = [];

	try {
		// Try to load events from CSV file
		const response = await fetch('/events.csv');
		if (response.ok) {
			const csvText = await response.text();
			events = parseCSV(csvText);
		}
	} catch (error) {
		console.error('Error loading events CSV:', error);
	}

	try {
		// Try to load announcements from CSV file
		const response = await fetch('/announcements.csv');
		if (response.ok) {
			const csvText = await response.text();
			announcements = parseAnnouncementsCSV(csvText);
		}
	} catch (error) {
		console.error('Error loading announcements CSV:', error);
	}

	return {
		events,
		announcements
	};
};

