import { Link } from 'react-router-dom';

interface Props {
  genres: string[];
  decades: number[];
  selectedGenre?: string;
  selectedDecade?: number;
}

export default function GenreChips({
  genres,
  decades,
  selectedGenre,
  selectedDecade,
}: Props) {
  return (
    <div className="mb-6">
      {/* Genre Chips */}
      <div className="mb-4">
        <h3 className="text-sm font-medium text-gray-400 mb-2">Genres</h3>
        <div className="flex flex-wrap gap-2">
          {genres.map((genre) => (
            <Link
              key={genre}
              to={`/explore?genres=${genre}`}
              className={`px-3 py-1.5 rounded-full text-sm transition ${
                selectedGenre === genre
                  ? 'bg-amber-500 text-black font-medium'
                  : 'bg-gray-800 text-gray-300 hover:bg-gray-700 hover:text-white'
              }`}
            >
              {genre}
            </Link>
          ))}
        </div>
      </div>

      {/* Decade Chips */}
      <div>
        <h3 className="text-sm font-medium text-gray-400 mb-2">Decades</h3>
        <div className="flex flex-wrap gap-2">
          {decades.map((decade) => (
            <Link
              key={decade}
              to={`/explore?minYear=${decade}&maxYear=${decade + 9}`}
              className={`px-3 py-1.5 rounded-full text-sm transition ${
                selectedDecade === decade
                  ? 'bg-amber-500 text-black font-medium'
                  : 'bg-gray-800 text-gray-300 hover:bg-gray-700 hover:text-white'
              }`}
            >
              {decade}s
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
}
