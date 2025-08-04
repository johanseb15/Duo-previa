import React, { useState, useEffect, useMemo, useRef } from 'react';
import { Home, ShoppingCart, User, Search, X, Plus, Minus, Star, ChevronRight, Heart, Share2, ArrowLeft, LoaderCircle } from 'lucide-react';

// --- Framer Motion (Simulación para animaciones suaves) ---
// En un proyecto real: npm install framer-motion
const motion = {
  div: ({ children, initial, animate, exit, whileHover, whileTap, transition, ...props }) => <div {...props}>{children}</div>,
  button: ({ children, initial, animate, exit, whileHover, whileTap, transition, ...props }) => <button {...props}>{children}</button>,
  li: ({ children, initial, animate, exit, whileHover, whileTap, transition, ...props }) => <li {...props}>{children}</li>,
};

// --- Zustand Store Simulation (Estado Global para Carrito y Favoritos) ---
const createStore = (initialState) => {
  let state = initialState;
  const listeners = new Set();
  const setState = (updater) => {
    const newState = typeof updater === 'function' ? updater(state) : updater;
    state = { ...state, ...newState };
    listeners.forEach(listener => listener(state));
  };
  const getState = () => state;
  const subscribe = (listener) => {
    listeners.add(listener);
    return () => listeners.delete(listener);
  };
  return { setState, getState, subscribe };
};

const useStore = (store, selector) => {
  const [localState, setLocalState] = useState(() => selector(store.getState()));
  useEffect(() => {
    const listener = (newState) => setLocalState(selector(newState));
    const unsubscribe = store.subscribe(listener);
    listener(store.getState());
    return unsubscribe;
  }, [store, selector]);
  return localState;
};

const appStore = createStore({
  cart: [],
  favorites: ['p1'], // 'p1' es un producto popular por defecto
});

// --- MOCK DATA (Datos de ejemplo como fallback) ---
const mockRestaurant = {
  name: 'DUO Previa',
  logoUrl: 'https://placehold.co/100x100/dc2626/f9fafb?text=DUO',
  heroImage: 'https://images.unsplash.com/photo-1550547660-d9450f859349?q=80&w=2564&auto=format&fit=crop',
};

const fallbackCategories = [
  { id: 'cat1', name: 'Lomitos', icon: '' },
  { id: 'cat2', name: 'Hamburguesas', icon: '' },
  { id: 'cat3', name: 'Empanadas', icon: '' },
  { id: 'cat4', name: 'Bebidas', icon: '' },
];

const fallbackProducts = [
  { id: 'p1', name: 'Lomito Clásico', description: 'Tierna carne de lomo, lechuga, tomate, huevo y mayonesa de la casa.', price: 15500, image: 'https://placehold.co/600x400/cccccc/333333?text=Lomito', categoryId: 'cat1', popular: true, rating: 4.9 },
  { id: 'p2', name: 'Hamburguesa DUO', description: 'Doble medallón de carne, queso cheddar, panceta crocante, y salsa DUO.', price: 14000, image: 'https://images.unsplash.com/photo-1568901346375-23c9450c58cd?q=80&w=1998&auto=format&fit=crop', categoryId: 'cat2', popular: true, rating: 4.8 },
  { id: 'p3', name: 'Empanada de Carne', description: 'Jugosa carne cortada a cuchillo, con la receta tradicional cordobesa.', price: 1800, image: 'https://images.unsplash.com/photo-1628323283129-3f4942995f49?q=80&w=2070&auto=format&fit=crop', categoryId: 'cat3', rating: 4.7 },
];


// --- COMPONENTES DE UI REFINADOS ---

const BottomNav = ({ activeView, setActiveView }) => {
  const navItems = [
    { id: 'home', icon: Home, label: 'Inicio' },
    { id: 'cart', icon: ShoppingCart, label: 'Carrito' },
    { id: 'profile', icon: User, label: 'Perfil' },
  ];
  const cart = useStore(appStore, state => state.cart);

  return (
    <div className="fixed bottom-0 left-0 right-0 bg-white/90 backdrop-blur-lg border-t border-gray-200 z-40">
      <div className="flex justify-around items-center h-20 max-w-md mx-auto">
        {navItems.map(item => (
          <button
            key={item.id}
            onClick={() => setActiveView(item.id)}
            className="flex flex-col items-center justify-center gap-1 w-20 transition-colors duration-300 text-gray-500 hover:text-red-600 relative"
          >
            <div className={`p-2 rounded-full transition-all ${activeView === item.id ? 'bg-red-100' : ''}`}>
              {item.id === 'cart' && cart.length > 0 && (
                <div className="absolute top-1 right-3.5 w-5 h-5 bg-red-600 text-white text-xs font-bold rounded-full flex items-center justify-center">
                  {cart.reduce((acc, item) => acc + item.quantity, 0)}
                </div>
              )}
              <item.icon className={`w-6 h-6 transition-colors ${activeView === item.id ? 'text-red-600' : ''}`} />
            </div>
            <span className={`text-xs font-semibold transition-colors ${activeView === item.id ? 'text-red-600' : ''}`}>{item.label}</span>
          </button>
        ))}
      </div>
    </div>
  );
};

