import React, { useState } from 'react';
import { Card, CardContent } from "@/components/ui/card";
import SessionHistorySection from './SessionHistorySection';
import ExportSection from './ExportSection';

const TabButton = ({ isActive, onClick, children, icon }) => (
  <button
    onClick={onClick}
    className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-all duration-200 ${
      isActive 
        ? 'bg-purple-500/30 text-purple-300 border border-purple-400/50' 
        : 'bg-black/20 text-gray-400 hover:bg-white/10 hover:text-white border border-transparent'
    }`}
  >
    <span>{icon}</span>
    <span className="font-medium">{children}</span>
  </button>
);

const TabbedSecondarySection = ({ result, sessionHistory, sessionId, onSelectHistoryItem }) => {
  const [activeTab, setActiveTab] = useState('history');

  const tabs = [
    {
      id: 'history',
      label: 'Session History',
      icon: '📜',
      component: SessionHistorySection
    },
    {
      id: 'export',
      label: 'Export Results',
      icon: '📥',
      component: ExportSection
    }
  ];

  const ActiveComponent = tabs.find(tab => tab.id === activeTab)?.component;

  return (
    <Card className="section-container">
      <CardContent className="p-6">
        {/* Tab Navigation */}
        <div className="flex space-x-2 mb-6 border-b border-gray-600/30 pb-4">
          {tabs.map((tab) => (
            <TabButton
              key={tab.id}
              isActive={activeTab === tab.id}
              onClick={() => setActiveTab(tab.id)}
              icon={tab.icon}
            >
              {tab.label}
            </TabButton>
          ))}
        </div>

        {/* Active Tab Content */}
        <div className="min-h-[300px]">
          {ActiveComponent && (
            <ActiveComponent
              result={result}
              sessionHistory={sessionHistory}
              sessionId={sessionId}
              onSelectHistoryItem={onSelectHistoryItem}
            />
          )}
        </div>
      </CardContent>
    </Card>
  );
};

export default TabbedSecondarySection;
