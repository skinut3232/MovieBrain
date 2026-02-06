interface Props {
  posterUrl: string | null | undefined;
  title: string;
  size?: 'sm' | 'md' | 'lg';
}

const sizeClasses = {
  sm: 'w-12 h-18',
  md: 'w-20 h-30',
  lg: 'w-48 h-72',
};

export default function MoviePoster({ posterUrl, title, size = 'md' }: Props) {
  if (!posterUrl) {
    return (
      <div
        className={`${sizeClasses[size]} bg-gray-700 rounded flex items-center justify-center shrink-0`}
      >
        <span className="text-gray-500 text-xs text-center px-1 leading-tight">
          {title.length > 20 ? title.slice(0, 18) + '...' : title}
        </span>
      </div>
    );
  }

  return (
    <img
      src={posterUrl}
      alt={`${title} poster`}
      className={`${sizeClasses[size]} object-cover rounded shrink-0`}
      loading="lazy"
    />
  );
}