const Header = () => (
  <div className="p-4 pt-6 bg-white sticky top-0 z-30 border-b border-gray-100">
    <div className="flex justify-between items-center">
        <div>
            <p className="text-sm text-gray-500">Pedir en</p>
            <h1 className="font-bold text-xl text-gray-800 flex items-center">
                DUO Previa
            </h1>
        </div>
        <img src={mockRestaurant.logoUrl} alt="DUO Previa Logo" className="w-12 h-12 rounded-full border-2 border-white shadow-md"/>
    </div>
  </div>
);

const ProductCard = ({ product, onSelect }) => {
  const { setState } = appStore;
  const favorites = useStore(appStore, state => state.favorites);
  const isFavorite = favorites.includes(product.id);

  const toggleFavorite = (e) => {
    e.stopPropagation();
    setState(state => ({
      favorites: isFavorite 
        ? state.favorites.filter(id => id !== product.id)
        : [...state.favorites, product.id]
    }));
  };
  
  const handleAddToCart = (e) => {
      e.stopPropagation();
      setState(state => {
          const existingItem = state.cart.find(item => item.id === product.id);
          if (existingItem) {
              return { cart: state.cart.map(item => item.id === product.id ? {...item, quantity: item.quantity + 1} : item) };
          }
          return { cart: [...state.cart, {...product, quantity: 1}] };
      });
  };

  return (
    <motion.div 
      onClick={() => onSelect(product)}
      className="bg-white rounded-2xl shadow-md shadow-gray-200/50 overflow-hidden flex flex-col relative transition-all duration-300 hover:shadow-xl hover:-translate-y-1"
      whileTap={{ scale: 0.98 }}
    >
      <div className="relative">
        <img src={product.image} alt={product.name} className="w-full h-40 object-cover" onError={(e) => { e.target.onerror = null; e.target.src='https://placehold.co/600x400/dc2626/f9fafb?text=Error'; }}
/>
        <button onClick={toggleFavorite} className="absolute top-3 right-3 p-2 bg-white/70 rounded-full backdrop-blur-sm transition-transform active:scale-90">
          <Heart className={`w-5 h-5 transition-all ${isFavorite ? 'text-red-500 fill-current' : 'text-gray-700'}`}/>
        </button>
      </div>
      <div className="p-4 flex-grow flex flex-col">
        <h3 className="font-bold text-lg text-gray-800 flex-grow">{product.name}</h3>
        <div className="flex justify-between items-center mt-3">
          <p className="text-xl font-black text-gray-900">${product.price.toLocaleString('es-AR')}</p>
          <div className="flex items-center gap-1 text-amber-500">
            <Star className="w-4 h-4 fill-current" />
            <span className="font-bold text-sm text-gray-700">{product.rating}</span>
          </div>
        </div>
      </div>
       <button onClick={handleAddToCart} className="absolute bottom-4 right-4 w-12 h-12 bg-red-600 text-white rounded-full flex items-center justify-center shadow-lg hover:bg-red-700 transition-all active:scale-90">
          <Plus className="w-6 h-6"/>
      </button>
    </motion.div>
  );
};

