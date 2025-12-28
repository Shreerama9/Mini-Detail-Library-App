import { useState, useEffect, useRef } from 'react';
import { fetchDetails, searchDetails, autocomplete } from '../services/api';

export default function DetailsList() {
  const [details, setDetails] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [suggestions, setSuggestions] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const inputRef = useRef(null);

  useEffect(() => {
    loadDetails();
  }, []);

  // Autocomplete effect - triggers on query change
  useEffect(() => {
    if (searchQuery.length >= 2) {
      const timer = setTimeout(async () => {
        const data = await autocomplete(searchQuery);
        setSuggestions(data.suggestions || []);
        setShowSuggestions(true);
      }, 300); // Debounce 300ms
      return () => clearTimeout(timer);
    } else {
      setSuggestions([]);
      setShowSuggestions(false);
    }
  }, [searchQuery]);

  const loadDetails = async () => {
    setLoading(true);
    setError('');
    try {
      const data = await fetchDetails();
      setDetails(data);
    } catch (err) {
      setError('Failed to load details. Make sure the backend is running.');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    setShowSuggestions(false);
    if (!searchQuery.trim()) {
      loadDetails();
      return;
    }
    
    setLoading(true);
    setError('');
    try {
      const data = await searchDetails(searchQuery);
      setDetails(data);
    } catch (err) {
      setError('Search failed. Try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleSuggestionClick = (suggestion) => {
    setSearchQuery(suggestion);
    setShowSuggestions(false);
    // Trigger search with the selected suggestion
    searchDetails(suggestion).then(data => setDetails(data));
  };

  const handleClear = () => {
    setSearchQuery('');
    setSuggestions([]);
    setShowSuggestions(false);
    loadDetails();
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-xl font-semibold text-gray-800 mb-4">All Details</h2>
      
      <form onSubmit={handleSearch} className="flex gap-2 mb-4 relative">
        <div className="flex-1 relative">
          <input
            ref={inputRef}
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onFocus={() => suggestions.length > 0 && setShowSuggestions(true)}
            onBlur={() => setTimeout(() => setShowSuggestions(false), 200)}
            placeholder="Search by title, tags, or description..."
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
          
          {/* Autocomplete dropdown */}
          {showSuggestions && suggestions.length > 0 && (
            <div className="absolute top-full left-0 right-0 mt-1 bg-white border border-gray-300 rounded-md shadow-lg z-10 max-h-48 overflow-y-auto">
              {suggestions.map((suggestion, index) => (
                <div
                  key={index}
                  onMouseDown={() => handleSuggestionClick(suggestion)}
                  className="px-3 py-2 hover:bg-blue-50 cursor-pointer text-gray-700"
                >
                  {suggestion}
                </div>
              ))}
            </div>
          )}
        </div>
        <button
          type="submit"
          className="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 transition-colors"
        >
          Search
        </button>
        <button
          type="button"
          onClick={handleClear}
          className="px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 transition-colors"
        >
          Clear
        </button>
      </form>

      {error && (
        <div className="mb-4 p-3 bg-red-100 text-red-700 rounded-md">
          {error}
        </div>
      )}

      {loading ? (
        <div className="text-center py-8 text-gray-500">Loading details...</div>
      ) : details.length === 0 ? (
        <div className="text-center py-8 text-gray-500">No details found</div>
      ) : (
        <div className="space-y-3">
          {details.map((detail) => (
            <div key={detail.id} className="p-4 border border-gray-200 rounded-md hover:border-blue-300 transition-colors">
              <div className="flex items-start justify-between">
                <h3 className="font-medium text-gray-800">{detail.title}</h3>
                <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded">
                  {detail.category}
                </span>
              </div>
              <p className="mt-1 text-gray-600 text-sm">{detail.description}</p>
              <div className="mt-2 flex flex-wrap gap-1">
                {detail.tags.map((tag, i) => (
                  <span key={i} className="px-2 py-0.5 bg-gray-100 text-gray-600 text-xs rounded">
                    {tag}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
