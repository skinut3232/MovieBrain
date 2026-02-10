import { useState } from 'react';

const MOOD_PRESETS = [
  'Feel-good',
  'Mind-bending',
  'Edge of my seat',
  'Nostalgic',
  'Dark & gritty',
  'Hidden gems',
  'Lighthearted comedy',
  'Epic adventure',
];

interface MoodInputProps {
  onSearch: (mood: string) => void;
  onClear: () => void;
  loading: boolean;
}

export default function MoodInput({ onSearch, onClear, loading }: MoodInputProps) {
  const [text, setText] = useState('');
  const [selectedPresets, setSelectedPresets] = useState<Set<string>>(new Set());

  const hasInput = selectedPresets.size > 0 || text.trim().length > 0;

  const buildMoodString = (): string => {
    const parts: string[] = [];
    if (selectedPresets.size > 0) {
      parts.push(Array.from(selectedPresets).join(', '));
    }
    if (text.trim()) {
      parts.push(text.trim());
    }
    return parts.join('. ');
  };

  const handleTogglePreset = (preset: string) => {
    setSelectedPresets((prev) => {
      const next = new Set(prev);
      if (next.has(preset)) {
        next.delete(preset);
      } else {
        next.add(preset);
      }
      return next;
    });
  };

  const handleSearch = () => {
    const mood = buildMoodString();
    if (mood) onSearch(mood);
  };

  const handleClear = () => {
    setText('');
    setSelectedPresets(new Set());
    onClear();
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSearch();
    }
  };

  return (
    <div className="bg-gray-900 rounded-lg border border-gray-700 p-4 mb-4">
      <h2 className="text-lg font-semibold text-white mb-3">
        What are you in the mood for?
      </h2>

      <div className="flex flex-wrap gap-2 mb-3">
        {MOOD_PRESETS.map((preset) => {
          const isSelected = selectedPresets.has(preset);
          return (
            <button
              key={preset}
              onClick={() => handleTogglePreset(preset)}
              className={`px-3 py-1.5 rounded-full text-sm border transition-colors ${
                isSelected
                  ? 'border-amber-400 bg-amber-400/15 text-amber-400'
                  : 'border-gray-600 text-gray-300 hover:border-amber-400 hover:text-amber-400'
              }`}
            >
              {preset}
            </button>
          );
        })}
      </div>

      <textarea
        value={text}
        onChange={(e) => setText(e.target.value.slice(0, 500))}
        onKeyDown={handleKeyDown}
        placeholder="Add more detail... (optional)"
        rows={2}
        className="w-full bg-gray-800 border border-gray-600 rounded px-3 py-2 text-white placeholder-gray-500 focus:outline-none focus:border-amber-400 resize-none"
      />

      <div className="flex items-center justify-between mt-2">
        <span className="text-xs text-gray-500">{text.length}/500</span>
        <div className="flex items-center gap-3">
          {hasInput && (
            <button
              onClick={handleClear}
              disabled={loading}
              className="text-sm text-gray-400 hover:text-white disabled:opacity-50"
            >
              Clear
            </button>
          )}
          <button
            onClick={handleSearch}
            disabled={loading || !hasInput}
            className="px-4 py-2 rounded bg-amber-500 hover:bg-amber-600 text-black font-semibold text-sm disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Searching...' : 'Search'}
          </button>
        </div>
      </div>
    </div>
  );
}
