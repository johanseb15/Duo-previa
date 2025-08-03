'use client';

import { useEffect, useState } from 'react';

export default function Home() {
  const [message, setMessage] = useState('');

  useEffect(() => {
    fetch('/api/message')
      .then((res) => res.json())
      .then((data) => setMessage(data.message));
  }, []);

  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <h1 className="text-4xl font-bold">PWA Moderna</h1>
      <p className="mt-4 text-lg">{message}</p>
    </main>
  );
}
