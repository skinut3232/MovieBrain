import { useRef, useState } from 'react';
import { Link } from 'react-router-dom';
import type { FeaturedRowMovie } from '../../types';

interface Props {
  title: string;
  movies: FeaturedRowMovie[];
  seeAllLink?: string;
}

export default function MovieRow({ title, movies, seeAllLink }: Props) {
  const scrollRef = useRef<HTMLDivElement>(null);
  const [showLeftArrow, setShowLeftArrow] = useState(false);
  const [showRightArrow, setShowRightArrow] = useState(true);

  const scroll = (direction: 'left' | 'right') => {
    if (!scrollRef.current) return;
    const scrollAmount = scrollRef.current.clientWidth * 0.8;
    scrollRef.current.scrollBy({
      left: direction === 'left' ? -scrollAmount : scrollAmount,
      behavior: 'smooth',
    });
  };

  const handleScroll = () => {
    if (!scrollRef.current) return;
    const { scrollLeft, scrollWidth, clientWidth } = scrollRef.current;
    setShowLeftArrow(scrollLeft > 0);
    setShowRightArrow(scrollLeft + clientWidth < scrollWidth - 10);
  };

  if (movies.length === 0) return null;

  return (
    <div className="mb-8">
      <div className="flex items-center justify-between mb-3">
        <h2 className="text-lg font-semibold text-gray-200">{title}</h2>
        {seeAllLink && (
          <Link
            to={seeAllLink}
            className="text-sm text-amber-400 hover:text-amber-300"
          >
            See All &rarr;
          </Link>
        )}
      </div>

      <div className="relative group">
        {/* Left Arrow */}
        {showLeftArrow && (
          <button
            onClick={() => scroll('left')}
            className="absolute left-0 top-1/2 -translate-y-1/2 z-10 w-10 h-full bg-gradient-to-r from-gray-900 to-transparent opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-start pl-1"
            aria-label="Scroll left"
          >
            <svg
              className="w-6 h-6 text-white"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M15 19l-7-7 7-7"
              />
            </svg>
          </button>
        )}

        {/* Right Arrow */}
        {showRightArrow && (
          <button
            onClick={() => scroll('right')}
            className="absolute right-0 top-1/2 -translate-y-1/2 z-10 w-10 h-full bg-gradient-to-l from-gray-900 to-transparent opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-end pr-1"
            aria-label="Scroll right"
          >
            <svg
              className="w-6 h-6 text-white"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 5l7 7-7 7"
              />
            </svg>
          </button>
        )}

        {/* Movie Row */}
        <div
          ref={scrollRef}
          onScroll={handleScroll}
          className="flex gap-3 overflow-x-auto scrollbar-hide scroll-smooth"
          style={{ scrollbarWidth: 'none', msOverflowStyle: 'none' }}
        >
          {movies.map((movie) => (
            <Link
              key={movie.id}
              to={`/movie/${movie.id}`}
              className="flex-shrink-0 w-[calc(100%/3-8px)] sm:w-[calc(100%/4-9px)] md:w-[calc(100%/5-10px)] lg:w-[calc(100%/6-10px)] group/poster"
            >
              <div className="relative transition-transform duration-200 group-hover/poster:scale-105">
                {movie.poster_url ? (
                  <img
                    src={movie.poster_url}
                    alt={movie.primary_title}
                    className="w-full aspect-[2/3] object-cover rounded"
                    loading="lazy"
                  />
                ) : (
                  <div className="w-full aspect-[2/3] bg-gray-700 rounded flex items-center justify-center">
                    <span className="text-gray-500 text-xs text-center px-2">
                      {movie.primary_title.length > 20
                        ? movie.primary_title.slice(0, 18) + '...'
                        : movie.primary_title}
                    </span>
                  </div>
                )}
                {/* Rating Badge */}
                {movie.average_rating && (
                  <div className="absolute top-2 right-2 bg-black/80 text-amber-400 text-xs font-semibold px-1.5 py-0.5 rounded">
                    {movie.average_rating.toFixed(1)}
                  </div>
                )}
              </div>
              <div className="mt-2">
                <h3 className="text-sm font-medium text-gray-300 group-hover/poster:text-white truncate">
                  {movie.primary_title}
                </h3>
                <p className="text-xs text-gray-500">
                  {movie.start_year || 'Unknown year'}
                </p>
              </div>
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
}
