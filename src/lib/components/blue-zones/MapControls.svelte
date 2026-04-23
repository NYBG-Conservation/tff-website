<script lang="ts">
	import type { Map as MapLibreMap, MapMouseEvent } from 'maplibre-gl';
	import {
		MAPSTORE_CONTEXT_KEY,
		type MapStore,
		blueZonesSearchMount,
		blueZonesSearchResult,
		blueZonesSelectedPolygon,
		blueZonesCriteriaFilter
	} from '$lib/stores';
	import { getContext, onDestroy } from 'svelte';
	import { slide } from 'svelte/transition';
	import { quintOut } from 'svelte/easing';

	const accordionSlide = { duration: 280, easing: quintOut };

	type BzProperties = {
		unique_id?: number;
		ATOMICID?: string;
		gridcode?: number;
		BZ_past?: number;
		BZ_present?: number;
		BZ_future?: number;
		BZ_past_correct?: number;
		BZ_present_correct?: number;
		BZ_future_correct?: number;
		BZ_correct?: number;
		[key: string]: unknown;
	};

	type ZoneSummary = {
		name: string;
		id: string;
	areaSqFt?: number;
		properties: BzProperties;
	};

	type AddressResult = {
		address: string;
		insideBlueZone: boolean;
		zone?: ZoneSummary;
		nearestZone?: ZoneSummary;
		distanceMiles?: number;
		stats: { past: boolean; present: boolean; future: boolean };
	blockInfo?: AtomicBlockInfo;
	blockOwnership?: OwnershipFlags;
	zoneOwnership?: OwnershipFlags;
	hurricaneEvacuationZonesDisplay?: string;
	};

	type ViewMode = 'intro' | 'searchResult' | 'mapClickResult';

type AtomicBlockInfo = {
	atomicId: string;
	waterFlag?: string;
	hurricaneEvacuationZone?: string;
	assemblyDistrict?: string;
	borough?: string;
	schoolDistrict?: string;
	electionDistrict?: string;
};

type OwnershipFlags = {
	federal: boolean;
	state: boolean;
	city: boolean;
	private: boolean;
};

	let viewMode: ViewMode = $state('intro');
	let errorMessage = $state('');
	let result: AddressResult | null = $state(null);
	let searchMountElement: HTMLDivElement | null = $state(null);
	let criteriaExpanded = $state({ past: false, present: false, future: false });
	let copiedLink = $state(false);

	let mapStore: MapStore = getContext(MAPSTORE_CONTEXT_KEY);
	let geojsonFeatures: GeoJSON.Feature[] | null = null;
	let atomicById: Map<string, AtomicBlockInfo> | null = null;
	let tenureOwnershipByAtomicId: Map<string, OwnershipFlags> | null = null;
	/** Joined from BlueZone.json: authoritative area_ft2 by atomic polygon unique_id */
	let areaFt2ByUniqueId: Map<number, number> | null = null;
	let unbindMapHandlers: (() => void) | null = null;
	let currentMap: MapLibreMap | null = null;

	async function loadBlueZones() {
		if (geojsonFeatures) return geojsonFeatures;
		const response = await fetch('/data/blue-zones/blue_zone_4326.json');
		if (!response.ok) throw new Error('Could not load blue zone polygons');
		const data = await response.json();
		geojsonFeatures = data.features as GeoJSON.Feature[];
		return geojsonFeatures;
	}

	async function loadBlueZoneAreaFt2() {
		if (areaFt2ByUniqueId) return areaFt2ByUniqueId;
		const response = await fetch('/data/blue-zones/BlueZone.json');
		if (!response.ok) throw new Error('Could not load Blue Zone area data');
		const data = await response.json();
		const index = new Map<number, number>();
		for (const feature of data.features as GeoJSON.Feature[]) {
			const props = (feature.properties ?? {}) as Record<string, unknown>;
			const uid = props.unique_id;
			const aft = props.area_ft2;
			if (typeof uid !== 'number') continue;
			if (typeof aft === 'number' && Number.isFinite(aft)) {
				index.set(uid, aft);
			} else if (typeof aft === 'string' && aft !== '') {
				const n = Number(aft);
				if (Number.isFinite(n)) index.set(uid, n);
			}
		}
		areaFt2ByUniqueId = index;
		return index;
	}

async function loadAtomicPolygons() {
	if (atomicById) return atomicById;
	const response = await fetch('/data/blue-zones/atomic_polygons.json');
	if (!response.ok) throw new Error('Could not load atomic polygons data');
	const data = await response.json();
	const index = new Map<string, AtomicBlockInfo>();
	for (const feature of data.features as GeoJSON.Feature[]) {
		const props = (feature.properties ?? {}) as Record<string, unknown>;
		const atomicId = String(props.ATOMICID ?? '');
		if (!atomicId) continue;
		index.set(atomicId, {
			atomicId,
			waterFlag: String(props.WATER_FLAG ?? ''),
			hurricaneEvacuationZone: props.HURRICANE_EVACUATION_ZONE
				? String(props.HURRICANE_EVACUATION_ZONE)
				: undefined,
			assemblyDistrict: props.ASSEMDIST ? String(props.ASSEMDIST) : undefined,
			borough: props.BOROUGH ? String(props.BOROUGH) : undefined,
			schoolDistrict: props.SCHOOLDIST ? String(props.SCHOOLDIST) : undefined,
			electionDistrict: props.ELECTDIST ? String(props.ELECTDIST) : undefined
		});
	}
	atomicById = index;
	return atomicById;
}

