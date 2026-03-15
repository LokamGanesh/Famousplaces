import React, { useState } from 'react';
import { MapPin, Compass, Sparkles, AlertCircle } from 'lucide-react';
import SearchBar from './components/SearchBar';
import PlaceCard from './components/PlaceCard';
import { fetchRecommendations } from './api';

function App() {
  const [results, setResults] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [searchedCity, setSearchedCity] = useState('');

  const handleSearch = async (city) => {
    setIsLoading(true);
    setError(null);
    setSearchedCity(city);
    setResults(null);

    try {
      const data = await fetchRecommendations(city);
      setResults(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const getSourceLabel = (source) => {
    if (source === 'ml_model') {
      return (
        <span className="inline-flex items-center gap-1 px-3 py-1 bg-green-100 text-green-700 text-sm rounded-full">
          <Sparkles className="w-4 h-4" />
          AI Powered
        </span>
      );
    }
    return (
      <span className="inline-flex items-center gap-1 px-3 py-1 bg-blue-100 text-blue-700 text-sm rounded-full">
        <Compass className="w-4 h-4" />
        Live Data
      </span>
    );
  };

  return (
    <div className="min-h-screen py-8 px-4 sm:px-6 lg:px-8">
      {/* Header */}
      <div className="text-center mb-12 animate-fade-in">
        <div className="inline-flex items-center justify-center p-3 bg-white/20 rounded-2xl mb-4">
          <MapPin className="w-8 h-8 text-white" />
        </div>
        <h1 className="text-4xl sm:text-5xl font-bold text-white mb-4">
          AI Tourism Recommendation
        </h1>
        <p className="text-lg text-white/80 max-w-2xl mx-auto">
          Discover amazing tourist destinations powered by Machine Learning. 
          Enter any city to get personalized recommendations.
        </p>
      </div>

      {/* Search Section */}
      <div className="mb-8">
        <SearchBar onSearch={handleSearch} isLoading={isLoading} />
      </div>

      {/* Error Message */}
      {error && (
        <div className="max-w-2xl mx-auto mb-8 animate-slide-up">
          <div className="bg-red-50 border-l-4 border-red-500 p-4 rounded-r-lg flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
            <div>
              <h3 className="text-red-800 font-semibold">Error</h3>
              <p className="text-red-700">{error}</p>
            </div>
          </div>
        </div>
      )}

      {/* Results Section */}
      {results && !error && (
        <div className="max-w-6xl mx-auto animate-fade-in">
          {/* Results Header */}
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
            <div>
              <h2 className="text-2xl font-bold text-white">
                Places in {results.city}
              </h2>
              <p className="text-white/70">
                Found {results.count} amazing destinations
              </p>
            </div>
            <div>
              {getSourceLabel(results.source)}
            </div>
          </div>

          {/* Places Grid */}
          {results.places && results.places.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {results.places.map((place, index) => (
                <PlaceCard key={index} place={place} index={index} />
              ))}
            </div>
          ) : (
            <div className="text-center py-12">
              <div className="inline-flex items-center justify-center p-4 bg-white/10 rounded-full mb-4">
                <Compass className="w-8 h-8 text-white/60" />
              </div>
              <p className="text-white/80 text-lg">
                No places found for this city.
              </p>
              <p className="text-white/60 mt-2">
                Try searching for a different city.
              </p>
            </div>
          )}
        </div>
      )}

      {/* Empty State */}
      {!results && !isLoading && !error && (
        <div className="max-w-2xl mx-auto text-center py-16 animate-fade-in">
          <div className="glass rounded-2xl p-8">
            <div className="inline-flex items-center justify-center p-4 bg-white/10 rounded-full mb-6">
              <Compass className="w-12 h-12 text-white/80" />
            </div>
            <h3 className="text-xl font-semibold text-white mb-2">
              Ready to Explore?
            </h3>
            <p className="text-white/70">
              Enter a city name above to discover tourist attractions. 
              Try cities like Hyderabad, Delhi, Mumbai, or Jaipur!
            </p>
          </div>
        </div>
      )}

      {/* Loading State */}
      {isLoading && (
        <div className="max-w-2xl mx-auto text-center py-16">
          <div className="inline-flex items-center justify-center p-4 bg-white/10 rounded-full mb-4 animate-pulse-slow">
            <Sparkles className="w-10 h-10 text-white/80 animate-spin-slow" />
          </div>
          <p className="text-white/80 text-lg">
            Discovering amazing places in {searchedCity}...
          </p>
        </div>
      )}

      {/* Footer */}
      <footer className="mt-16 text-center">
        <p className="text-white/50 text-sm">
          Powered by FastAPI + React • Deployed on Google Cloud Run
        </p>
      </footer>
    </div>
  );
}

export default App;
