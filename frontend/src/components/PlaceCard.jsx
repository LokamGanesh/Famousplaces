import React from 'react';
import { MapPin, Star, Building2, Landmark, Info } from 'lucide-react';

const PlaceCard = ({ place, index }) => {
  const isOverpassData = place.tourism_type !== undefined;
  
  const getIcon = () => {
    if (isOverpassData) {
      return <Landmark className="w-6 h-6 text-secondary-500" />;
    }
    if (place.type?.toLowerCase().includes('historical')) {
      return <Landmark className="w-6 h-6 text-amber-500" />;
    }
    if (place.type?.toLowerCase().includes('religious') || place.type?.toLowerCase().includes('temple')) {
      return <Building2 className="w-6 h-6 text-purple-500" />;
    }
    return <MapPin className="w-6 h-6 text-primary-500" />;
  };

  const getRatingColor = (rating) => {
    if (!rating) return 'text-gray-400';
    if (rating >= 4.5) return 'text-green-500';
    if (rating >= 4.0) return 'text-blue-500';
    if (rating >= 3.0) return 'text-yellow-500';
    return 'text-red-500';
  };

  return (
    <div 
      className="glass-card rounded-2xl p-6 shadow-lg hover:shadow-2xl
                 transition-all duration-300 transform hover:-translate-y-1
                 animate-slide-up"
      style={{ animationDelay: `${index * 100}ms` }}
    >
      <div className="flex items-start gap-4">
        <div className="flex-shrink-0 p-3 bg-gray-50 rounded-xl">
          {getIcon()}
        </div>
        
        <div className="flex-1 min-w-0">
          <h3 className="text-lg font-bold text-gray-900 mb-1 truncate">
            {place.name}
          </h3>
          
          <div className="flex flex-wrap items-center gap-2 mb-3">
            {!isOverpassData && place.city && (
              <span className="inline-flex items-center gap-1 px-3 py-1 
                             bg-primary-50 text-primary-700 text-sm rounded-full">
                <MapPin className="w-3 h-3" />
                {place.city}
              </span>
            )}
            
            {!isOverpassData && place.type && (
              <span className="inline-flex items-center gap-1 px-3 py-1
                             bg-gray-100 text-gray-700 text-sm rounded-full">
                {place.type}
              </span>
            )}
            
            {isOverpassData && place.tourism_type && (
              <span className="inline-flex items-center gap-1 px-3 py-1
                             bg-secondary-50 text-secondary-700 text-sm rounded-full capitalize">
                <Landmark className="w-3 h-3" />
                {place.tourism_type}
              </span>
            )}
          </div>
          
          {!isOverpassData && place.rating !== null && place.rating !== undefined && (
            <div className="flex items-center gap-2">
              <div className="flex items-center gap-1">
                <Star className={`w-4 h-4 fill-current ${getRatingColor(place.rating)}`} />
                <span className={`font-semibold ${getRatingColor(place.rating)}`}>
                  {place.rating.toFixed(1)}
                </span>
              </div>
              <span className="text-gray-400 text-sm">Google Rating</span>
            </div>
          )}
          
          {!isOverpassData && place.significance && (
            <div className="flex items-center gap-2 mt-2 text-sm text-gray-600">
              <Info className="w-4 h-4" />
              <span>{place.significance}</span>
            </div>
          )}
          
          {isOverpassData && place.latitude && place.longitude && (
            <div className="flex items-center gap-2 mt-2 text-sm text-gray-500">
              <MapPin className="w-4 h-4" />
              <span>{place.latitude.toFixed(4)}, {place.longitude.toFixed(4)}</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default PlaceCard;
