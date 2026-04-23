import type { Map as MapLibreMap } from 'maplibre-gl';
import { writable, type Writable } from 'svelte/store';

export type MapStore = Writable<MapLibreMap | null>;

export const MAPSTORE_CONTEXT_KEY = Symbol('MAPSTORE_CONTEXT_KEY');

export function createMapStore(initialValue: MapLibreMap | null = null): MapStore {
	return writable(initialValue);
}

export type BlueZonesSearchResult = {
	label: string;
	coordinates: [number, number];
	properties: Record<string, unknown>;
};

export const blueZonesSearchResult = writable<BlueZonesSearchResult | null>(null);
export const blueZonesSearchMount = writable<HTMLElement | null>(null);

export type BlueZonesSelectedPolygon = {
	uniqueId?: number;
	atomicId?: string;
	gridcode?: number;
};

export const blueZonesSelectedPolygon = writable<BlueZonesSelectedPolygon | null>(null);

export type BlueZonesCriteriaFilter = {
	past: boolean;
	present: boolean;
	future: boolean;
};

export const blueZonesCriteriaFilter = writable<BlueZonesCriteriaFilter>({
	past: true,
	present: true,
	future: true
});

/** True after Blue Zone vector/geo layers are added and the map has idled (first paint). */
export const blueZonesMapLayersReady = writable(false);
