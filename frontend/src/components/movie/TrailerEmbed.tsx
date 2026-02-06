interface Props {
  trailerKey: string;
  title: string;
}

export default function TrailerEmbed({ trailerKey, title }: Props) {
  return (
    <div className="mt-6">
      <h2 className="text-lg font-semibold text-gray-200 mb-3">Trailer</h2>
      <div className="relative pb-[56.25%] h-0 rounded-lg overflow-hidden bg-gray-800">
        <iframe
          src={`https://www.youtube.com/embed/${trailerKey}`}
          title={`${title} Trailer`}
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
          allowFullScreen
          className="absolute top-0 left-0 w-full h-full"
        />
      </div>
    </div>
  );
}