const Sheet = ({ children, isOpen, onClose, title }) => {
    if (!isOpen) return null;
    return (
        <motion.div 
            className="fixed inset-0 bg-black/60 z-50 flex items-end justify-center"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
        >
            <motion.div
                className="bg-gray-50 w-full max-w-md rounded-t-3xl max-h-[90vh] flex flex-col"
                initial={{ y: "100%" }}
                animate={{ y: "0%" }}
                exit={{ y: "100%" }}
                transition={{ type: 'spring', damping: 30, stiffness: 300 }}
                onClick={e => e.stopPropagation()}
            >
                <div className="p-4 border-b border-gray-200 flex-shrink-0 relative text-center">
                    <div className="w-10 h-1.5 bg-gray-300 rounded-full mx-auto mb-3"></div>
                    <h2 className="text-xl font-bold">{title}</h2>
                    <button onClick={onClose} className="absolute top-4 right-4 p-2 rounded-full bg-gray-200 hover:bg-gray-300">
                        <X className="w-5 h-5 text-gray-600" />
                    </button>
                </div>
                <div className="overflow-y-auto flex-grow">
                    {children}
                </div>
            </motion.div>
        </motion.div>
    );
};

const ProductDetailSheet = ({ product, isOpen, onClose }) => {
    const { setState } = appStore;
    const [quantity, setQuantity] = useState(1);
    
    useEffect(() => {
        if(isOpen) setQuantity(1);
    }, [isOpen]);

    const handleAddToCart = () => {
        setState(state => {
          const existingItem = state.cart.find(item => item.id === product.id);
          if (existingItem) {
              return { cart: state.cart.map(item => item.id === product.id ? {...item, quantity: item.quantity + quantity} : item) };
          }
          return { cart: [...state.cart, {...product, quantity}] };
        });
        onClose();
    };

    if (!product) return null;

    return (
        <Sheet isOpen={isOpen} onClose={onClose} title="">
            <img src={product.image} alt={product.name} className="w-full h-60 object-cover"/>
            <div className="p-6 pb-32">
                <div className="flex justify-between items-start">
                    <h2 className="text-3xl font-bold text-gray-900 max-w-xs">{product.name}</h2>
                    <div className="flex items-center gap-1 text-amber-500 bg-white px-3 py-1.5 rounded-full shadow-md">
                        <Star className="w-5 h-5 fill-current"/>
                        <span className="font-bold text-lg">{product.rating}</span>
                    </div>
                </div>
                <p className="text-gray-600 leading-relaxed my-4">{product.description}</p>
            </div>
            
            <div className="fixed bottom-0 left-0 right-0 p-4 bg-white/90 border-t border-gray-200 backdrop-blur-sm">
                 <div className="flex justify-between items-center max-w-lg mx-auto">
                    <div className="flex items-center gap-4">
                        <button onClick={() => setQuantity(q => Math.max(1, q - 1))} className="p-3 bg-gray-200 rounded-full hover:bg-gray-300 transition-colors"><Minus className="w-5 h-5"/></button>
                        <span className="text-2xl font-bold w-8 text-center">{quantity}</span>
                        <button onClick={() => setQuantity(q => q + 1)} className="p-3 bg-gray-200 rounded-full hover:bg-gray-300 transition-colors"><Plus className="w-5 h-5"/></button>
                    </div>
                    <button onClick={handleAddToCart} className="bg-red-600 text-white font-bold py-4 px-6 rounded-full hover:bg-red-700 transition-colors shadow-lg shadow-red-300/50 flex-grow ml-6">
                        Agregar ${ (product.price * quantity).toLocaleString('es-AR') }
                    </button>
                </div>
            </div>
        </Sheet>
    );
};

// --- VISTAS PRINCIPALES (PANTALLAS) ---

