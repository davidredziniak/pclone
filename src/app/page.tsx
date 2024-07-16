"use client";

import React from 'react';
import CloneBox from './components/CloneBox';

const Home: React.FC = () => {
  return (
    <div>
    <div className="bg-white bg-opacity-80 p-10 rounded-lg shadow-lg text-center mb-8">
      <h1 className="text-3xl font-bold text-gray-800 mb-4">PClone</h1>
      <p>
        Quickly clone your pre-built PC link into pcpartpicker.com
      </p>
    </div>
    <div className="bg-white bg-opacity-80 p-10 rounded-lg shadow-lg text-center">
      <CloneBox />
    </div>
    </div>
  );
};

export default Home;