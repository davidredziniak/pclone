"use client";

import React from 'react';

type CloneResultProps = {
  result: {
    success: boolean;
    exactPc: boolean;
    originalPrice: number;
    newPrice: number;
    link: string;
  } | null;
};

const CloneResult: React.FC<CloneResultProps> = ({ result }) => {
  if (!result) return null;

  return (
    <div className="mt-8 p-4 border border-gray-300 rounded-lg shadow-lg bg-white w-full max-w-md">
      <h2 className="text-2xl font-bold mb-4">Result</h2>
      <p className="text-lg">
        <strong>Matched Exact Specs:</strong> {result.exactPc ? 'Yes' : 'No'}
      </p>
      <p className="text-lg">
        <strong>Original Price:</strong> ${result.originalPrice.toFixed(2)}
      </p>
      <p className="text-lg">
        <strong>New Price:</strong> ${result.newPrice.toFixed(2)}
      </p>
      <p className="text-lg">
        <strong>Link:</strong> <a href={result.link} className="text-blue-500 hover:underline" target="_blank" rel="noopener noreferrer">{result.link}</a>
      </p>
    </div>
  );
};

export default CloneResult;