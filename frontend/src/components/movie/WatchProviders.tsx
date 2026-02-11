import { useEffect, useState } from 'react';
import { getTitleProviders } from '../../api/catalog';
import type { WatchProvider } from '../../types';

const TMDB_IMAGE_BASE = 'https://image.tmdb.org/t/p/w92';

const PROVIDER_SEARCH_URLS: Record<number, (title: string) => string> = {
  8: (t) => `https://www.netflix.com/search?q=${encodeURIComponent(t)}`,
  9: (t) => `https://www.amazon.com/s?k=${encodeURIComponent(t)}&i=instant-video`,
  119: (t) => `https://www.amazon.com/s?k=${encodeURIComponent(t)}&i=instant-video`,
  337: (t) => `https://www.disneyplus.com/search/${encodeURIComponent(t)}`,
  15: (t) => `https://www.hulu.com/search?q=${encodeURIComponent(t)}`,
  1899: (t) => `https://play.max.com/search?q=${encodeURIComponent(t)}`,
  384: (t) => `https://play.max.com/search?q=${encodeURIComponent(t)}`,
  350: (t) => `https://tv.apple.com/search?term=${encodeURIComponent(t)}`,
  2: (t) => `https://tv.apple.com/search?term=${encodeURIComponent(t)}`,
  531: (t) => `https://www.paramountplus.com/search/?q=${encodeURIComponent(t)}`,
  386: (t) => `https://www.peacocktv.com/search?q=${encodeURIComponent(t)}`,
  387: (t) => `https://www.peacocktv.com/search?q=${encodeURIComponent(t)}`,
  43: (t) => `https://www.starz.com/search?q=${encodeURIComponent(t)}`,
  37: (t) => `https://www.sho.com/search?q=${encodeURIComponent(t)}`,
  73: (t) => `https://tubitv.com/search/${encodeURIComponent(t)}`,
  300: (t) => `https://pluto.tv/search/details/${encodeURIComponent(t)}`,
  283: (t) => `https://www.crunchyroll.com/search?q=${encodeURIComponent(t)}`,
};

function getProviderUrl(providerId: number, movieTitle: string): string | null {
  const fn = PROVIDER_SEARCH_URLS[providerId];
  return fn ? fn(movieTitle) : null;
}

interface Props {
  titleId: number;
  title?: string;
}

export default function WatchProviders({ titleId, title }: Props) {
  const [providers, setProviders] = useState<WatchProvider[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    getTitleProviders(titleId)
      .then((data) => { if (!cancelled) setProviders(data); })
      .catch(() => { /* non-critical */ })
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [titleId]);

  if (loading) return null;
  if (providers.length === 0) return null;

  return (
    <div className="mt-6">
      <h2 className="text-lg font-semibold text-gray-200 mb-3">Where to Stream</h2>
      <div className="flex flex-wrap gap-2">
        {providers.map((p) => {
          const url = title ? getProviderUrl(p.provider_id, title) : null;
          const content = (
            <>
              {p.logo_path && (
                <img
                  src={`${TMDB_IMAGE_BASE}${p.logo_path}`}
                  alt=""
                  className="w-6 h-6 rounded"
                />
              )}
              <span className="text-sm text-gray-300">{p.provider_name}</span>
            </>
          );

          return url ? (
            <a
              key={p.provider_id}
              href={url}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 bg-gray-800 rounded-lg px-3 py-1.5 hover:bg-gray-700 cursor-pointer transition"
              title={`Search ${p.provider_name}`}
            >
              {content}
            </a>
          ) : (
            <div
              key={p.provider_id}
              className="flex items-center gap-2 bg-gray-800 rounded-lg px-3 py-1.5"
              title={p.provider_name}
            >
              {content}
            </div>
          );
        })}
      </div>
      <p className="text-xs text-gray-600 mt-2">
        Streaming data powered by JustWatch via TMDB
      </p>
    </div>
  );
}
