import React from 'react';

const Header = () => {
  return (
    <div className="bg-black/20 backdrop-blur-sm border-b border-white/10">
      <div className="max-w-7xl mx-auto px-6 py-6">
        <div className="text-center">
          <h1 className="text-5xl font-bold bg-gradient-to-r from-blue-400 via-purple-400 to-cyan-400 bg-clip-text text-transparent mb-3">
            🎙️ NoLyan
          </h1>
          <p className="text-gray-300 text-lg">Advanced voice analysis with AI-powered deception detection</p>
        </div>
      </div>
    </div>
  );
};

export default Header;
