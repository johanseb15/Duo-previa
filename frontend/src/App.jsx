import React, { useState, useEffect } from 'react';
import './index.css'; // Import Tailwind CSS

function App() {
  const [message, setMessage] = useState('');
  const [prompt, setPrompt] = useState('');
  const [aiResponse, setAiResponse] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Fetch message from backend
    fetch('/api/message')
      .then(response => {
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
      })
      .then(data => setMessage(data.message))
      .catch(error => {
        console.error("Error fetching message:", error);
        setMessage("Failed to load message from backend.");
      });
  }, []);

  const handleGenerate = async () => {
    setLoading(true);
    setError(null);
    setAiResponse('');
    try {
      const response = await fetch('/api/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text: prompt }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setAiResponse(data.response);
    } catch (err) {
      console.error("Error generating AI response:", err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col items-center justify-center p-4">
      <h1 className="text-4xl font-bold text-gray-800 mb-6">Duo Previa AI</h1>
      
      <div className="bg-white p-8 rounded-lg shadow-md w-full max-w-md mb-8">
        <h2 className="text-2xl font-semibold text-gray-700 mb-4">Backend Message:</h2>
        <p className="text-gray-600 text-lg">{message}</p>
      </div>

      <div className="bg-white p-8 rounded-lg shadow-md w-full max-w-md">
        <h2 className="text-2xl font-semibold text-gray-700 mb-4">Generate AI Text:</h2>
        <textarea
          className="w-full p-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500 mb-4"
          rows="5"
          placeholder="Enter your prompt here..."
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
        ></textarea>
        <button
          className="w-full bg-red-600 text-white py-3 rounded-md font-semibold hover:bg-red-700 transition-colors duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
          onClick={handleGenerate}
          disabled={loading || !prompt.trim()}
        >
          {loading ? 'Generating...' : 'Generate'}
        </button>

        {error && (
          <p className="text-red-500 mt-4 text-center">Error: {error}</p>
        )}

        {aiResponse && (
          <div className="mt-6 p-4 bg-gray-50 border border-gray-200 rounded-md">
            <h3 className="text-xl font-medium text-gray-700 mb-2">AI Response:</h3>
            <p className="text-gray-800 whitespace-pre-wrap">{aiResponse}</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;