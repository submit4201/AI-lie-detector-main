import React from 'react';
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

const ListSection = ({ title, items, emptyMessage, color = "blue" }) => {
  const colorClasses = {
    blue: "bg-blue-500/20 border-blue-400/30 text-blue-300",
    red: "bg-red-500/20 border-red-400/30 text-red-300",
    yellow: "bg-yellow-500/20 border-yellow-400/30 text-yellow-300",
    green: "bg-green-500/20 border-green-400/30 text-green-300",
    purple: "bg-purple-500/20 border-purple-400/30 text-purple-300"
  };

  return (
    <div>
      <h4 className={`text-md font-semibold mb-2 ${colorClasses[color].split(' ')[2]}`}>
        {title}
      </h4>
      {items && items.length > 0 ? (
        <div className="space-y-2">
          {items.map((item, index) => (
            <div
              key={index}
              className={`${colorClasses[color].split(' ').slice(0, 2).join(' ')} backdrop-blur-sm border rounded-lg p-3`}
            >
              <p className="text-gray-200 text-sm">{item}</p>
            </div>
          ))}
        </div>
      ) : (
        <p className="text-gray-400 text-sm">{emptyMessage}</p>
      )}
    </div>
  );
};

const EnhancedUnderstandingCard = ({ understanding }) => {
  if (!understanding) {
    return (
      <Card className="bg-transparent shadow-none border-none rounded-none">
        <CardContent className="p-0">
          <div className="bg-black/30 backdrop-blur-sm border border-white/20 rounded-lg p-4">
            <p className="text-gray-400">Enhanced understanding data not available.</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  const {
    key_inconsistencies = [],
    areas_of_evasiveness = [],
    suggested_follow_up_questions = [],
    unverified_claims = []
  } = understanding;

  return (
    <Card className="bg-transparent shadow-none border-none rounded-none">
      <CardContent className="p-0 space-y-6">
        
        {/* Key Inconsistencies */}
        <ListSection
          title="🔍 Key Inconsistencies"
          items={key_inconsistencies}
          emptyMessage="No significant inconsistencies detected."
          color="red"
        />

        {/* Areas of Evasiveness */}
        <ListSection
          title="🚪 Areas of Evasiveness"
          items={areas_of_evasiveness}
          emptyMessage="No evasive patterns detected."
          color="yellow"
        />

        {/* Suggested Follow-up Questions */}
        <ListSection
          title="❓ Suggested Follow-up Questions"
          items={suggested_follow_up_questions}
          emptyMessage="No specific follow-up questions suggested."
          color="blue"
        />

        {/* Unverified Claims */}
        <ListSection
          title="⚠️ Unverified Claims"
          items={unverified_claims}
          emptyMessage="No unverified claims identified."
          color="purple"
        />

        {/* Summary Badge */}
        <div className="flex flex-wrap gap-2 pt-4 border-t border-white/10">
          <Badge variant="outline" className="bg-black/20 text-gray-300 border-white/20">
            {key_inconsistencies.length} Inconsistencies
          </Badge>
          <Badge variant="outline" className="bg-black/20 text-gray-300 border-white/20">
            {areas_of_evasiveness.length} Evasive Areas
          </Badge>
          <Badge variant="outline" className="bg-black/20 text-gray-300 border-white/20">
            {suggested_follow_up_questions.length} Follow-ups
          </Badge>
          <Badge variant="outline" className="bg-black/20 text-gray-300 border-white/20">
            {unverified_claims.length} Unverified Claims
          </Badge>
        </div>
      </CardContent>
    </Card>
  );
};

export default EnhancedUnderstandingCard;
