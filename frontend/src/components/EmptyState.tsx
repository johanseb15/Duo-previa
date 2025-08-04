import React from 'react';

const EmptyState = ({ category }) => (
  <div className="text-center py-16">
    <div className="text-6xl mb-4"></div>
    <h3 className="text-xl font-semibold text-gray-800 mb-2">
      No hay productos en {category === 'all' ? 'el menú' : category}
    </h3>
    <p className="text-gray-600 mb-6">
      Pero no te preocupes, pronto tendremos más opciones deliciosas.
    </p>
    <button
      onClick={() => window.location.reload()}
      className="bg-red-600 hover:bg-red-700 text-white px-6 py-3 rounded-lg transition-colors"
    >
      Recargar menú
    </button>
  </div>
);

export default EmptyState;