async function loadTenureOwnership() {
	if (tenureOwnershipByAtomicId) return tenureOwnershipByAtomicId;
	const response = await fetch('/data/blue-zones/phase2/BZ_tenure.csv');
	if (!response.ok) throw new Error('Could not load tenure ownership data');
	const csvText = await response.text();
	const lines = csvText.split(/\r?\n/);
	if (lines.length === 0) {
		tenureOwnershipByAtomicId = new Map();
		return tenureOwnershipByAtomicId;
	}
	const headers = lines[0].split(',');
	const atomicIdx = headers.indexOf('ATOMICID');
	const federalIdx = headers.indexOf('SUM_Federa');
	const stateIdx = headers.indexOf('SUM_State');
	const cityIdx = headers.indexOf('SUM_City');
	const privateIdx = headers.indexOf('Private');
	if (atomicIdx < 0 || federalIdx < 0 || stateIdx < 0 || cityIdx < 0 || privateIdx < 0) {
		throw new Error('Tenure ownership data is missing required columns');
	}
	const index = new Map<string, OwnershipFlags>();
	for (let i = 1; i < lines.length; i++) {
		const line = lines[i];
		if (!line) continue;
		const cols = line.split(',');
		const atomicId = (cols[atomicIdx] ?? '').trim();
		if (!atomicId) continue;
		const existing = index.get(atomicId) ?? {
			federal: false,
			state: false,
			city: false,
			private: false
		};
		existing.federal = existing.federal || Number(cols[federalIdx] ?? 0) > 0;
		existing.state = existing.state || Number(cols[stateIdx] ?? 0) > 0;
		existing.city = existing.city || Number(cols[cityIdx] ?? 0) > 0;
		existing.private = existing.private || Number(cols[privateIdx] ?? 0) > 0;
		index.set(atomicId, existing);
	}
	tenureOwnershipByAtomicId = index;
	return tenureOwnershipByAtomicId;
}

	function pointInRing(point: [number, number], ring: number[][]): boolean {
		let inside = false;
		for (let i = 0, j = ring.length - 1; i < ring.length; j = i++) {
			const [xi, yi] = ring[i];
			const [xj, yj] = ring[j];
			const intersects =
				yi > point[1] !== yj > point[1] &&
				point[0] < ((xj - xi) * (point[1] - yi)) / (yj - yi + 1e-12) + xi;
			if (intersects) inside = !inside;
		}
		return inside;
	}

	function pointInPolygonGeometry(point: [number, number], geometry: GeoJSON.Geometry): boolean {
		if (geometry.type === 'Polygon') {
			const [outer] = geometry.coordinates as number[][][];
			return pointInRing(point, outer);
		}
		if (geometry.type === 'MultiPolygon') {
			const polygons = geometry.coordinates as number[][][][];
			return polygons.some((poly) => pointInRing(point, poly[0]));
		}
		return false;
	}

	function getFeatureCentroid(feature: GeoJSON.Feature): [number, number] {
		const geometry = feature.geometry;
		if (!geometry) return [0, 0];
		const points: [number, number][] = [];

		if (geometry.type === 'Polygon') {
			for (const pt of geometry.coordinates[0] as number[][]) points.push([pt[0], pt[1]]);
		} else if (geometry.type === 'MultiPolygon') {
			for (const poly of geometry.coordinates as number[][][][]) {
				for (const pt of poly[0]) points.push([pt[0], pt[1]]);
			}
		}

		if (points.length === 0) return [0, 0];
		const sum = points.reduce(
			(acc, cur) => [acc[0] + cur[0], acc[1] + cur[1]] as [number, number],
			[0, 0]
		);
		return [sum[0] / points.length, sum[1] / points.length];
	}

	function haversineMiles(from: [number, number], to: [number, number]): number {
		const toRad = (d: number) => (d * Math.PI) / 180;
		const earthMiles = 3958.8;
		const dLat = toRad(to[1] - from[1]);
		const dLon = toRad(to[0] - from[0]);
		const lat1 = toRad(from[1]);
		const lat2 = toRad(to[1]);
		const a =
			Math.sin(dLat / 2) ** 2 +
			Math.cos(lat1) * Math.cos(lat2) * Math.sin(dLon / 2) ** 2;
		return 2 * earthMiles * Math.asin(Math.sqrt(a));
	}

	function getAreaSqFtForProperties(props: BzProperties): number | undefined {
		const uid = props.unique_id;
		if (typeof uid === 'number' && areaFt2ByUniqueId?.has(uid)) {
			return areaFt2ByUniqueId.get(uid);
		}
		const rawArea = props.area;
		return typeof rawArea === 'number' ? rawArea : undefined;
	}

	function toZoneSummary(properties: BzProperties): ZoneSummary {
		const id = String(properties.gridcode ?? 'N/A');
		const areaSqFt = getAreaSqFtForProperties(properties);
		return {
			id,
			name: `Blue Zone ${properties.gridcode ?? 'Unknown'}`,
			areaSqFt,
			properties
		};
	}

	function sumAreaSqFtForBlueZoneGridcode(gridcode: number): number {
		const features = geojsonFeatures ?? [];
		let zoneArea = 0;
		for (const feature of features) {
			const fp = (feature.properties ?? {}) as BzProperties;
			if (Number(fp.gridcode) !== gridcode || !isBlueZone(fp)) continue;
			const a = getAreaSqFtForProperties(fp);
			if (typeof a === 'number') zoneArea += a;
		}
		return zoneArea;
	}

	function isBlueZone(properties: BzProperties): boolean {
		return (
			properties.BZ_past_correct === 1 &&
			properties.BZ_present_correct === 1 &&
			properties.BZ_future_correct === 1
		);
	}

function waterFlagDisplay(flag?: string): { label: string; description: string } | null {
	switch (flag) {
		case '1':
			return {
				label: 'Water',
				description: 'Atomic polygon is under water that is part of the shoreline.'
			};
		case '2':
			return {
				label: 'Non-Water',
				description: 'Atomic polygon is on land.'
			};
		case '3':
			return {
				label: 'Internal Water',
				description:
					'Atomic polygon is under water that is not part of the shoreline (lake, pond, reservoir, etc.).'
			};
		case '4':
			return {
				label: 'Pier',
				description: 'Atomic polygon is on a pier or structure over water.'
			};
		default:
			return null;
	}
}

function toHurricaneEvacuationZonesDisplay(rawValues: Array<string | undefined>): string {
	const values = rawValues
		.map((v) => (typeof v === 'string' ? v.trim() : ''))
		.filter((v) => v.length > 0);
	if (values.length === 0) return 'None';
	const nonX = [...new Set(values.filter((v) => v !== 'X'))].sort();
	if (nonX.length === 0) return 'None';
	return JSON.stringify(nonX);
}

function hurricaneEvacuationZonesForGridcode(gridcode: number): string {
	const features = geojsonFeatures ?? [];
	const vals: string[] = [];
	for (const feature of features) {
		const props = (feature.properties ?? {}) as BzProperties;
		if (props.gridcode !== gridcode || !isBlueZone(props)) continue;
		const atomicId = typeof props.ATOMICID === 'string' ? props.ATOMICID : undefined;
		if (!atomicId) continue;
		const block = atomicById?.get(atomicId);
		if (block?.hurricaneEvacuationZone != null) {
			vals.push(block.hurricaneEvacuationZone);
		}
	}
	return toHurricaneEvacuationZonesDisplay(vals);
}

