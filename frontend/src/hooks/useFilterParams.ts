import { useCallback, useMemo } from 'react';
import { useSearchParams } from 'react-router-dom';
import type { SortOption } from '../types';

export interface FilterState {
  genres: string[];
  minYear?: number;
  maxYear?: number;
  minRating?: number;
  minRtScore?: number;
  minRuntime?: number;
  maxRuntime?: number;
  language?: string;
  sort: SortOption;
  hideWatched: boolean;
  browseAll: boolean;
  providerIds: number[];
}

export type FilterUpdates = Partial<Omit<FilterState, 'browseAll'>>;

export function useFilterParams() {
  const [searchParams, setSearchParams] = useSearchParams();

  const filters = useMemo<FilterState>(() => {
    // Read genres — support both new "genres" (comma-sep) and legacy "genre" (single)
    const genresParam = searchParams.get('genres');
    const legacyGenre = searchParams.get('genre');
    let genres: string[] = [];
    if (genresParam) {
      genres = genresParam.split(',').filter(Boolean);
    } else if (legacyGenre) {
      genres = [legacyGenre];
    }

    // Read year — support legacy "decade" param
    const decadeParam = searchParams.get('decade');
    let minYear = searchParams.get('minYear') ? Number(searchParams.get('minYear')) : undefined;
    let maxYear = searchParams.get('maxYear') ? Number(searchParams.get('maxYear')) : undefined;
    if (decadeParam && !minYear && !maxYear) {
      const decade = Number(decadeParam);
      minYear = decade;
      maxYear = decade + 9;
    }

    const minRatingParam = searchParams.get('minRating');
    const minRtScoreParam = searchParams.get('minRtScore');
    const minRuntimeParam = searchParams.get('minRuntime');
    const maxRuntimeParam = searchParams.get('maxRuntime');

    const providerIdsParam = searchParams.get('providerIds');
    const providerIds = providerIdsParam
      ? providerIdsParam.split(',').map(Number).filter(n => !isNaN(n))
      : [];

    return {
      genres,
      minYear,
      maxYear,
      minRating: minRatingParam ? Number(minRatingParam) : undefined,
      minRtScore: minRtScoreParam ? Number(minRtScoreParam) : undefined,
      minRuntime: minRuntimeParam ? Number(minRuntimeParam) : undefined,
      maxRuntime: maxRuntimeParam ? Number(maxRuntimeParam) : undefined,
      language: searchParams.get('language') || undefined,
      sort: (searchParams.get('sort') as SortOption) || 'popularity',
      hideWatched: searchParams.get('hideWatched') === 'true',
      browseAll: searchParams.get('browse') === 'all',
      providerIds,
    };
  }, [searchParams]);

  const setFilters = useCallback(
    (updates: FilterUpdates) => {
      const params = new URLSearchParams(searchParams);

      // Remove legacy params on any update
      params.delete('genre');
      params.delete('decade');

      if ('genres' in updates) {
        if (updates.genres?.length) {
          params.set('genres', updates.genres.join(','));
        } else {
          params.delete('genres');
        }
      }

      if ('minYear' in updates) {
        if (updates.minYear != null) params.set('minYear', String(updates.minYear));
        else params.delete('minYear');
      }

      if ('maxYear' in updates) {
        if (updates.maxYear != null) params.set('maxYear', String(updates.maxYear));
        else params.delete('maxYear');
      }

      if ('minRating' in updates) {
        if (updates.minRating != null) params.set('minRating', String(updates.minRating));
        else params.delete('minRating');
      }

      if ('minRtScore' in updates) {
        if (updates.minRtScore != null) params.set('minRtScore', String(updates.minRtScore));
        else params.delete('minRtScore');
      }

      if ('minRuntime' in updates) {
        if (updates.minRuntime != null) params.set('minRuntime', String(updates.minRuntime));
        else params.delete('minRuntime');
      }

      if ('maxRuntime' in updates) {
        if (updates.maxRuntime != null) params.set('maxRuntime', String(updates.maxRuntime));
        else params.delete('maxRuntime');
      }

      if ('language' in updates) {
        if (updates.language) params.set('language', updates.language);
        else params.delete('language');
      }

      if ('sort' in updates) {
        if (updates.sort && updates.sort !== 'popularity') params.set('sort', updates.sort);
        else params.delete('sort');
      }

      if ('hideWatched' in updates) {
        if (updates.hideWatched) params.set('hideWatched', 'true');
        else params.delete('hideWatched');
      }

      if ('providerIds' in updates) {
        if (updates.providerIds?.length) params.set('providerIds', updates.providerIds.join(','));
        else params.delete('providerIds');
      }

      setSearchParams(params, { replace: true });
    },
    [searchParams, setSearchParams]
  );

  const clearAllFilters = useCallback(() => {
    setSearchParams({}, { replace: true });
  }, [setSearchParams]);

  const isFilteredMode = useMemo(() => {
    return (
      filters.browseAll ||
      filters.genres.length > 0 ||
      filters.minYear != null ||
      filters.maxYear != null ||
      filters.minRating != null ||
      filters.minRtScore != null ||
      filters.minRuntime != null ||
      filters.maxRuntime != null ||
      filters.language != null ||
      filters.providerIds.length > 0
    );
  }, [filters]);

  const activeFilterCount = useMemo(() => {
    let count = 0;
    if (filters.genres.length > 0) count++;
    if (filters.minYear != null || filters.maxYear != null) count++;
    if (filters.minRating != null) count++;
    if (filters.minRtScore != null) count++;
    if (filters.minRuntime != null || filters.maxRuntime != null) count++;
    if (filters.language != null) count++;
    if (filters.providerIds.length > 0) count++;
    return count;
  }, [filters]);

  return { filters, setFilters, clearAllFilters, isFilteredMode, activeFilterCount };
}
