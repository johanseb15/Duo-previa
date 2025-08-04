import React from 'react';

const SuccessAnimation = () => (
  <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-[60]">
    <div className="bg-white rounded-2xl p-8 text-center max-w-sm mx-4 animate-pulse">
      <div className="text-6xl mb-4"></div>
      <h3 className="text-xl font-bold text-gray-800 mb-2">
        ¡Pedido enviado!
      </h3>
      <p className="text-gray-600">
        Te contactaremos por WhatsApp para confirmar tu pedido.
      </p>
    </div>
  </div>
);

export default SuccessAnimation;
