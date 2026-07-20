import { useEffect, useRef } from "react";
import maplibregl from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";

const EMPTY_GEOJSON = {
  type: "FeatureCollection",
  features: [],
};

function extendBounds(bounds, coordinates) {
  if (
    Array.isArray(coordinates) &&
    coordinates.length >= 2 &&
    typeof coordinates[0] === "number" &&
    typeof coordinates[1] === "number"
  ) {
    bounds.extend(coordinates);
    return;
  }

  if (!Array.isArray(coordinates)) {
    return;
    }

    coordinates.forEach((coordinate) => {
    extendBounds(bounds, coordinate);
    });
}

function fitMapToGeojson(map, geojson) {
  if (!geojson?.features?.length) {
    return;
  }

  const bounds = new maplibregl.LngLatBounds();

  geojson.features.forEach((feature) => {
    if (feature.geometry?.coordinates) {
      extendBounds(bounds, feature.geometry.coordinates);
    }
  });

  if (!bounds.isEmpty()) {
    map.fitBounds(bounds, {
      padding: 50,
      maxZoom: 17,
      duration: 800,
    });
  }
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function MapPanel({ geojson = EMPTY_GEOJSON, title = "Map Results" }) {
  const mapContainerRef = useRef(null);
  const mapRef = useRef(null);
  const latestGeojsonRef = useRef(geojson);

  useEffect(() => {
    latestGeojsonRef.current = geojson;
  }, [geojson]);

  useEffect(() => {
    if (mapRef.current || !mapContainerRef.current) {
      return;
    }

    const map = new maplibregl.Map({
      container: mapContainerRef.current,

      style: {
        version: 8,
        sources: {
          osm: {
            type: "raster",
            tiles: [
              "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
            ],
            tileSize: 256,
            attribution:
              '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
          },
        },
        layers: [
          {
            id: "osm",
            type: "raster",
            source: "osm",
          },
        ],
      },

      center: [39.2, -6.16],
      zoom: 11,
    });

    map.addControl(
      new maplibregl.NavigationControl(),
      "top-right",
    );

    map.on("load", () => {
      const initialGeojson = latestGeojsonRef.current;

      map.addSource("query-results", {
        type: "geojson",
        data: initialGeojson,
      });

      map.addLayer({
        id: "query-results-fill",
        type: "fill",
        source: "query-results",
        filter: ["==", ["geometry-type"], "Polygon"],
        paint: {
          "fill-color": [
            "match",
            ["get", "status"],
            "approved",
            "#16a34a",
            "in_process",
            "#2563eb",
            "#6b7280",
          ],
          "fill-opacity": 0.4,
        },
      });

      map.addLayer({
        id: "query-results-outline",
        type: "line",
        source: "query-results",
        filter: ["==", ["geometry-type"], "Polygon"],
        paint: {
          "line-color": [
            "match",
            ["get", "status"],
            "approved",
            "#166534",
            "in_process",
            "#1d4ed8",
            "#374151",
          ],
          "line-width": 2,
        },
      });

      map.addLayer({
        id: "query-results-points",
        type: "circle",
        source: "query-results",
        filter: ["==", ["geometry-type"], "Point"],
        paint: {
          "circle-radius": 7,
          "circle-color": "#dc2626",
          "circle-stroke-color": "#ffffff",
          "circle-stroke-width": 2,
        },
      });

      fitMapToGeojson(map, initialGeojson);

      map.on("click", "query-results-fill", (event) => {
        const feature = event.features?.[0];

        if (!feature) {
          return;
        }

        const properties = feature.properties ?? {};

        const statusLabel = String(
          properties.status ?? "Unknown"
        ).replaceAll("_", " ");

        const popupContent = `
          <div class="parcel-popup">
            <h3>Parcel Information</h3>

            <div class="parcel-popup-row">
              <strong>Plot number:</strong>
              <span>
                ${escapeHtml(properties.plot_number ?? "—")}
              </span>
            </div>

            <div class="parcel-popup-row">
              <strong>Parcel UID:</strong>
              <span>
                ${escapeHtml(properties.parcel_uid ?? "—")}
              </span>
            </div>

            <div class="parcel-popup-row">
              <strong>Status:</strong>
              <span>
                ${escapeHtml(statusLabel)}
              </span>
            </div>

            <div class="parcel-popup-row">
              <strong>District:</strong>
              <span>
                ${escapeHtml(properties.district_name ?? "—")}
              </span>
            </div>

            <div class="parcel-popup-row">
              <strong>Valid from:</strong>
              <span>
                ${escapeHtml(properties.valid_from ?? "—")}
              </span>
            </div>
          </div>
        `;

        new maplibregl.Popup({
          closeButton: true,
          closeOnClick: true,
          maxWidth: "340px",
        })
          .setLngLat(event.lngLat)
          .setHTML(popupContent)
          .addTo(map);
      });

      map.on("mouseenter", "query-results-fill", () => {
        map.getCanvas().style.cursor = "pointer";
      });

      map.on("mouseleave", "query-results-fill", () => {
        map.getCanvas().style.cursor = "";
      });
    });

    mapRef.current = map;

    return () => {
      map.remove();
      mapRef.current = null;
    };
  }, []);

  useEffect(() => {
    const map = mapRef.current;

    if (!map || !map.isStyleLoaded()) {
      return;
    }

    const source = map.getSource("query-results");

    if (!source) {
      return;
    }

    source.setData(geojson);
    fitMapToGeojson(map, geojson);
  }, [geojson]);

  return (
    <div className="map-wrapper">
        <div
            ref={mapContainerRef}
            className="map-container"
        />

        <div className="map-title">
            {title}
        </div>

        <div className="map-legend">
            <div className="map-legend-title">
                Parcel Status
            </div>

            <div className="map-legend-item">
                <span className="legend-symbol approved" />
                <span>Approved</span>
            </div>

            <div className="map-legend-item">
                <span className="legend-symbol in-process" />
                <span>In process</span>
            </div>
        </div>
    </div>
  );
}

export default MapPanel;