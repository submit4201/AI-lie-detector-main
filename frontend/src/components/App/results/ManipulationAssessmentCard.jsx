import React from 'react';
import { Card, CardContent } from "@/components/ui/card";
import ConfidenceChip from '@/components/ui/ConfidenceChip';
import Tooltip from '@/components/ui/tooltip';

const ListItem = ({ item }) => (
  <li className="text-gray-300 text-sm bg-black/20 p-2 rounded-md border border-white/10">
    {item}
  </li>
);

const ManipulationAssessmentCard = ({ assessment }) => {
  if (!assessment) {
    return (
      <Card className="bg-transparent shadow-none border-none rounded-none">
        <CardContent className="p-0">
          <div className="bg-black/30 backdrop-blur-sm border border-white/20 rounded-lg p-4">
            <p className="text-gray-400">Manipulation assessment data not available.</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  const {
    manipulation_score = 0,
    manipulation_tactics = [],
    manipulation_explanation = "N/A",
    example_phrases = []
  } = assessment;

  return (
    <Card className="bg-transparent shadow-none border-none rounded-none">
      <CardContent className="p-0 space-y-4"> {/* Added space-y-4 here */}
        {/* Removed the intermediate div */}
        <div>
          <h4 className="text-md font-semibold text-purple-300 mb-2">Manipulation Likelihood</h4>
          <div className="flex items-center">
            <div className="w-full bg-gray-700 rounded-full h-2.5 mr-3">
              <div
                className="bg-purple-500 h-2.5 rounded-full"
                style={{ width: `${manipulation_score}%` }}
              ></div>
            </div>
            <span className="text-purple-200 font-bold">{manipulation_score}/100</span>
            <ConfidenceChip value={manipulation_score} />
          </div>
        </div>

        <div>
          <h4 className="text-md font-semibold text-purple-300 mb-2">Identified Tactics</h4>
            {manipulation_tactics.length > 0 ? (
            <ul className="space-y-1 list-disc list-inside pl-1">
              {manipulation_tactics.map((tactic, index) => (
                <ListItem key={index} item={<Tooltip text={typeof tactic === 'string' ? `Tactic: ${tactic}` : 'Tactic'}>{typeof tactic === 'string' ? tactic : JSON.stringify(tactic)}</Tooltip>} />
              ))}
            </ul>
          ) : (
            <p className="text-gray-400 text-sm">None detected.</p>
          )}
        </div>

        <div>
          <h4 className="text-md font-semibold text-purple-300 mb-2">Explanation</h4>
          <p className="text-gray-300 text-sm bg-black/20 p-3 rounded-md border border-white/10 whitespace-pre-wrap">
            {manipulation_explanation || "N/A"}
          </p>
        </div>

        <div>
          <h4 className="text-md font-semibold text-purple-300 mb-2">Example Phrases</h4>
          {example_phrases.length > 0 ? (
            <ul className="space-y-1 list-disc list-inside pl-1">
              {example_phrases.map((phrase, index) => <ListItem key={index} item={phrase} />)}
            </ul>
          ) : (
            <p className="text-gray-400 text-sm">None provided.</p>
          )}
        </div>
      </CardContent>
    </Card>  );
};

export default ManipulationAssessmentCard;
