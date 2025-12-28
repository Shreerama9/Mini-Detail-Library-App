import { useState } from 'react';
import { suggestDetail } from '../services/api';

export default function SuggestForm() {
  const [hostElement, setHostElement] = useState('');
  const [adjacentElement, setAdjacentElement] = useState('');
  const [exposure, setExposure] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    try {
      const data = await suggestDetail({
        host_element: hostElement,
        adjacent_element: adjacentElement,
        exposure: exposure
      });
      setResult(data);
    } catch (err) {
      setError('Failed to get suggestion. Make sure the backend is running.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-xl font-semibold text-gray-800 mb-4">Get Detail Suggestions</h2>
      <p className="text-gray-600 text-sm mb-4">Provide your drawing context to get AI-powered recommendations</p>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Host Element</label>
          <select
            value={hostElement}
            onChange={(e) => setHostElement(e.target.value)}
            required
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="">-- Select Host Element --</option>
            <option value="External Wall">External Wall</option>
            <option value="Internal Wall">Internal Wall</option>
            <option value="Window">Window</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Adjacent Element</label>
          <select
            value={adjacentElement}
            onChange={(e) => setAdjacentElement(e.target.value)}
            required
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="">-- Select Adjacent Element --</option>
            <option value="Slab">Slab</option>
            <option value="Floor">Floor</option>
            <option value="External Wall">External Wall</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Exposure</label>
          <select
            value={exposure}
            onChange={(e) => setExposure(e.target.value)}
            required
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="">-- Select Exposure --</option>
            <option value="External">External</option>
            <option value="Internal">Internal</option>
          </select>
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:bg-blue-400 transition-colors"
        >
          {loading ? 'Getting Suggestions...' : 'Get Suggestions'}
        </button>
      </form>

      {error && (
        <div className="mt-4 p-3 bg-red-100 text-red-700 rounded-md">
          {error}
        </div>
      )}

      {result && (
        <div className="mt-6">
          <h3 className="font-semibold text-gray-800 mb-2">{result.summary}</h3>
          
          {result.suggestions && result.suggestions.length > 0 ? (
            <div className="space-y-4">
              {result.suggestions.map((suggestion, index) => (
                <div key={suggestion.id} className="p-4 bg-gray-50 rounded-md border border-gray-200">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="inline-flex items-center justify-center w-6 h-6 bg-blue-600 text-white text-sm font-bold rounded-full">
                      {suggestion.rank}
                    </span>
                    <h4 className="font-medium text-blue-600">{suggestion.title}</h4>
                  </div>
                  <span className="inline-block px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded">
                    {suggestion.category}
                  </span>
                  <p className="mt-2 text-gray-600 text-sm">{suggestion.description}</p>
                  <div className="mt-2 flex flex-wrap gap-1">
                    {suggestion.tags.map((tag, i) => (
                      <span key={i} className="px-2 py-0.5 bg-gray-200 text-gray-700 text-xs rounded">
                        {tag}
                      </span>
                    ))}
                  </div>
                  
                  <div className="mt-3 p-3 bg-amber-50 border border-amber-200 rounded-md">
                    <h5 className="font-medium text-amber-800 text-sm mb-1">Why this detail?</h5>
                    <p className="text-amber-700 text-sm whitespace-pre-line">{suggestion.reason}</p>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 italic">No matching details found</p>
          )}
        </div>
      )}
    </div>
  );
}