function ownershipForBlueZoneGridcode(gridcode: number): OwnershipFlags | undefined {
	const features = geojsonFeatures ?? [];
	const combined: OwnershipFlags = { federal: false, state: false, city: false, private: false };
	let sawAnyAtomic = false;
	for (const feature of features) {
		const props = (feature.properties ?? {}) as BzProperties;
		if (props.gridcode !== gridcode || !isBlueZone(props)) continue;
		const atomicId = typeof props.ATOMICID === 'string' ? props.ATOMICID : undefined;
		if (!atomicId) continue;
		const flags = tenureOwnershipByAtomicId?.get(atomicId);
		if (!flags) continue;
		sawAnyAtomic = true;
		combined.federal = combined.federal || flags.federal;
		combined.state = combined.state || flags.state;
		combined.city = combined.city || flags.city;
		combined.private = combined.private || flags.private;
	}
	return sawAnyAtomic ? combined : undefined;
}

	function formatArea(areaSqFt: number): string {
		const rounded = Math.round(areaSqFt);
		const acres = rounded / 43560;
		return `${rounded.toLocaleString()} sq ft (${acres.toFixed(2)} acres)`;
	}

	function addressResultFromBlueZoneFeature(
		containingBlueZone: GeoJSON.Feature,
		address: string
	): AddressResult {
		const props = (containingBlueZone.properties ?? {}) as BzProperties;
		const containingGridcode = props.gridcode;
		const containingAtomicId =
			typeof props.ATOMICID === 'string' ? props.ATOMICID : undefined;
		const blockInfo = containingAtomicId ? atomicById?.get(containingAtomicId) : undefined;
		const blockOwnership = containingAtomicId
			? tenureOwnershipByAtomicId?.get(containingAtomicId)
			: undefined;
		const blockHurricaneEvacuationZones = toHurricaneEvacuationZonesDisplay([
			blockInfo?.hurricaneEvacuationZone
		]);
		const localStats = {
			past: props.BZ_past_correct === 1,
			present: props.BZ_present_correct === 1,
			future: props.BZ_future_correct === 1
		};

		let zoneSummary = toZoneSummary(props);
		let hurricaneEvacuationZonesDisplay = blockHurricaneEvacuationZones;
		let zoneOwnership = blockOwnership;
		if (typeof containingGridcode === 'number') {
			const zoneArea = sumAreaSqFtForBlueZoneGridcode(containingGridcode);
			zoneSummary = {
				...zoneSummary,
				id: String(containingGridcode),
				name: `Blue Zone ${containingGridcode}`,
				areaSqFt: zoneArea > 0 ? zoneArea : zoneSummary.areaSqFt
			};
			hurricaneEvacuationZonesDisplay = hurricaneEvacuationZonesForGridcode(containingGridcode);
			zoneOwnership = ownershipForBlueZoneGridcode(containingGridcode);
		}
		return {
			address,
			insideBlueZone: true,
			zone: zoneSummary,
			stats: localStats,
			blockInfo,
			blockOwnership,
			zoneOwnership,
			hurricaneEvacuationZonesDisplay
		};
	}

	async function analyzePoint(point: [number, number], address: string): Promise<AddressResult> {
		await loadBlueZones();
		await loadAtomicPolygons();
		await loadTenureOwnership();
		await loadBlueZoneAreaFt2();
		const features = geojsonFeatures ?? [];
		let containing: GeoJSON.Feature | null = null;
		let containingBlueZone: GeoJSON.Feature | null = null;
		let nearest: GeoJSON.Feature | null = null;
		let nearestDistance = Number.POSITIVE_INFINITY;

		for (const feature of features) {
			if (!feature.geometry) continue;
			const props = (feature.properties ?? {}) as BzProperties;
			const qualifies = isBlueZone(props);
			const containsPoint = pointInPolygonGeometry(point, feature.geometry);

			if (!containing && containsPoint) containing = feature;
			if (!containingBlueZone && containsPoint && qualifies) containingBlueZone = feature;

			if (!qualifies) continue;
			const centroid = getFeatureCentroid(feature);
			const d = haversineMiles(point, centroid);
			if (d < nearestDistance) {
				nearestDistance = d;
				nearest = feature;
			}
		}

	const containingProps = (containing?.properties ?? {}) as BzProperties;
	const containingAtomicId =
		typeof containingProps.ATOMICID === 'string' ? containingProps.ATOMICID : undefined;
	const blockInfo = containingAtomicId ? atomicById?.get(containingAtomicId) : undefined;
	const blockOwnership = containingAtomicId
		? tenureOwnershipByAtomicId?.get(containingAtomicId)
		: undefined;
	const blockHurricaneEvacuationZones = toHurricaneEvacuationZonesDisplay([
		blockInfo?.hurricaneEvacuationZone
	]);
		/** Same feature as blue-zone / not-in-zone messaging: BZ polygon when inside a BZ, else atomic polygon under click */
		const statsProps = (
			containingBlueZone ?? containing
		)?.properties as BzProperties | undefined;
		const localStats = {
			past: statsProps?.BZ_past_correct === 1,
			present: statsProps?.BZ_present_correct === 1,
			future: statsProps?.BZ_future_correct === 1
		};

		if (containingBlueZone) {
			return addressResultFromBlueZoneFeature(containingBlueZone, address);
		}

		const nearestProps = (nearest?.properties ?? {}) as BzProperties;
		let nearestZoneSummary = toZoneSummary(nearestProps);
		if (typeof nearestProps.gridcode === 'number') {
			const zoneArea = sumAreaSqFtForBlueZoneGridcode(nearestProps.gridcode);
			nearestZoneSummary = {
				...nearestZoneSummary,
				id: String(nearestProps.gridcode),
				name: `Blue Zone ${nearestProps.gridcode}`,
				areaSqFt: zoneArea > 0 ? zoneArea : nearestZoneSummary.areaSqFt
			};
		}
		return {
			address,
			insideBlueZone: false,
			nearestZone: nearestZoneSummary,
			distanceMiles: nearestDistance,
			stats: localStats,
			blockInfo,
			blockOwnership,
			zoneOwnership: undefined,
			hurricaneEvacuationZonesDisplay: blockHurricaneEvacuationZones
		};
	}

	function renderDistance(distanceMiles: number): string {
		if (distanceMiles < 0.2) return `${Math.round(distanceMiles * 5280)} ft`;
		return `${distanceMiles.toFixed(2)} miles`;
	}

	function countFloodRiskCriteriaMet(stats: AddressResult['stats']): number {
		return [stats.past, stats.present, stats.future].filter(Boolean).length;
	}

	/**
	 * Subject–verb agreement: only exactly one criterion met uses "is"; 0, 2, or 3 use "are".
	 * (E.g. "0 … are", "1 … is", "2 … are".)
	 */
	function floodingCriteriaMetFragment(stats: AddressResult['stats']): string {
		const n = countFloodRiskCriteriaMet(stats);
		if (n === 1) {
			return '1 of the 3 flooding criteria is met here';
		}
		return `${n} of the 3 flooding criteria are met here`;
	}

	/** A centroid that lies inside its own atomic polygon (not the mean of many, which can fall outside). */
	function getInteriorPointForBlueZoneGridcode(gridcode: number): [number, number] | null {
		const features = geojsonFeatures ?? [];
		for (const feature of features) {
			const props = (feature.properties ?? {}) as BzProperties;
			if (!feature.geometry || props.gridcode !== gridcode || !isBlueZone(props)) continue;
			const c = getFeatureCentroid(feature);
			if (pointInPolygonGeometry(c, feature.geometry)) return c;
		}
		return null;
	}

	function firstBlueZoneFeatureForGridcode(gridcode: number): GeoJSON.Feature | null {
		const features = geojsonFeatures ?? [];
		for (const feature of features) {
			const props = (feature.properties ?? {}) as BzProperties;
			if (!feature.geometry || props.gridcode !== gridcode || !isBlueZone(props)) continue;
			return feature;
		}
		return null;
	}

	/** Mean of atomic centroids — OK for framing the map; can lie outside all polygons. */
	function getZoneCenterByGridcode(gridcode: number): [number, number] | null {
		const features = geojsonFeatures ?? [];
		const centroids: [number, number][] = [];
		for (const feature of features) {
			const props = (feature.properties ?? {}) as BzProperties;
			if (!feature.geometry || props.gridcode !== gridcode || !isBlueZone(props)) continue;
			centroids.push(getFeatureCentroid(feature));
		}
		if (centroids.length === 0) return null;
		const sum = centroids.reduce(
			(acc, cur) => [acc[0] + cur[0], acc[1] + cur[1]] as [number, number],
			[0, 0]
		);
		return [sum[0] / centroids.length, sum[1] / centroids.length];
	}

	function resetToIntro() {
		viewMode = 'intro';
		result = null;
		errorMessage = '';
		blueZonesSelectedPolygon.set(null);
		copiedLink = false;
	}

	/**
	 * MapLibre `hash: true` format (`zoom/lat/lng` [+ bearing/pitch]).
	 * Map.svelte only auto-selects the polygon at center when zoom is **> 14** (see idle handler).
	 */
	function buildShareHashForMap(map: MapLibreMap, minZoom: number): string {
		const center = map.getCenter();
		let zoom = Math.max(map.getZoom(), minZoom);
		zoom = Math.round(zoom * 100) / 100;
		const precision = Math.ceil((zoom * Math.LN2 + Math.log(512 / 360 / 0.5)) / Math.LN10);
		const m = Math.pow(10, precision);
		const lng = Math.round(center.lng * m) / m;
		const lat = Math.round(center.lat * m) / m;
		const bearing = map.getBearing();
		const pitch = map.getPitch();
		let body = `${zoom}/${lat}/${lng}`;
		if (bearing || pitch) body += `/${Math.round(bearing * 10) / 10}`;
		if (pitch) body += `/${Math.round(pitch)}`;
		return body;
	}

	const SHARE_LINK_MIN_ZOOM = 12.5;

	async function copyShareLink() {
		if (typeof window === 'undefined') return;
		try {
			const url = new URL(window.location.href);
			url.searchParams.delete('bz_lat');
			url.searchParams.delete('bz_lng');
			url.searchParams.delete('bz_mode');
			url.searchParams.delete('bz_label');
			window.history.replaceState({}, '', url.toString());

			let textToCopy = url.toString();
			if (currentMap) {
				const shareUrl = new URL(url.toString());
				shareUrl.searchParams.set('bz_share', '1');
				shareUrl.hash = `#${buildShareHashForMap(currentMap, SHARE_LINK_MIN_ZOOM)}`;
				textToCopy = shareUrl.toString();
			}

			await navigator.clipboard.writeText(textToCopy);
			copiedLink = true;
			setTimeout(() => {
				copiedLink = false;
			}, 1500);
		} catch {
			copiedLink = false;
		}
	}

	async function goToNearestBlueZone() {
		if (!result || result.insideBlueZone || !result.nearestZone?.id) return;
		const zoneId = Number(result.nearestZone.id);
		if (Number.isNaN(zoneId)) return;
		await loadBlueZones();
		await loadAtomicPolygons();
		await loadBlueZoneAreaFt2();

		const interior = getInteriorPointForBlueZoneGridcode(zoneId);
		const fallbackFeature = firstBlueZoneFeatureForGridcode(zoneId);
		const center =
			interior ??
			(fallbackFeature ? getFeatureCentroid(fallbackFeature) : null) ??
			getZoneCenterByGridcode(zoneId);
		if (!center) return;
		const map = currentMap;
		if (!map) return;

		await new Promise<void>((resolve) => {
			map.once('moveend', () => resolve());
			map.flyTo({
				center,
				zoom: Math.max(map.getZoom(), 14.5),
				speed: 1,
				curve: 1.35,
				essential: true
			});
		});

		// Select the zone on the map (outline) and align the sidebar with that destination.
		blueZonesSelectedPolygon.set({ gridcode: zoneId });
		try {
			// `analyzePoint` needs a point inside a BZ polygon; the mean centroid often is not.
			const next =
				interior != null
					? await analyzePoint(interior, 'The area you have selected')
					: fallbackFeature != null
						? addressResultFromBlueZoneFeature(fallbackFeature, 'The area you have selected')
						: await analyzePoint(center, 'The area you have selected');
			result = next;
			viewMode = 'mapClickResult';
			errorMessage = '';
		} catch (error) {
			errorMessage = error instanceof Error ? error.message : 'Could not load zone details';
		}
	}

	function toggleCriteriaSection(key: 'past' | 'present' | 'future') {
		criteriaExpanded = { ...criteriaExpanded, [key]: !criteriaExpanded[key] };
	}

	async function handleMapFeatureClick(clickedPoint: [number, number]) {
		result = await analyzePoint(clickedPoint, 'The area you have selected');
		viewMode = 'mapClickResult';
		/* Set store after viewMode so hash/deep-link sync (below) does not re-run analyzePoint */
		if (result?.insideBlueZone && result.zone?.id) {
			const zoneId = Number(result.zone.id);
			if (!Number.isNaN(zoneId)) blueZonesSelectedPolygon.set({ gridcode: zoneId });
		}
	}

	const unsubscribe = mapStore.subscribe((map) => {
		unbindMapHandlers?.();
		unbindMapHandlers = null;
		currentMap = map;
		if (!map) return;

		const clickHandler = (event: MapMouseEvent) => {
			const hits = map.queryRenderedFeatures([event.point.x, event.point.y], {
				layers: ['blue-zones-hit-area']
			});
			if (hits.length > 0) {
				const { lng, lat } = event.lngLat;
				void handleMapFeatureClick([lng, lat]);
			}
		};

		const moveHandler = (event: { point: { x: number; y: number } }) => {
			const hovered = map.queryRenderedFeatures([event.point.x, event.point.y], {
				layers: ['blue-zones-hit-area']
			});
			map.getCanvas().style.cursor = hovered.length ? 'pointer' : 'default';
		};

		map.on('click', clickHandler);
		map.on('mousemove', moveHandler);
		unbindMapHandlers = () => {
			map.off('click', clickHandler);
			map.off('mousemove', moveHandler);
			map.getCanvas().style.cursor = 'default';
		};
	});

	const unSubSearchResult = blueZonesSearchResult.subscribe(async (selected) => {
		if (!selected) return;
		try {
			result = await analyzePoint(selected.coordinates, selected.label);
			viewMode = 'searchResult';
			errorMessage = '';
			if (result?.insideBlueZone && result.zone?.id) {
				const zoneId = Number(result.zone.id);
				if (!Number.isNaN(zoneId)) blueZonesSelectedPolygon.set({ gridcode: zoneId });
			} else {
				blueZonesSelectedPolygon.set(null);
			}
		} catch (error) {
			errorMessage = error instanceof Error ? error.message : 'Search analysis failed';
		}
	});

	/** When Map.svelte selects from hash / idle (no click), populate the panel from map center */
	let selectionPanelSyncGen = 0;
	const unSubSelectedPolygon = blueZonesSelectedPolygon.subscribe((selected) => {
		void (async () => {
			const gen = ++selectionPanelSyncGen;
			if (!selected) return;
			if (viewMode !== 'intro') return;
			const map = currentMap;
			if (!map) return;
			const c = map.getCenter();
			try {
				const next = await analyzePoint([c.lng, c.lat], 'The area you have selected');
				if (gen !== selectionPanelSyncGen) return;
				if (viewMode !== 'intro') return;
				result = next;
				viewMode = 'mapClickResult';
				errorMessage = '';
			} catch (error) {
				if (gen !== selectionPanelSyncGen) return;
				errorMessage = error instanceof Error ? error.message : 'Could not load location details';
			}
		})();
	});

	$effect(() => {
		blueZonesCriteriaFilter.set({ past: true, present: true, future: true });
	});

	$effect(() => {
		blueZonesSearchMount.set(searchMountElement);
		return () => {
			blueZonesSearchMount.set(null);
		};
	});

	onDestroy(() => {
		unbindMapHandlers?.();
		unSubSearchResult();
		unSubSelectedPolygon();
		unsubscribe();
	});
