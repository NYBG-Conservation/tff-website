<script lang="ts">
	import { PUBLIC_MAPTILER_KEY } from '$env/static/public';
	import {
		MAPSTORE_CONTEXT_KEY,
		type MapStore,
		blueZonesMapLayersReady,
		blueZonesSearchMount,
		blueZonesSearchResult,
		blueZonesSelectedPolygon,
		blueZonesCriteriaFilter
	} from '../../stores';
	import { MapLibreSearchControl } from '../search/MapLibreSearchBox';
	import 'maplibre-gl/dist/maplibre-gl.css';
	import maplibregl from 'maplibre-gl';
	import union from '@turf/union';
	import { featureCollection } from '@turf/helpers';
	import { getContext, untrack } from 'svelte';

	let mapStore: MapStore = getContext(MAPSTORE_CONTEXT_KEY);
	const MAPTILER_STYLE_ID = '019d01cd-0eb7-7c62-9be0-65ff812b59c5';
	const STADIA_KEY = import.meta.env.PUBLIC_STADIA_KEY as string | undefined;

	const ZONE_BOUNDARIES_URL = '/data/blue-zones/phase1/zone_boundaries.geojson';
	const FULL_GEOJSON_URL = '/data/blue-zones/blue_zone_4326.json';
	const TILES_META_URL = '/data/blue-zones/tiles/meta.json';

	type TilesMeta = {
		vectorTiles: boolean;
		sourceLayer: string;
		tilesUrl: string;
		minzoom?: number;
		maxzoom?: number;
	};

	let mapContainer: HTMLDivElement | undefined = $state();

	$effect(() =>
		untrack(() => {
			if (!mapContainer) return;
			blueZonesMapLayersReady.set(false);
			let searchMountHost: HTMLElement | null = null;
			let searchMarker: maplibregl.Marker | null = null;
			const emptySelection = {
				type: 'FeatureCollection',
				features: []
			} as GeoJSON.FeatureCollection;
			const selectedZoneByGridcode = new Map<number, GeoJSON.Feature>();
			const selectedByUniqueId = new Map<number, GeoJSON.Feature>();
			const selectedByAtomicId = new Map<string, GeoJSON.Feature>();
			let zoneBoundariesLoaded = false;
			let fullAtomicIndexLoaded = false;

			const isBlueZone = (props: Record<string, unknown> | undefined) =>
				props?.BZ_past_correct === 1 &&
				props?.BZ_present_correct === 1 &&
				props?.BZ_future_correct === 1;
			const buildCriteriaCountExpression = (criteria: {
				past: boolean;
				present: boolean;
				future: boolean;
			}) =>
				[
					'+',
					['case', ['==', ['get', 'BZ_past_correct'], 1], criteria.past ? 1 : 0, 0],
					['case', ['==', ['get', 'BZ_present_correct'], 1], criteria.present ? 1 : 0, 0],
					['case', ['==', ['get', 'BZ_future_correct'], 1], criteria.future ? 1 : 0, 0]
				] as any;

			const applyCriteriaFilter = (criteria: {
				past: boolean;
				present: boolean;
				future: boolean;
			}) => {
				if (!map.getLayer('blue-zones-bz-fill')) return;
				const countExpression = buildCriteriaCountExpression(criteria);
				// Only render polygons that satisfy all three criteria (3/3).
				map.setFilter('blue-zones-bz-fill', ['==', countExpression, 3] as any);
				map.setPaintProperty('blue-zones-bz-fill', 'fill-opacity', 0.5);
			};

			/** zone_boundaries.geojson stores many separate polygons in one MultiPolygon without geometric union; line layers draw each ring. Merge for a single zone outline. */
			const dissolvedZoneOutlineCache = new Map<number, GeoJSON.Feature>();

			function dissolveMultiPolygonZoneOutline(feature: GeoJSON.Feature): GeoJSON.Feature {
				const g = feature.geometry;
				if (!g || g.type !== 'MultiPolygon') return feature;
				const polys = g.coordinates;
				if (polys.length <= 1) return feature;

				const gc = feature.properties?.gridcode;
				if (typeof gc === 'number') {
					const cached = dissolvedZoneOutlineCache.get(gc);
					if (cached) return cached;
				}

				let merged: GeoJSON.Feature<GeoJSON.Polygon | GeoJSON.MultiPolygon> = {
					type: 'Feature',
					properties: {},
					geometry: { type: 'Polygon', coordinates: polys[0] }
				};
				for (let i = 1; i < polys.length; i++) {
					const next: GeoJSON.Feature<GeoJSON.Polygon> = {
						type: 'Feature',
						properties: {},
						geometry: { type: 'Polygon', coordinates: polys[i] }
					};
					const u = union(featureCollection([merged, next] as any));
					if (u && u.type === 'Feature' && u.geometry) {
						merged = u as GeoJSON.Feature<GeoJSON.Polygon | GeoJSON.MultiPolygon>;
					}
				}
				const out = { ...feature, geometry: merged.geometry };
				if (typeof gc === 'number') dissolvedZoneOutlineCache.set(gc, out);
				return out;
			}

			const setSelectionData = (feature: GeoJSON.Feature | null) => {
				const source = map.getSource('blue-zones-selected') as maplibregl.GeoJSONSource | undefined;
				if (!source) return;
				if (!feature) {
					source.setData(emptySelection);
					return;
				}
				const outline =
					feature.geometry?.type === 'MultiPolygon' &&
					feature.properties &&
					typeof (feature.properties as Record<string, unknown>).gridcode === 'number'
						? dissolveMultiPolygonZoneOutline(feature)
						: feature;
				source.setData({
					type: 'FeatureCollection',
					features: [outline]
				});
			};

			const loadZoneBoundariesForSelection = async () => {
				if (zoneBoundariesLoaded) return;
				const response = await fetch(ZONE_BOUNDARIES_URL);
				if (response.ok) {
					const data = (await response.json()) as GeoJSON.FeatureCollection;
					for (const feature of data.features) {
						const gridcode = feature.properties?.gridcode;
						if (typeof gridcode === 'number') {
							selectedZoneByGridcode.set(gridcode, feature);
						}
					}
				}
				zoneBoundariesLoaded = true;
			};

			/** Loads per-polygon lookups; only runs when needed. If zone_boundaries.geojson is missing, also builds merged gridcode outlines here. */
			const loadFullAtomicIndexForSelection = async () => {
				if (fullAtomicIndexLoaded) return;
				const response = await fetch(FULL_GEOJSON_URL);
				if (!response.ok) return;
				const data = (await response.json()) as GeoJSON.FeatureCollection;
				for (const feature of data.features) {
					const props = (feature.properties ?? {}) as Record<string, unknown>;
					const uniqueId = props.unique_id;
					const atomicId = props.ATOMICID;
					if (typeof uniqueId === 'number') selectedByUniqueId.set(uniqueId, feature);
					if (typeof atomicId === 'string') selectedByAtomicId.set(atomicId, feature);
				}
				if (selectedZoneByGridcode.size === 0) {
					for (const feature of data.features) {
						const props = (feature.properties ?? {}) as Record<string, unknown>;
						const gridcode = props.gridcode;
						if (typeof gridcode !== 'number' || !isBlueZone(props)) continue;
						const current = selectedZoneByGridcode.get(gridcode);
						if (!current) {
							selectedZoneByGridcode.set(gridcode, feature);
						} else {
							const merged = union(featureCollection([current, feature] as any));
							if (merged) selectedZoneByGridcode.set(gridcode, merged as GeoJSON.Feature);
						}
					}
				}
				fullAtomicIndexLoaded = true;
			};

			const loadSelectionFeatures = async (selected: {
				gridcode?: number;
				uniqueId?: number;
				atomicId?: string;
			}) => {
				await loadZoneBoundariesForSelection();
				if (selected.uniqueId != null || selected.atomicId != null) {
					await loadFullAtomicIndexForSelection();
					return;
				}
				if (typeof selected.gridcode === 'number' && !selectedZoneByGridcode.has(selected.gridcode)) {
					await loadFullAtomicIndexForSelection();
				}
			};

			const mapStyleUrl = PUBLIC_MAPTILER_KEY
				? `https://api.maptiler.com/maps/${MAPTILER_STYLE_ID}/style.json?key=${PUBLIC_MAPTILER_KEY}`
				: 'https://demotiles.maplibre.org/style.json';

			const map = new maplibregl.Map({
				container: mapContainer,
				style: mapStyleUrl,
				center: [-74.0002, 40.7056],
				zoom: 10,
				hash: true,
				attributionControl: false
			});
			const getShareSelectionFlag = (): boolean => {
				if (typeof window === 'undefined') return false;
				const q = new URLSearchParams(window.location.search).get('bz_share')?.toLowerCase();
				if (q === '1' || q === 'true' || q === 'yes') return true;
				// Also support lightweight hash flags, e.g. ...#10/40.7/-74.0&share
				const h = window.location.hash.toLowerCase();
				return h.includes('&share') || h.includes('/share');
			};
			const clearShareSelectionFlag = () => {
				if (typeof window === 'undefined') return;
				const next = new URL(window.location.href);
				if (!next.searchParams.has('bz_share')) return;
				next.searchParams.delete('bz_share');
				window.history.replaceState({}, '', next.toString());
			};

			let mapLayersReadyFallbackTimer: ReturnType<typeof setTimeout> | null = null;
			const clearMapLayersReadyFallbackTimer = () => {
				if (mapLayersReadyFallbackTimer != null) {
					clearTimeout(mapLayersReadyFallbackTimer);
					mapLayersReadyFallbackTimer = null;
				}
			};

			map.on('error', (error) => {
				console.error('MapLibre error:', error?.error ?? error);
				clearMapLayersReadyFallbackTimer();
				blueZonesMapLayersReady.set(true);
			});

			/** Bbox center of polygon geometry — matches search `flyTo` target (zoom 14). */
			const centerOfPolygonGeometry = (
				geom: GeoJSON.Geometry | undefined
			): [number, number] | null => {
				if (!geom || (geom.type !== 'Polygon' && geom.type !== 'MultiPolygon')) {
					return null;
				}
				let minLng = Infinity;
				let maxLng = -Infinity;
				let minLat = Infinity;
				let maxLat = -Infinity;
				const expandRing = (ring: number[][]) => {
					for (const c of ring) {
						const lng = c[0];
						const lat = c[1];
						if (typeof lng !== 'number' || typeof lat !== 'number') continue;
						minLng = Math.min(minLng, lng);
						maxLng = Math.max(maxLng, lng);
						minLat = Math.min(minLat, lat);
						maxLat = Math.max(maxLat, lat);
					}
				};
				if (geom.type === 'Polygon') {
					for (const ring of geom.coordinates) expandRing(ring);
				} else {
					for (const poly of geom.coordinates) {
						for (const ring of poly) expandRing(ring);
					}
				}
				if (!Number.isFinite(minLng)) return null;
				return [(minLng + maxLng) / 2, (minLat + maxLat) / 2];
			};

			const selectFromPoint = (point: { x: number; y: number }) => {
				// Guard: ensure layer exists before querying
				if (!map.getLayer('blue-zones-hit-area')) {
					return;
				}
				const hits = map.queryRenderedFeatures([point.x, point.y], {
					layers: ['blue-zones-hit-area']
				});
				if (!hits.length) {
					blueZonesSelectedPolygon.set(null);
					return;
				}

				const selected = hits[0];
				const props = selected.properties as Record<string, unknown> | undefined;
				const gridcode = props?.gridcode;
				const uniqueId = props?.unique_id;
				const atomicId = props?.ATOMICID;

				const flyToSelection = () => {
					const c = centerOfPolygonGeometry(selected.geometry);
					if (c) {
						map.flyTo({ center: c, zoom: 13.5, essential: true });
					}
				};

				if (typeof gridcode === 'number' && isBlueZone(props)) {
					flyToSelection();
					blueZonesSelectedPolygon.set({ gridcode });
					return;
				}
				if (typeof uniqueId === 'number') {
					flyToSelection();
					blueZonesSelectedPolygon.set({ uniqueId });
					return;
				}
				if (typeof atomicId === 'string') {
					flyToSelection();
					blueZonesSelectedPolygon.set({ atomicId });
					return;
				}
				blueZonesSelectedPolygon.set(null);
			};

			const searchControl = new MapLibreSearchControl({
				apiKey: STADIA_KEY ?? null,
				searchOnEnter: true,
				onResultSelected: (feature) => {
					if (feature.geometry?.type === 'Point') {
						const [lon, lat] = feature.geometry.coordinates;
						map.flyTo({ center: [lon, lat], zoom: 13.5, essential: true });
						blueZonesSearchResult.set({
							label: feature.properties.name,
							coordinates: [lon, lat],
							properties: feature.properties as unknown as Record<string, unknown>
						});
					}
				}
			});
			const searchElement = searchControl.onAdd(map);

			const unSubSearchMount = blueZonesSearchMount.subscribe((host) => {
				searchMountHost = host;
				if (!host) return;
				if (searchElement.parentElement !== host) {
					host.appendChild(searchElement);
				}
			});

			const unSubSearchResult = blueZonesSearchResult.subscribe((selected) => {
				if (!selected) return;

				searchMarker?.remove();
				searchMarker = new maplibregl.Marker({ color: '#079ED3' })
					.setLngLat(selected.coordinates)
					.addTo(map);
			});

			map.on('load', () => {
				void (async () => {
					try {
						let tilesMeta: TilesMeta | null = null;
						try {
							const res = await fetch(TILES_META_URL);
							if (res.ok) {
								const parsed = (await res.json()) as TilesMeta;
								if (parsed.vectorTiles && parsed.sourceLayer && parsed.tilesUrl) {
									tilesMeta = parsed;
								}
							}
						} catch {
							tilesMeta = null;
						}

						const origin =
							typeof window !== 'undefined' ? window.location.origin : '';
						const tileUrlAbsolute = tilesMeta?.tilesUrl?.startsWith('http')
							? tilesMeta.tilesUrl
							: `${origin}${tilesMeta?.tilesUrl ?? ''}`;

						if (tilesMeta) {
							map.addSource('blue-zones', {
								type: 'vector',
								tiles: [tileUrlAbsolute],
								minzoom: tilesMeta.minzoom ?? 0,
								maxzoom: tilesMeta.maxzoom ?? 14
							});
						} else {
							try {
								const geojsonRes = await fetch(FULL_GEOJSON_URL);
								if (!geojsonRes.ok) {
									console.error(`Failed to fetch GeoJSON: ${geojsonRes.status} ${geojsonRes.statusText}`);
									throw new Error(`GeoJSON fetch returned ${geojsonRes.status}`);
								}
								const geojsonData = await geojsonRes.json();
								map.addSource('blue-zones', {
									type: 'geojson',
									data: geojsonData
								});
							} catch (err) {
								console.error('Failed to load GeoJSON source:', err);
								blueZonesMapLayersReady.set(true);
								return;
							}
						}

						const sl = tilesMeta?.sourceLayer;

						map.addSource('blue-zones-selected', {
							type: 'geojson',
							data: emptySelection
						});

						const hitLayer: maplibregl.LayerSpecification = {
							id: 'blue-zones-hit-area',
							type: 'fill',
							source: 'blue-zones',
							...(sl ? { 'source-layer': sl } : {}),
							paint: {
								'fill-color': '#000000',
								'fill-opacity': 0
							}
						};
						map.addLayer(hitLayer);

						const fillLayer: maplibregl.LayerSpecification = {
							id: 'blue-zones-bz-fill',
							type: 'fill',
							source: 'blue-zones',
							...(sl ? { 'source-layer': sl } : {}),
							filter: ['==', ['get', 'unique_id'], -1],
							paint: {
								'fill-color': '#079ED3',
								'fill-opacity': 0.72
							}
						};
						map.addLayer(fillLayer);

						map.addLayer({
							id: 'blue-zones-selected-glow',
							type: 'line',
							source: 'blue-zones-selected',
							paint: {
								'line-color': '#079ED3',
								'line-width': 9,
								'line-opacity': 0.35,
								'line-blur': 1.1
							}
						});

						map.addLayer({
							id: 'blue-zones-selected-outline',
							type: 'line',
							source: 'blue-zones-selected',
							paint: {
								'line-color': '#036f96',
								'line-width': 3.2
							}
						});

						applyCriteriaFilter({ past: true, present: true, future: true });

						mapLayersReadyFallbackTimer = window.setTimeout(() => {
							console.warn('Blue Zones map idle timeout reached; forcing ready state');
							blueZonesMapLayersReady.set(true);
							mapLayersReadyFallbackTimer = null;
						}, 15000);

						map.once('idle', () => {
							clearMapLayersReadyFallbackTimer();
							blueZonesMapLayersReady.set(true);
							const shouldSelectFromShare = getShareSelectionFlag();
							if (map.getZoom() <= 13.5 && !shouldSelectFromShare) return;
							const centerPixel = map.project(map.getCenter());
							selectFromPoint({ x: centerPixel.x, y: centerPixel.y });
							if (shouldSelectFromShare) clearShareSelectionFlag();
						});
					} catch (err) {
						clearMapLayersReadyFallbackTimer();
						console.error(err);
						blueZonesMapLayersReady.set(true);
					}
				})();
			});

			map.on('click', (event) => {
				selectFromPoint({ x: event.point.x, y: event.point.y });
			});

			const unSubSelectedPolygon = blueZonesSelectedPolygon.subscribe((selected) => {
				(async () => {
					if (!selected) {
						setSelectionData(null);
						return;
					}
					await loadSelectionFeatures(selected);
					if (typeof selected.gridcode === 'number') {
						setSelectionData(selectedZoneByGridcode.get(selected.gridcode) ?? null);
						return;
					}
					if (typeof selected.uniqueId === 'number') {
						setSelectionData(selectedByUniqueId.get(selected.uniqueId) ?? null);
						return;
					}
					if (typeof selected.atomicId === 'string') {
						setSelectionData(selectedByAtomicId.get(selected.atomicId) ?? null);
						return;
					}
					setSelectionData(null);
				})();
			});

			const unSubCriteriaFilter = blueZonesCriteriaFilter.subscribe((criteria) => {
				applyCriteriaFilter(criteria);
			});

			map.addControl(new maplibregl.NavigationControl({}), 'top-right');
			map.addControl(new maplibregl.GlobeControl(), 'top-right');
			map.addControl(
				new maplibregl.GeolocateControl({
					positionOptions: { enableHighAccuracy: true },
					trackUserLocation: true
				}),
				'top-right'
			);
			map.addControl(new maplibregl.ScaleControl({ maxWidth: 80, unit: 'metric' }), 'bottom-left');
			map.addControl(new maplibregl.AttributionControl({ compact: true }), 'bottom-right');

			mapStore?.set(map);

			return () => {
				blueZonesMapLayersReady.set(false);
				clearMapLayersReadyFallbackTimer();
				unSubSearchMount();
				unSubSearchResult();
				unSubSelectedPolygon();
				unSubCriteriaFilter();
				searchMarker?.remove();
				if (searchElement.parentElement && searchElement.parentElement === searchMountHost) {
					searchElement.parentElement.removeChild(searchElement);
				}
				searchControl.onRemove(map);
				map.remove();
			};
		})
	);
</script>

<div class="map" data-testid="map" bind:this={mapContainer}></div>

<style>
	.map {
		position: absolute;
		top: 0;
		bottom: 0;
		width: 100%;
		z-index: 1;
	}
</style>
