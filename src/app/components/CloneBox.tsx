"use client";

import React, { useState } from 'react';
import CloneResult from './CloneResult';

type CloneError = {
  success: boolean;
  message: string;
};

type CloneResult = {
  success: boolean;
  exactPc: boolean;
  originalPrice: number;
  newPrice: number;
  link: string;
};

const CloneBox: React.FC = () => {
  const [query, setQuery] = useState<string>('');
  const [result, setResult] = useState<CloneResult | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<CloneError | null>(null);

  const handleClone = async () => {
    setResult(null); // Clear previous result
    setLoading(true); // Set loading state to true
    setError(null); // Clear any previus errors

    try {
      const response = await fetch(`/api/clone?q=${query}`);
      if (!response.ok) { // error
        setLoading(false); // Set loading state to false
        const data: CloneError = await response.json();
        setError(data);
        return;
      }
      else {
        // Response received a 200 OK
        const data: CloneResult = await response.json();
        setResult(data);
      }
    } catch (error: any) {
      setError(error.message);
    } finally {
      setLoading(false); // Set loading state to false
    }
  };

  return (
    <div className="flex flex-col items-center space-y-4">
      <div className="flex justify-center items-center space-x-4">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Enter Bestbuy.com URL..."
          className="p-2 border border-gray-300 rounded-md w-64"
        />
        <button
          onClick={handleClone}
          className={`p-2 text-white rounded-md ${loading ? 'bg-gray-400 cursor-not-allowed' : 'bg-blue-500 hover:bg-blue-600'}`}
          disabled={loading}
        >
          {loading ? (
            <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"></path>
            </svg>
          ) : (
            'Clone'
          )}
        </button>
      </div>
      {error && (
        <div className="mt-4 text-red-500">
          {error.message}
        </div>
      )}
      {result && <CloneResult result={result} />}</div>
  );
};

export default CloneBox;