</script>

{#if result}
<button class="back" onclick={resetToIntro}>
	<span class="arrow" aria-hidden="true">←</span>
	Back
</button><br/><br/>
{/if}

<section class="controls">
{#if viewMode === 'intro'}<br/>
<div class="intro">
	<h1 class="intro-title">The Blue Zones Map Explorer</h1>
	<p>Search an address below or click anywhere on the map to see if it's in a <strong>Blue Zone</strong>, or a watershed-derived area susceptible to flooding.</p>
</div>
{/if}


	<div class="search-wrap">
		<div class="search-control-host" bind:this={searchMountElement}></div>
	</div>

	<!-- <h3>Map Key</h3>

	<p style="margin: 0px;">The scale shows how many Blue Zone criteria each block meets: 1, 2, or all 3.</p>
	<div class="criteria-scale">
		<div class="scale-bar" aria-hidden="true">
			<div class="step one"></div>
			<div class="step two"></div>
			<div class="step three"></div>
		</div>
		<div class="scale-labels">
			<span>1/3</span>
			<span>2/3</span>
			<span>3/3</span>
		</div>
	</div> -->
	{#if errorMessage}
		<p class="error">{errorMessage}</p>
	{/if}


	{#if result}
		<div class="result">
			<div class="headline-row">
				{#if result.insideBlueZone && result.zone}
					<p class="headline">
						{#if viewMode === 'mapClickResult'}
							You have selected <strong>Blue Zone #{result.zone.id}</strong>, a watershed-derived area with high past, present, and future flooding risk.
						{:else}
							{result.address} is located in <strong>Blue Zone #{result.zone.id}</strong>, a watershed-derived area with high past, present, and future flooding risk.
						{/if}
					</p>
				{:else if result.nearestZone && result.distanceMiles !== undefined}
					<p class="headline">
						{result.address} is <strong>not in a Blue Zone</strong>: {floodingCriteriaMetFragment(result.stats)}. The closest Blue Zone, #{result.nearestZone.id}, is {renderDistance(result.distanceMiles)} away.
					</p>
				{/if}
				<button
					type="button"
					class="copy-link-btn"
					onclick={copyShareLink}
					aria-label="Copy link to this location"
					title="Copy link to this location"
				>
					<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
						<path d="M10.73 6.01973L13.2577 3.49199C14.2441 2.49322 15.5635 2 16.8705 2C18.1899 2 19.4969 2.49322 20.4957 3.49199C21.4945 4.49075 22 5.81011 22 7.11714C22 8.4365 21.4945 9.74353 20.4957 10.7423L16.3157 14.9223C15.3169 15.9211 14.0099 16.4143 12.6905 16.4143C11.3835 16.4143 10.0641 15.9211 9.06535 14.9223C8.78175 14.6387 8.53514 14.3181 8.33785 13.9852L10.1011 12.2219C10.2244 12.6042 10.4464 12.9494 10.7423 13.2454C11.2725 13.7879 11.9877 14.0592 12.6905 14.0592C13.4057 14.0592 14.1085 13.7879 14.6387 13.2454L18.8311 9.06535C19.3613 8.53514 19.6326 7.83231 19.6326 7.11714C19.6326 6.4143 19.3613 5.69914 18.8311 5.16893C18.2885 4.63872 17.5857 4.36745 16.8705 4.36745C16.1677 4.36745 15.4649 4.63872 14.9223 5.16893L13.6646 6.42663C12.9125 6.14303 12.111 5.99507 11.2972 5.99507C11.1122 5.99507 10.9149 6.0074 10.73 6.01973V6.01973ZM3.49199 13.2577L7.67201 9.06535C8.67078 8.07892 9.99014 7.57337 11.2972 7.57337C12.6165 7.57337 13.9236 8.07892 14.9223 9.06535C15.2059 9.36128 15.4525 9.66954 15.6621 10.0025L13.8989 11.7657C13.7633 11.3958 13.5536 11.0382 13.2454 10.7423C12.7152 10.2121 12.0123 9.94081 11.2972 9.94081C10.5943 9.94081 9.87916 10.2121 9.34895 10.7423L5.16893 14.9223C4.63872 15.4649 4.36745 16.1677 4.36745 16.8705C4.36745 17.5857 4.63872 18.2885 5.16893 18.8311C5.69914 19.3613 6.4143 19.6326 7.11714 19.6326C7.83231 19.6326 8.53514 19.3613 9.06535 18.8311L10.3231 17.5734C11.0752 17.8446 11.8767 17.9926 12.6905 17.9926C12.8878 17.9926 13.0727 17.9926 13.27 17.9679L10.7423 20.4957C9.74353 21.4945 8.4365 22 7.11714 22C5.81011 22 4.49075 21.4945 3.49199 20.4957C2.49322 19.4969 2 18.1899 2 16.8705C2 15.5635 2.49322 14.2441 3.49199 13.2577V13.2577Z"></path>
					</svg>
				</button>
			</div>
			{#if copiedLink}
				<p class="copied-note">Link copied</p>
			{/if}
			{#if !result.insideBlueZone && result.nearestZone}
				<button type="button" class="back" onclick={goToNearestBlueZone}>
					<span>Take me to the nearest Blue Zone</span>
					<svg
						class="arrow"
						xmlns="http://www.w3.org/2000/svg"
						width="24"
						height="24"
						viewBox="0 0 24 24"
						fill="none"
						aria-hidden="true"
					>
						<line x1="7" y1="17" x2="17" y2="7" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
						<polyline
							points="7 7 17 7 17 17"
							stroke="currentColor"
							stroke-width="2"
							stroke-linecap="round"
							stroke-linejoin="round"
						/>
					</svg>
				</button>
			{/if}


			{#if result.insideBlueZone && result.zone}
				{#if result.zone.areaSqFt !== undefined}
					<p class="meta">Blue Zone Area: {formatArea(result.zone.areaSqFt)}</p>
				{/if}
			{/if}

			<h3>Blue Zone Criteria</h3>
			<div class="stats-bar">
				<div class:active={result.stats.past}>
					<span>Past</span>
					<strong>{result.stats.past ? 'Yes' : 'No'}</strong>
				</div>
				<div class:active={result.stats.present}>
					<span>Present</span>
					<strong>{result.stats.present ? 'Yes' : 'No'}</strong>
				</div>
				<div class:active={result.stats.future}>
					<span>Future</span>
					<strong>{result.stats.future ? 'Yes' : 'No'}</strong>
				</div>
			</div>

			{#if result.blockInfo}
				<div class="block-info">
					<p class="block-title">Block info</p>
					<p class="meta"><strong>ATOMIC ID:</strong> {result.blockInfo.atomicId}</p>
					{#if waterFlagDisplay(result.blockInfo.waterFlag)}
						{@const waterInfo = waterFlagDisplay(result.blockInfo.waterFlag)}
						<p class="meta">
							<strong>Water:</strong> {waterInfo?.label}
						</p>
						<p class="meta small">{waterInfo?.description}</p>
					{/if}
					<p class="meta">
						<strong>Hurricane Evacuation Zone:</strong> {result.hurricaneEvacuationZonesDisplay ?? 'None'}
					</p>
					<p class="meta">
						<strong>Assembly District:</strong> {result.blockInfo.assemblyDistrict ?? 'N/A'}
					</p>
					<p class="meta"><strong>Borough:</strong> {result.blockInfo.borough ?? 'N/A'}</p>
					<p class="meta">
						<strong>School District:</strong> {result.blockInfo.schoolDistrict ?? 'N/A'}
					</p>
					<p class="meta">
						<strong>Election District:</strong> {result.blockInfo.electionDistrict ?? 'N/A'}
					</p>
					{#if result.blockOwnership}
						<p class="meta"><strong>Ownership:</strong></p>
						<div class="stats-bar ownership-bar">
							<div class:active={result.blockOwnership.federal}>
								<span>Federal</span>
								<strong>{result.blockOwnership.federal ? 'Yes' : 'No'}</strong>
							</div>
							<div class:active={result.blockOwnership.state}>
								<span>State</span>
								<strong>{result.blockOwnership.state ? 'Yes' : 'No'}</strong>
							</div>
							<div class:active={result.blockOwnership.city}>
								<span>City</span>
								<strong>{result.blockOwnership.city ? 'Yes' : 'No'}</strong>
							</div>
							<div class:active={result.blockOwnership.private}>
								<span>Private</span>
								<strong>{result.blockOwnership.private ? 'Yes' : 'No'}</strong>
							</div>
						</div>
					{/if}
				</div>
			{/if}
			{#if result.insideBlueZone && result.zoneOwnership}
				<div class="block-info">
					<p class="block-title">Land tenure</p>
					<div class="stats-bar ownership-bar">
						<div class:active={result.zoneOwnership.federal}>
							<span>Federal</span>
							<strong>{result.zoneOwnership.federal ? 'Yes' : 'No'}</strong>
						</div>
						<div class:active={result.zoneOwnership.state}>
							<span>State</span>
							<strong>{result.zoneOwnership.state ? 'Yes' : 'No'}</strong>
						</div>
						<div class:active={result.zoneOwnership.city}>
							<span>City</span>
							<strong>{result.zoneOwnership.city ? 'Yes' : 'No'}</strong>
						</div>
						<div class:active={result.zoneOwnership.private}>
							<span>Private</span>
							<strong>{result.zoneOwnership.private ? 'Yes' : 'No'}</strong>
						</div>
					</div>
				</div>
			{/if}

		</div>
	{/if}
	
	<h3>About the Data</h3>
	<p style="margin: 0px;">Expand each section to learn more about the data sources behind each flood risk category.</p>

	<div class="criteria-accordion">
		<div class="criteria-item">
			<button
				type="button"
				class="criteria-row-toggle"
				aria-expanded={criteriaExpanded.past}
				onclick={() => toggleCriteriaSection('past')}
			>
				<span class="criteria-heading">Past</span>
				<span class="criteria-expand-icon" aria-hidden="true">{criteriaExpanded.past ? '−' : '+'}</span>
			</button>
			{#if criteriaExpanded.past}
				<div class="criteria-panel-body" transition:slide={accordionSlide}>
					<ul class="criteria-sources">
						<li>Historical ecology — Based on the block-by-block historical landscape data of the <a href="https://www.welikia.org/">NYBG Welikia Project.</a></li>
					</ul>
				</div>
			{/if}
		</div>

		<div class="criteria-item">
			<button
				type="button"
				class="criteria-row-toggle"
				aria-expanded={criteriaExpanded.present}
				onclick={() => toggleCriteriaSection('present')}
			>
				<span class="criteria-heading">Present</span>
				<span class="criteria-expand-icon" aria-hidden="true">{criteriaExpanded.present ? '−' : '+'}</span>
			</button>
			{#if criteriaExpanded.present}
				<div class="criteria-panel-body" transition:slide={accordionSlide}>
					<ul class="criteria-sources">
						<li>NYC Office of Technology and Innovation — <a target="_blank" href="https://data.cityofnewyork.us/Social-Services/311-Service-Requests-from-2020-to-Present/erm2-nwe9">311 calls of reported flooding</a></li>
						<li>NYC Department of Environmental Protection — <a target="_blank" href="https://data.cityofnewyork.us/Environment/NYC-Stormwater-Flood-Maps/9i7c-xyvv/about_data">Stormwater Flood Maps</a></li>
						<li>Federal Emergency Management Agency — <a target="_blank" href="https://data.cityofnewyork.us/Environment/Sea-Level-Rise-Maps-2050s-100-year-Floodplain-/hbw8-2bah">100 year flood plain</a></li>
						<li>NYC Department of Small Business Services —  <a href="https://data.cityofnewyork.us/Environment/Sandy-Inundation-Zone/uyj8-7rv5" target="_blank">Hurricane Sandy Inundation zones</a></li>
					</ul>
				</div>
			{/if}
		</div>

		<div class="criteria-item">
			<button
				type="button"
				class="criteria-row-toggle"
				aria-expanded={criteriaExpanded.future}
				onclick={() => toggleCriteriaSection('future')}
			>
				<span class="criteria-heading">Future</span>
				<span class="criteria-expand-icon" aria-hidden="true">{criteriaExpanded.future ? '−' : '+'}</span>
			</button>
			{#if criteriaExpanded.future}
				<div class="criteria-panel-body" transition:slide={accordionSlide}>
					<ul class="criteria-sources">
						<li>NYC Department of Environmental Protection — <a href="https://experience.arcgis.com/experience/e83a49daef8a472da4a7e34dc25ac445">Stormwater Flood Maps with Sea Level Rise projects</a></li>
						<li>NYC Mayor's Office of Climate and Environmental Justice — <a href="https://data.cityofnewyork.us/Environment/Future-Floodplain-2020s/aqw3-vugz/about_data">500 year floodplain</a></li>
					</ul>
				</div>
			{/if}
		</div>
	</div>
	<p style="margin: 0px;">To learn more about the methodology and analysis behind the Blue Zones, read our paper in the Annals of the New York Academy of Sciences <a href="https://www.documentcloud.org/documents/27929587-royte-and-sanderson-blue-zones-identifying-adaptation-opportunities-using-past-present-and-future-flooding-in-new-yor/" target="_blank">here</a>, or our post on the NYBG blog <a href="https://www.nybg.org/planttalk/blue-zones-identifying-adaptation-opportunities-using-past-present-and-future-flooding-in-new-york-city/" target="_blank">here</a>. </p>


</section>

<style>
	.controls strong{
		color:  #0b4b63;
	}
	.controls {
		display: flex;
		flex-direction: column;
		gap: 1rem;
		font-family: 'GT Super Regular', serif;
		color: #0b4b63;
	}

	.controls a,
	.controls a:visited {
		color: #079ed3;
		text-decoration: none;
	}

	.controls a:hover {
		color: #079ed3;
		opacity: 0.9;
	}

	.search-wrap {
		display: block;
	}

	.criteria-accordion {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}

	.criteria-item {
		background: rgba(255, 255, 255, 0.72);
		border: 1px solid rgba(7, 158, 211, 0.25);
		border-radius: 10px;
		padding: 0.5rem 0.65rem;
	}

	.criteria-row-toggle {
		width: 100%;
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 0.75rem;
		background: transparent;
		border: none;
		border-radius: 0;
		padding: 0;
		cursor: pointer;
		font-family: inherit;
		text-align: left;
		color: #079ed3;
	}

	.criteria-heading {
		font-size: 0.95rem;
		font-weight: 600;
	}

	.criteria-expand-icon {
		flex: 0 0 auto;
		width: 1.4rem;
		height: 1.4rem;
		border: 1px solid #079ed3;
		border-radius: 999px;
		display: inline-flex;
		align-items: center;
		justify-content: center;
		font-size: 1rem;
		line-height: 1;
	}

	.criteria-sources {
		margin: 0.45rem 0 0 1.35rem;
		padding: 0;
		display: flex;
		flex-direction: column;
		gap: 0.2rem;
		font-size: 0.88rem;
		color: black;
	}

	h3{
		margin-bottom: 0;
	}

	.criteria-scale {
		display: flex;
		flex-direction: column;
		gap: 0.35rem;
		max-width: 200px;
	}

	.scale-bar {
		display: grid;
		grid-template-columns: repeat(3, 1fr);
		height: 14px;
		max-width: 200px;
	}

	.scale-bar .step {
		border: 1px solid rgba(7, 158, 211, 0.25);
	}

	.scale-bar .step.one {
		background: rgba(7, 158, 211, 0.22);
	}

	.scale-bar .step.two {
		background: rgba(7, 158, 211, 0.45);
		border-left: none;
	}

	.scale-bar .step.three {
		background: rgba(7, 158, 211, 0.72);
		border-left: none;
	}

	.scale-labels {
		display: grid;
		grid-template-columns: repeat(3, 1fr);
		font-size: 0.78rem;
		line-height: 1;
		color: #2e5f74;
		max-width: 200px;
		text-align: right;
	}

	.scale-labels span:nth-child(1),
	.scale-labels span:nth-child(2) {
		text-align: right;
	}

	.scale-labels span:nth-child(3) {
		text-align: right;
	}

	.search-control-host {
		width: 100%;
	}

	.search-control-host :global(.stadiamaps-search-box) {
		width: 100%;
		max-width: 100%;
	}

	.search-control-host :global(.stadiamaps-search-box .input-container) {
		position: relative;
	}

	.search-control-host :global(.stadiamaps-search-box .input-container input) {
		width: 100%;
		height: 42px;
		padding: 0.55rem 2rem 0.55rem 0.85rem;
		border-radius: 8px;
		border: 1px solid rgba(7, 158, 211, 0.4);
		font-family: 'GT Super Regular', serif;
		font-size: 0.95rem;
		box-sizing: border-box;
	}

	.search-control-host :global(.stadiamaps-search-box .results) {
		width: 100%;
		margin: 0.5rem 0 0;
		border: 1px solid rgba(7, 158, 211, 0.18);
		box-shadow: 0 8px 22px rgba(0, 0, 0, 0.08);
	}

	.search-control-host :global(.stadiamaps-search-box .results .result) {
		padding: 0.6rem 0.55rem;
		border-bottom: 1px solid rgba(7, 158, 211, 0.2);
	}

	.search-control-host :global(.stadiamaps-search-box .results .result:hover),
	.search-control-host :global(.stadiamaps-search-box .results .result.hover) {
		background: rgba(7, 158, 211, 0.1);
	}

	.search-control-host :global(.stadiamaps-search-box .search-attribution) {
		font-size: 0.75rem;
	}

	.search-control-host :global(.stadiamaps-search-box .search-attribution .logo) {
		height: 20px;
		width: 20px;
		top: 0;
	}

	button {
		background: #079ed3;
		color: #f5f2eb;
		border: none;
		border-radius: 8px;
		padding: 0.7rem 0.85rem;
		cursor: pointer;
		font-family: 'GT Super Regular', serif;
	}

	button:disabled {
		opacity: 0.7;
		cursor: not-allowed;
	}

	.intro p,
	.headline {
		margin: 0;
		line-height: 1.5;
		font-size: 1rem;
	}

	.headline {
		font-size: 1.15rem;
		line-height: 1.45;
	}

	.intro {
		display: flex;
		flex-direction: column;
		gap: 0.75rem;
	}

	.intro-title {
		margin: 0;
		font-family: 'NY Botanical Gothic', serif;
		font-size: 1.85rem;
		line-height: 1.1;
		color: #0b4b63;
	}

	.error {
		margin: 0;
		font-size: 0.9rem;
		color: #b42318;
	}

	.result {
		display: flex;
		flex-direction: column;
		gap: 0.9rem;
	}

	.headline-row {
		display: flex;
		align-items: flex-start;
		gap: 0.6rem;
	}

	.copy-link-btn {
		flex: 0 0 auto;
		width: 2rem;
		height: 2rem;
		border-radius: 999px;
		padding: 0;
		display: inline-flex;
		align-items: center;
		justify-content: center;
		background: #ffffff;
		border: 1px solid rgba(7, 158, 211, 0.35);
		color: #0b4b63;
	}

	.copy-link-btn svg {
		width: 1.05rem;
		height: 1.05rem;
	}

	.nearest-cta {
		align-self: flex-start;
		background: #ffffff;
		border: 1px solid rgba(7, 158, 211, 0.35);
		color: #0b4b63;
		border-radius: 999px;
		padding: 0.45rem 0.85rem;
		font-size: 0.9rem;
		line-height: 1.2;
		transition: background-color 0.2s ease, border-color 0.2s ease;
	}

	.nearest-cta:hover {
		background: rgba(7, 158, 211, 0.1);
		border-color: rgba(7, 158, 211, 0.6);
	}

	.back {
		align-self: flex-start;
		background: transparent;
		border: none;
		border-radius: 0;
		color: #0b4b63;
		padding: 0 0 3px 0;
		font-size: 0.95rem;
		display: inline-flex;
		align-items: center;
		gap: 0.35rem;
		border-bottom: 1px solid transparent;
		transition: border-color 0.2s ease, opacity 0.2s ease;
	}

	.back:hover {
		opacity: 0.9;
		/* border-bottom-color: #0b4b63; */
	}

	.back .arrow {
		display: inline-block;
		flex-shrink: 0;
		width: 1.1em;
		height: 1.1em;
		vertical-align: -0.15em;
		transition: transform 0.2s ease;
	}

	.back:hover .arrow {
		transform: translate(2px, -2px);
	}

	.copied-note {
		margin: -0.35rem 0 0;
		font-size: 0.8rem;
		color: #2e5f74;
	}

	.meta {
		margin: 0;
		font-size: 0.92rem;
		color: #2e5f74;
	}

	.meta.small {
		font-size: 0.86rem;
	}

	.block-info {
		border-top: 1px solid rgba(7, 158, 211, 0.22);
		padding-top: 0.8rem;
		display: flex;
		flex-direction: column;
		gap: 0.28rem;
	}

	.block-title {
		margin: 0 0 0.2rem 0;
		font-size: 0.86rem;
		text-transform: uppercase;
		color: #2e5f74;
	}

	.stats-bar {
		display: grid;
		grid-template-columns: repeat(3, minmax(0, 1fr));
		border: 1px solid rgba(7, 158, 211, 0.35);
		border-radius: 10px;
		overflow: hidden;
	}

	.stats-bar > div {
		background: #ffffff;
		padding: 0.65rem 0.55rem;
		display: flex;
		flex-direction: column;
		gap: 0.15rem;
		border-right: 1px solid rgba(7, 158, 211, 0.25);
	}

	.stats-bar > div:last-child {
		border-right: none;
	}

	.stats-bar > div.active {
		background: rgba(7, 158, 211, 0.12);
	}

	.stats-bar span {
		font-size: 0.75rem;
		text-transform: uppercase;
		letter-spacing: 0.07em;
		color: #3a6373;
	}

	.stats-bar strong {
		font-size: 0.95rem;
		color: #0b4b63;
	}

	.ownership-bar {
		grid-template-columns: repeat(4, minmax(0, 1fr));
	}

</style>
