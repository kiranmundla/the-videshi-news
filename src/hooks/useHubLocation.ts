import { useState, useCallback } from "react";

export interface HubLocation {
  city: string;
  state: string;
  lat: number;
  lon: number;
  /** Display label, e.g. "San Jose, CA" */
  label: string;
}

const STORAGE_KEY = "videshi-user-location";

function readStored(): HubLocation | null {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return null;
    const loc = JSON.parse(raw);
    if (typeof loc.lat !== "number" || typeof loc.lon !== "number") return null;
    return loc as HubLocation;
  } catch {
    return null;
  }
}

/* Top US metros by Indian-diaspora presence (coordinates are metro centers).
   Used for the manual picker fallback when geolocation is denied. */
export const METRO_PICKER: { city: string; state: string; lat: number; lon: number }[] = [
  { city: "New York", state: "NY", lat: 40.7128, lon: -74.006 },
  { city: "San Jose", state: "CA", lat: 37.3382, lon: -121.8863 },
  { city: "San Francisco", state: "CA", lat: 37.7749, lon: -122.4194 },
  { city: "Los Angeles", state: "CA", lat: 34.0522, lon: -118.2437 },
  { city: "Chicago", state: "IL", lat: 41.8781, lon: -87.6298 },
  { city: "Houston", state: "TX", lat: 29.7604, lon: -95.3698 },
  { city: "Dallas", state: "TX", lat: 32.7767, lon: -96.797 },
  { city: "Austin", state: "TX", lat: 30.2672, lon: -97.7431 },
  { city: "Seattle", state: "WA", lat: 47.6062, lon: -122.3321 },
  { city: "Boston", state: "MA", lat: 42.3601, lon: -71.0589 },
  { city: "Atlanta", state: "GA", lat: 33.749, lon: -84.388 },
  { city: "Washington", state: "DC", lat: 38.9072, lon: -77.0369 },
  { city: "Edison", state: "NJ", lat: 40.5187, lon: -74.4121 },
  { city: "Philadelphia", state: "PA", lat: 39.9526, lon: -75.1652 },
  { city: "Miami", state: "FL", lat: 25.7617, lon: -80.1918 },
  { city: "Denver", state: "CO", lat: 39.7392, lon: -104.9903 },
  { city: "Phoenix", state: "AZ", lat: 33.4484, lon: -112.074 },
  { city: "San Diego", state: "CA", lat: 32.7157, lon: -117.1611 },
  { city: "Minneapolis", state: "MN", lat: 44.9778, lon: -93.265 },
  { city: "Detroit", state: "MI", lat: 42.3314, lon: -83.0458 },
  { city: "Portland", state: "OR", lat: 45.5152, lon: -122.6784 },
  { city: "Columbus", state: "OH", lat: 39.9612, lon: -82.9988 },
  { city: "Raleigh", state: "NC", lat: 35.7796, lon: -78.6382 },
  { city: "Tampa", state: "FL", lat: 27.9506, lon: -82.4572 },
  { city: "Las Vegas", state: "NV", lat: 36.1699, lon: -115.1398 },
];

/**
 * User-chosen hub location, persisted in localStorage.
 * Unlike the transient IP-geo hook, this is an explicit user setting —
 * it never expires and is only changed by the user.
 */
export function useHubLocation() {
  const [location, setLocationState] = useState<HubLocation | null>(readStored);

  const setLocation = useCallback((loc: HubLocation) => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(loc));
    } catch {
      /* quota exceeded — ignore */
    }
    setLocationState(loc);
  }, []);

  const clearLocation = useCallback(() => {
    try {
      localStorage.removeItem(STORAGE_KEY);
    } catch {
      /* ignore */
    }
    setLocationState(null);
  }, []);

  return { location, setLocation, clearLocation, isSet: location !== null };
}

/** Great-circle distance in miles. */
export function haversineMiles(
  lat1: number,
  lon1: number,
  lat2: number,
  lon2: number,
): number {
  const R = 3958.8; // Earth radius in miles
  const dLat = ((lat2 - lat1) * Math.PI) / 180;
  const dLon = ((lon2 - lon1) * Math.PI) / 180;
  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos((lat1 * Math.PI) / 180) *
      Math.cos((lat2 * Math.PI) / 180) *
      Math.sin(dLon / 2) *
      Math.sin(dLon / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return R * c;
}
