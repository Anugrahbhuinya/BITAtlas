// src/features/navigation/hooks/useNavigation.ts

import { useState, useEffect, useCallback } from "react";
import navigationApi from "../services/navigationApi";
import type { Building, Room, Facility, Landmark, Pathway, NavigationSearchResult } from "../types";

export function useBuildings(initialParams?: { search?: string; category?: string }) {
  const [buildings, setBuildings] = useState<Building[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [params, setParams] = useState(initialParams || {});

  const fetchBuildings = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await navigationApi.fetchBuildings(params);
      setBuildings(data.buildings);
      setTotal(data.total);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to load buildings");
    } finally {
      setLoading(false);
    }
  }, [params]);

  useEffect(() => {
    fetchBuildings();
  }, [fetchBuildings]);

  return { buildings, total, loading, error, refetch: fetchBuildings, params, setParams };
}

export function useRooms(buildingId?: string) {
  const [rooms, setRooms] = useState<Room[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchRooms = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await navigationApi.fetchRooms({ building_id: buildingId, limit: 200 });
      setRooms(data.rooms);
      setTotal(data.total);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to load rooms");
    } finally {
      setLoading(false);
    }
  }, [buildingId]);

  useEffect(() => {
    fetchRooms();
  }, [fetchRooms]);

  return { rooms, total, loading, error, refetch: fetchRooms };
}

export function useFacilities(category?: string) {
  const [facilities, setFacilities] = useState<Facility[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchFacilities = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await navigationApi.fetchFacilities({ category, limit: 100 });
      setFacilities(data.facilities);
      setTotal(data.total);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to load facilities");
    } finally {
      setLoading(false);
    }
  }, [category]);

  useEffect(() => {
    fetchFacilities();
  }, [fetchFacilities]);

  return { facilities, total, loading, error, refetch: fetchFacilities };
}

export function useLandmarks(category?: string) {
  const [landmarks, setLandmarks] = useState<Landmark[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchLandmarks = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await navigationApi.fetchLandmarks({ category, limit: 100 });
      setLandmarks(data.landmarks);
      setTotal(data.total);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to load landmarks");
    } finally {
      setLoading(false);
    }
  }, [category]);

  useEffect(() => {
    fetchLandmarks();
  }, [fetchLandmarks]);

  return { landmarks, total, loading, error, refetch: fetchLandmarks };
}

export function useNavigationSearch() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<NavigationSearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const performSearch = useCallback(async (searchQuery: string) => {
    if (!searchQuery || searchQuery.trim().length < 2) {
      setResults([]);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const data = await navigationApi.searchNavigation(searchQuery);
      setResults(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Search request failed");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    const timer = setTimeout(() => {
      if (query) {
        performSearch(query);
      } else {
        setResults([]);
      }
    }, 300);

    return () => clearTimeout(timer);
  }, [query, performSearch]);

  return { query, setQuery, results, loading, error, performSearch };
}
