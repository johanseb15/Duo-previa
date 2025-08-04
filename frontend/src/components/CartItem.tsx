import React from 'react';
import { useAppStore } from '../store/appStore';

const CartItem = ({ item }) => {
  const setCart = useAppStore((state) => state.setCart);
  const cart = useAppStore((state) => state.cart);

  const updateQuantity = (id: string, newQuantity: number) => {
    if (newQuantity <= 0) {
      setCart(cart.filter(cartItem => cartItem.id !== id));
    } else {
      setCart(cart.map(cartItem => cartItem.id === id ? { ...cartItem, quantity: newQuantity } : cartItem));
    }
  };

  const removeFromCart = (id: string) => {
    setCart(cart.filter(cartItem => cartItem.id !== id));
  };

  return (
    <div className="flex items-center justify-between bg-gray-50 p-4 rounded-xl border border-gray-100">
      <div className="flex-1">
        <h3 className="font-semibold text-gray-800">{item.name}</h3>
        <p className="text-gray-600 text-sm">${item.price.toLocaleString()} c/u</p>
      </div>
      
      <div className="flex items-center space-x-3">
        <div className="flex items-center space-x-2 bg-white rounded-lg border border-gray-200 p-1">
          <button
            onClick={() => updateQuantity(item.id, (item.quantity || 1) - 1)}
            className="bg-gray-100 hover:bg-red-100 text-gray-700 hover:text-red-600 w-8 h-8 rounded-md flex items-center justify-center transition-colors"
          >
            -
          </button>
          <span className="font-semibold px-3 min-w-[40px] text-center">
            {item.quantity || 1}
          </span>
          <button
            onClick={() => updateQuantity(item.id, (item.quantity || 1) + 1)}
            className="bg-red-100 hover:bg-red-200 text-red-600 hover:text-red-700 w-8 h-8 rounded-md flex items-center justify-center transition-colors"
          >
            +
          </button>
        </div>
        
        <div className="flex flex-col items-end">
          <span className="font-bold text-red-600 text-lg">
            ${((item.price || 0) * (item.quantity || 1)).toLocaleString()}
          </span>
          <button
            onClick={() => removeFromCart(item.id)}
            className="text-gray-400 hover:text-red-500 transition-colors text-sm mt-1"
            title="Eliminar producto"
          >
            ️ Quitar
          </button>
        </div>
      </div>
    </div>
  );
};

export default CartItem;
