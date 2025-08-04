import React from 'react';

const DeliveryZoneSelector = ({ zones, selectedZone, onZoneChange }) => (
  <div className="mb-6">
    <label className="block text-sm font-medium text-gray-700 mb-3">
      <span className="flex items-center space-x-2">
        <span></span>
        <span>¿A dónde llevamos tu pedido?</span>
      </span>
    </label>
    <div className="grid grid-cols-1 gap-3">
      {zones.map(zone => (
        <label
          key={zone.id}
          className={`flex items-center justify-between p-4 rounded-xl border-2 cursor-pointer transition-all ${
            selectedZone?.id === zone.id
              ? 'border-red-500 bg-red-50'
              : 'border-gray-200 hover:border-gray-300 bg-white'
          }`}
        >
          <div className="flex items-center space-x-3">
            <input
              type="radio"
              name="delivery-zone"
              value={zone.id}
              checked={selectedZone?.id === zone.id}
              onChange={() => onZoneChange(zone)}
              className="text-red-600 focus:ring-red-500"
            />
            <div>
              <div className="font-semibold text-gray-800">{zone.name}</div>
              <div className="text-sm text-gray-600">{zone.estimated_time}</div>
            </div>
          </div>
          <div className="text-right">
            <div className="font-bold text-red-600">
              ${zone.delivery_fee.toLocaleString()}
            </div>
            <div className="text-xs text-gray-500">envío</div>
          </div>
        </label>
      ))}
    </div>
  </div>
);

export default DeliveryZoneSelector;
