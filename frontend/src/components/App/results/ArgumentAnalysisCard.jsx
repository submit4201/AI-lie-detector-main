import React from 'react';
import { Card, CardContent } from "@/components/ui/card";

const ListItem = ({ item, colorClass = "text-gray-300" }) => (
  <li className={`${colorClass} text-sm bg-black/20 p-2 rounded-md border border-white/10`}>
    {item}
  </li>
);

const ArgumentAnalysisCard = ({ analysis }) => {
  if (!analysis) {
    return (
      <Card className="bg-transparent shadow-none border-none rounded-none">
        <CardContent className="p-0">
          <div className="bg-black/30 backdrop-blur-sm border border-white/20 rounded-lg p-4">
            <p className="text-gray-400">Argument analysis data not available.</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  const {
    argument_strengths = [],
    argument_weaknesses = [],
    overall_argument_coherence_score = 0
  } = analysis;

  return (
    <Card className="bg-transparent shadow-none border-none rounded-none">
      <CardContent className="p-0 space-y-4"> {/* Added space-y-4 here */}
        {/* Removed the intermediate div */}
        <div>
          <h4 className="text-md font-semibold text-blue-300 mb-2">Argument Coherence Score</h4>
          <div className="flex items-center">
            <div className="w-full bg-gray-700 rounded-full h-2.5 mr-3">
              <div
                className="bg-blue-500 h-2.5 rounded-full"
                style={{ width: `${overall_argument_coherence_score}%` }}
              ></div>
            </div>
            <span className="text-blue-200 font-bold">{overall_argument_coherence_score}/100</span>
          </div>
        </div>

        <div>
          <h4 className="text-md font-semibold text-green-300 mb-2">Strengths</h4>
          {argument_strengths.length > 0 ? (
            <ul className="space-y-1 list-disc list-inside pl-1">
              {argument_strengths.map((strength, index) => (
                <ListItem key={index} item={strength} colorClass="text-green-200" />
              ))}
            </ul>
          ) : (
            <p className="text-gray-400 text-sm">None identified.</p>
          )}
        </div>

        <div>
          <h4 className="text-md font-semibold text-red-300 mb-2">Weaknesses</h4>
          {argument_weaknesses.length > 0 ? (
            <ul className="space-y-1 list-disc list-inside pl-1">
              {argument_weaknesses.map((weakness, index) => (
                <ListItem key={index} item={weakness} colorClass="text-red-200" />
              ))}
            </ul>
          ) : (
            <p className="text-gray-400 text-sm">None identified.</p>
          )}
        </div>
      </CardContent>
    </Card>  );
};

export default ArgumentAnalysisCard;
