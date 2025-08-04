import React from 'react';

const LoadingSpinner = () => (
  <div className="flex flex-col items-center justify-center py-16">
    <div className="relative">
      <div className="w-16 h-16 border-4 border-red-200 border-t-red-600 rounded-full animate-spin"></div>
      <div className="absolute inset-0 flex items-center justify-center">
        <span className="text-2xl"></span>
      </div>
    </div>
    <p className="mt-4 text-gray-600 font-medium">Cargando menú delicioso...</p>
  </div>
);

export default LoadingSpinner;
