import { create } from 'zustand';

interface Product {
  id: string;
  name: string;
  price: number;
  quantity?: number;
  image: string;
  description: string;
  rating: number;
  popular?: boolean;
  categoryId?: string;
  sizes?: any[];
  toppings?: any[];
}

interface AppState {
  cart: Product[];
  favorites: string[];
  addToCart: (product: Product, quantity: number) => void;
  toggleFavorite: (id: string) => void;
  setCart: (cart: Product[]) => void;
}

export const useAppStore = create<AppState>((set, get) => ({
  cart: [],
  favorites: [],
  addToCart: (product, quantity) => {
    const existing = get().cart.find(p => p.id === product.id);
    if (existing) {
      set({
        cart: get().cart.map(p =>
          p.id === product.id ? { ...p, quantity: (p.quantity || 1) + quantity } : p
        ),
      });
    } else {
      set({ cart: [...get().cart, { ...product, quantity }] });
    }
  },
  toggleFavorite: (id) => {
    const isFav = get().favorites.includes(id);
    set({
      favorites: isFav
        ? get().favorites.filter(f => f !== id)
        : [...get().favorites, id],
    });
  },
  setCart: (cart) => set({ cart }),
}));