const HomeScreen = ({ onProductSelect }) => {
    const [products, setProducts] = useState([]);
    const [categories, setCategories] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [activeCategory, setActiveCategory] = useState(null);

    useEffect(() => {
        const fetchData = async () => {
            setLoading(true);
            setError(null);
            // En un backend real, el slug del restaurante podría venir de la URL o de una configuración.
            const restaurantSlug = 'pizzeria-bella'; 
            // La URL base de la API debería estar en una variable de entorno.
            const API_BASE_URL = '/api'; 

            try {
                // Se hacen las dos peticiones en paralelo para mejorar el rendimiento.
                const [productsResponse, categoriesResponse] = await Promise.all([
                    fetch(`${API_BASE_URL}/${restaurantSlug}/products`),
                    // NOTA: Este endpoint de categorías no está en el backend de ejemplo.
                    // Debería ser implementado para devolver las categorías del restaurante.
                    fetch(`${API_BASE_URL}/${restaurantSlug}/categories`) 
                ]);

                if (!productsResponse.ok || !categoriesResponse.ok) {
                    throw new Error('La respuesta de la red no fue exitosa');
                }

                const productsData = await productsResponse.json();
                const categoriesData = await categoriesResponse.json();

                setProducts(productsData);
                setCategories(categoriesData);
                if (categoriesData.length > 0) {
                    setActiveCategory(categoriesData[0].id);
                }

            } catch (err) {
                console.error("No se pudo obtener datos de la API, usando datos de fallback.", err);
                setError('No se pudo cargar el menú. Por favor, intente de nuevo más tarde.');
                // Fallback a datos de mock para que la app siga funcionando en la demo.
                setProducts(fallbackProducts);
                setCategories(fallbackCategories);
                if (fallbackCategories.length > 0) {
                    setActiveCategory(fallbackCategories[0].id);
                }
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, []);

    const filteredProducts = useMemo(() => {
        if (!activeCategory) return products;
        return products.filter(p => p.categoryId === activeCategory);
    }, [activeCategory, products]);

    if (loading) {
        return (
            <div className="flex flex-col items-center justify-center h-screen">
                <LoaderCircle className="w-12 h-12 text-red-600 animate-spin" />
                <p className="mt-4 text-lg text-gray-600">Cargando menú...</p>
            </div>
        );
    }
    
    return (
        <div>
            <Header />
            <div className="p-4">
                <div className="relative">
                    <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400 w-5 h-5"/>
                    <input type="text" placeholder="Buscar lomitos, hamburguesas..." className="w-full bg-gray-100 border border-gray-200 rounded-full pl-11 pr-4 py-3 focus:outline-none focus:ring-2 focus:ring-red-400"/>
                </div>
            </div>
            
            {error && <div className="p-4 mx-4 bg-red-100 text-red-700 rounded-lg text-center">{error}</div>}

            <div className="py-2">
                <ul className="flex gap-3 overflow-x-auto px-4 pb-3">
                    {categories.map(cat => (
                        <motion.li key={cat.id}>
                            <button onClick={() => setActiveCategory(cat.id)} className={`flex-shrink-0 px-5 py-3 rounded-full font-semibold transition-all flex items-center gap-2.5 text-sm ${activeCategory === cat.id ? 'bg-red-600 text-white shadow-md shadow-red-300/50' : 'bg-white text-gray-700 border border-gray-200'}`}>
                                {cat.icon} {cat.name}
                            </button>
                        </motion.li>
                    ))}
                </ul>
            </div>

            <div className="p-4">
                <h2 className="text-2xl font-bold mb-4">Populares de la Semana </h2>
                <div className="grid grid-cols-2 gap-4">
                    {products.filter(p => p.popular).map(p => <ProductCard key={p.id} product={p} onSelect={onProductSelect} />)}
                </div>
                
                <h2 className="text-2xl font-bold mt-8 mb-4">Menú Completo</h2>
                <div className="grid grid-cols-2 gap-4">
                    {filteredProducts.map(p => <ProductCard key={p.id} product={p} onSelect={onProductSelect} />)}
                </div>
            </div>
        </div>
    );
};

const CartScreen = ({ onBack, onCheckout }) => {
    const cart = useStore(appStore, state => state.cart);
    const { setState } = appStore;

    const updateQuantity = (productId, newQuantity) => {
        if (newQuantity < 1) {
            setState(state => ({ cart: state.cart.filter(item => item.id !== productId) }));
        } else {
            setState(state => ({
                cart: state.cart.map(item => item.id === productId ? { ...item, quantity: newQuantity } : item)
            }));
        }
    };

    const subtotal = useMemo(() => cart.reduce((acc, item) => acc + item.price * item.quantity, 0), [cart]);
    const deliveryFee = 1500; // Ejemplo
    const total = subtotal + deliveryFee;

    return (
        <div>
            <div className="p-4 pt-6 bg-white sticky top-0 z-10 border-b flex items-center gap-4">
                <button onClick={onBack} className="p-2 -ml-2"><ArrowLeft className="w-6 h-6"/></button>
                <h1 className="text-2xl font-bold">Mi Carrito</h1>
            </div>

            {cart.length === 0 ? (
                <div className="p-6 text-center mt-20">
                    <ShoppingCart className="w-24 h-24 text-gray-300 mx-auto mb-4"/>
                    <h2 className="text-2xl font-bold">Tu carrito está vacío</h2>
                    <p className="text-gray-500 mt-2">Agregá tus productos favoritos para empezar a pedir.</p>
                </div>
            ) : (
                <div className="p-4 pb-48">
                    <ul className="space-y-4">
                        {cart.map(item => (
                            <li key={item.id} className="flex items-center gap-4 bg-white p-4 rounded-2xl shadow-sm">
                                <img src={item.image} alt={item.name} className="w-20 h-20 rounded-xl object-cover"/>
                                <div className="flex-grow">
                                    <h3 className="font-bold text-gray-800">{item.name}</h3>
                                    <p className="font-black text-red-600 mt-1">${(item.price * item.quantity).toLocaleString('es-AR')}</p>
                                </div>
                                <div className="flex items-center gap-3">
                                    <button onClick={() => updateQuantity(item.id, item.quantity - 1)} className="p-2 bg-gray-100 rounded-full"><Minus className="w-4 h-4"/></button>
                                    <span className="font-bold text-lg">{item.quantity}</span>
                                    <button onClick={() => updateQuantity(item.id, item.quantity + 1)} className="p-2 bg-gray-100 rounded-full"><Plus className="w-4 h-4"/></button>
                                </div>
                            </li>
                        ))}
                    </ul>

                    <div className="mt-8 p-4 bg-white rounded-2xl space-y-3">
                        <div className="flex justify-between text-gray-600"><span>Subtotal</span> <span className="font-medium">${subtotal.toLocaleString('es-AR')}</span></div>
                        <div className="flex justify-between text-gray-600"><span>Envío</span> <span className="font-medium">${deliveryFee.toLocaleString('es-AR')}</span></div>
                        <div className="flex justify-between font-bold text-xl mt-2 pt-3 border-t"><span>Total</span> <span>${total.toLocaleString('es-AR')}</span></div>
                    </div>
                </div>
            )}
            
            {cart.length > 0 && (
              <div className="fixed bottom-20 left-0 right-0 p-4 bg-white/90 border-t backdrop-blur-sm">
                  <button onClick={onCheckout} className="w-full bg-green-500 text-white font-bold py-4 rounded-full hover:bg-green-600 transition-colors shadow-lg shadow-green-300/50 flex items-center justify-center gap-2">
                      <ShoppingCart className="w-5 h-5"/>
                      Finalizar pedido por WhatsApp
                  </button>
              </div>
            )}
        </div>
    );
};


const ProfileScreen = () => (
    <div className="p-4 pt-6 h-screen flex flex-col items-center justify-center text-center bg-gray-50">
        <User className="w-24 h-24 text-gray-300 mb-4"/>
        <h2 className="text-2xl font-bold">Mi Perfil</h2>
        <p className="text-gray-500 mt-2 max-w-xs">Aquí podrás ver tu información, direcciones y pedidos anteriores.</p>
    </div>
);

// --- COMPONENTE PRINCIPAL DE LA APP ---
export default function DuoPreviaApp() {
  const [activeView, setActiveView] = useState('home');
  const [selectedProduct, setSelectedProduct] = useState(null);

  const handleCheckout = () => {
      const cart = appStore.getState().cart;
      const total = cart.reduce((acc, item) => acc + item.price * item.quantity, 0) + 1500;
      let message = `¡Hola DUO Previa!  Quiero hacer un pedido:\n\n`;
      cart.forEach(item => {
          message += `* ${item.quantity}x ${item.name} - $${(item.price * item.quantity).toLocaleString('es-AR')}\n`;
      });
      message += `\n*Total (con envío): $${total.toLocaleString('es-AR')}*`;
      message += `

_Por favor, confirmame el pedido y decime cómo seguimos._`;

      const whatsappUrl = `https://wa.me/5493510000000?text=${encodeURIComponent(message)}`; // Reemplazar con el número real
      window.open(whatsappUrl, '_blank');
  };

  const renderView = () => {
    switch (activeView) {
      case 'home':
        return <HomeScreen onProductSelect={setSelectedProduct} />;
      case 'cart':
        return <CartScreen onBack={() => setActiveView('home')} onCheckout={handleCheckout} />;
      case 'profile':
        return <ProfileScreen />;
      default:
        return <HomeScreen onProductSelect={setSelectedProduct} />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 font-sans max-w-md mx-auto border-x border-gray-100 pb-20 selection:bg-red-200">
      {renderView()}
      <BottomNav activeView={activeView} setActiveView={setActiveView} />
      <ProductDetailSheet 
        product={selectedProduct}
        isOpen={!!selectedProduct}
        onClose={() => setSelectedProduct(null)}
      />
    </div>
  );
}