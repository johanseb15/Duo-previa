import React, { useState } from 'react';
import { useAppStore } from '../store/appStore';

const MenuItem = ({ item }) => {
  const addToCart = useAppStore((state) => state.addToCart);
  const [isAdding, setIsAdding] = useState(false);

  const handleAddToCart = async () => {
    setIsAdding(true);
    addToCart(item, 1); // Asumiendo cantidad 1 por defecto
    
    // Visual feedback
    setTimeout(() => setIsAdding(false), 800);
  };

  return (
    <div className="bg-white rounded-2xl shadow-md overflow-hidden hover:shadow-xl transition-all duration-300 hover:-translate-y-1 group">
      <div className="relative overflow-hidden">
        <img
          src={item.image}
          alt={item.name}
          className="w-full h-48 object-cover group-hover:scale-110 transition-transform duration-300"
        />
        {/* {!item.available && (
          <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center">
            <span className="bg-red-600 text-white px-3 py-1 rounded-full text-sm font-medium">
              No disponible
            </span>
          </div>
        )} */}
        <div className="absolute top-3 right-3">
          <div className="bg-white bg-opacity-90 backdrop-blur-sm rounded-full px-3 py-1">
            <span className="text-sm font-semibold text-red-600">
              ${item.price.toLocaleString()}
            </span>
          </div>
        </div>
      </div>
      
      <div className="p-5">
        <h3 className="text-lg font-bold text-gray-800 mb-2 leading-tight">
          {item.name}
        </h3>
        <p className="text-gray-600 text-sm mb-4 line-clamp-2 leading-relaxed">
          {item.description}
        </p>
        
        <div className="flex items-center justify-between">
          <div className="flex flex-col">
            <span className="text-2xl font-bold text-red-600">
              ${item.price.toLocaleString()}
            </span>
            <span className="text-xs text-gray-500">Precio final</span>
          </div>
          
          <button
            onClick={handleAddToCart}
            disabled={isAdding} // Deshabilitar si se está añadiendo
            className={`px-6 py-3 rounded-xl font-semibold transition-all duration-200 flex items-center space-x-2 ${
              isAdding
                ? 'bg-green-600 text-white'
                : 'bg-red-600 hover:bg-red-700 text-white hover:shadow-lg transform hover:scale-105'
            }`}
          >
            {isAdding ? (
              <>
                <span>✓</span>
                <span>¡Agregado!</span>
              </>
            ) : (
              <>
                <span>+</span>
                <span>Agregar</span>
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

export default MenuItem;
