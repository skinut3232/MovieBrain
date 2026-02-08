import { useEffect, useState } from 'react';
import { getTitleProviders } from '../../api/catalog';
import type { WatchProvider } from '../../types';

const TMDB_IMAGE_BASE = 'https://image.tmdb.org/t/p/w92';

interface Props {
  titleId: number;
}

export default function WatchProviders({ titleId }: Props) {
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
        {providers.map((p) => (
          <div
            key={p.provider_id}
            className="flex items-center gap-2 bg-gray-800 rounded-lg px-3 py-1.5"
            title={p.provider_name}
          >
            {p.logo_path && (
              <img
                src={`${TMDB_IMAGE_BASE}${p.logo_path}`}
                alt=""
                className="w-6 h-6 rounded"
              />
            )}
            <span className="text-sm text-gray-300">{p.provider_name}</span>
          </div>
        ))}
      </div>
      <p className="text-xs text-gray-600 mt-2">
        Streaming data powered by JustWatch via TMDB
      </p>
    </div>
  );
}
