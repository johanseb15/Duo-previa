import React from 'react';

const MenuCategories = ({ activeCategory, setActiveCategory }) => {
  const categories = [
    { id: 'all', name: 'Todo', icon: '️', color: 'bg-gray-100 text-gray-700' },
    { id: 'lomitos', name: 'Lomitos', icon: '', color: 'bg-orange-100 text-orange-700' },
    { id: 'hamburgers', name: 'Hamburguesas', icon: '', color: 'bg-red-100 text-red-700' },
    { id: 'empanadas', name: 'Empanadas', icon: '', color: 'bg-yellow-100 text-yellow-700' }
  ];

  return (
    <div className="mb-8">
      <h3 className="text-xl font-semibold text-gray-800 mb-4 text-center">
        ¿Qué te provoca hoy?
      </h3>
      <div className="flex overflow-x-auto pb-2 space-x-4 px-4">
        {categories.map(category => (
          <button
            key={category.id}
            onClick={() => setActiveCategory(category.id)}
            className={`flex flex-col items-center p-4 rounded-xl whitespace-nowrap transition-all duration-200 min-w-[100px] ${
              activeCategory === category.id
                ? 'bg-red-600 text-white shadow-lg transform scale-105'
                : `${category.color} hover:shadow-md hover:scale-102`
            }`}
          >
            <span className="text-2xl mb-2">{category.icon}</span>
            <span className="font-medium text-sm">{category.name}</span>
          </button>
        ))}
      </div>
    </div>
  );
};

export default MenuCategories;
