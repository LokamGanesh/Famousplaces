import React, { useState } from 'react';
import { Search, MapPin } from 'lucide-react';

const SearchBar = ({ onSearch, isLoading }) => {
  const [city, setCity] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (city.trim()) {
      onSearch(city.trim());
    }
  };

  return (
    <form onSubmit={handleSubmit} className="w-full max-w-2xl mx-auto">
      <div className="relative group">
        <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
          <MapPin className="h-6 w-6 text-gray-400 group-focus-within:text-primary-500 transition-colors" />
        </div>
        
        <input
          type="text"
          value={city}
          onChange={(e) => setCity(e.target.value)}
          placeholder="Enter a city (e.g., Hyderabad, Delhi, Mumbai)..."
          className="w-full pl-12 pr-32 py-4 text-lg rounded-2xl border-2 border-transparent
                     bg-white/90 backdrop-blur-sm shadow-xl
                     focus:outline-none focus:border-primary-400 focus:bg-white
                     placeholder-gray-400 text-gray-800
                     transition-all duration-300"
          disabled={isLoading}
        />
        
        <button
          type="submit"
          disabled={isLoading || !city.trim()}
          className="absolute right-2 top-2 bottom-2 px-6
                     bg-gradient-to-r from-primary-500 to-primary-600
                     hover:from-primary-600 hover:to-primary-700
                     disabled:from-gray-400 disabled:to-gray-500
                     text-white font-semibold rounded-xl
                     flex items-center gap-2
                     transition-all duration-300
                     shadow-lg hover:shadow-xl
                     disabled:cursor-not-allowed"
        >
          {isLoading ? (
            <>
              <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              <span>Searching...</span>
            </>
          ) : (
            <>
              <Search className="w-5 h-5" />
              <span>Search</span>
            </>
          )}
        </button>
      </div>
    </form>
  );
};

export default SearchBar;
