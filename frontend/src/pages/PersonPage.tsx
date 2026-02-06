import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { getPersonWithFilmography } from '../api/catalog';
import MoviePoster from '../components/common/MoviePoster';
import type { FilmographyItem, PersonDetail } from '../types';

export default function PersonPage() {
  const { personId } = useParams<{ personId: string }>();
  const [person, setPerson] = useState<PersonDetail | null>(null);
  const [filmography, setFilmography] = useState<FilmographyItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!personId) return;
    setLoading(true);
    getPersonWithFilmography(Number(personId))
      .then((data) => {
        setPerson(data.person);
        setFilmography(data.filmography);
      })
      .catch(() => setError('Person not found'))
      .finally(() => setLoading(false));
  }, [personId]);

  if (loading) return <p className="text-gray-400">Loading...</p>;
  if (error) return <p className="text-red-400">{error}</p>;
  if (!person) return null;

  // Group filmography by category
  const grouped = filmography.reduce<Record<string, FilmographyItem[]>>((acc, item) => {
    const cat = item.category || 'Other';
    if (!acc[cat]) acc[cat] = [];
    acc[cat].push(item);
    return acc;
  }, {});

  // Sort categories: actor/actress first, then director, then others
  const categoryOrder = ['actor', 'actress', 'director', 'writer', 'producer'];
  const sortedCategories = Object.keys(grouped).sort((a, b) => {
    const aIdx = categoryOrder.indexOf(a.toLowerCase());
    const bIdx = categoryOrder.indexOf(b.toLowerCase());
    if (aIdx === -1 && bIdx === -1) return a.localeCompare(b);
    if (aIdx === -1) return 1;
    if (bIdx === -1) return -1;
    return aIdx - bIdx;
  });

  const formatCategory = (cat: string) => {
    if (cat === 'actor' || cat === 'actress') return 'Acting';
    return cat.charAt(0).toUpperCase() + cat.slice(1);
  };

  return (
    <div className="max-w-4xl mx-auto">
      {/* Person Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">{person.primary_name}</h1>
        <div className="text-gray-400 text-sm flex items-center gap-4">
          {person.birth_year && (
            <span>
              Born {person.birth_year}
              {person.death_year && ` - Died ${person.death_year}`}
            </span>
          )}
          <span className="text-gray-600">
            {filmography.length} credits
          </span>
        </div>
      </div>

      {/* Filmography by Category */}
      {sortedCategories.map((category) => {
        const items = grouped[category];
        // Merge actor/actress into one "Acting" section
        const displayCategory = formatCategory(category);

        return (
          <div key={category} className="mb-8">
            <h2 className="text-lg font-semibold text-gray-200 mb-4">
              {displayCategory}
              <span className="text-gray-500 font-normal ml-2">({items.length})</span>
            </h2>
            <div className="space-y-3">
              {items.map((item, idx) => (
                <Link
                  key={`${item.title_id}-${idx}`}
                  to={`/movie/${item.title_id}`}
                  className="flex items-center gap-4 p-3 bg-gray-800/50 rounded-lg hover:bg-gray-800 transition group"
                >
                  <div className="w-12 flex-shrink-0">
                    <MoviePoster
                      posterUrl={item.poster_url}
                      title={item.primary_title}
                      size="sm"
                    />
                  </div>
                  <div className="flex-1 min-w-0">
                    <h3 className="text-gray-200 font-medium group-hover:text-white truncate">
                      {item.primary_title}
                    </h3>
                    <div className="text-sm text-gray-400 flex items-center gap-2">
                      {item.start_year && <span>{item.start_year}</span>}
                      {item.characters && (
                        <span className="text-gray-500">
                          as {item.characters.replace(/[\[\]"]/g, '')}
                        </span>
                      )}
                    </div>
                  </div>
                  {item.average_rating && (
                    <div className="text-amber-400 font-semibold text-sm">
                      {item.average_rating.toFixed(1)}
                    </div>
                  )}
                </Link>
              ))}
            </div>
          </div>
        );
      })}
    </div>
  );
}
