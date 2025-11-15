import React from 'react';
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

const InsightSection = ({ title, content, icon, color = "blue" }) => {
  const colorClasses = {
    blue: "bg-blue-500/20 border-blue-400/30 text-blue-300",
    green: "bg-green-500/20 border-green-400/30 text-green-300",
    yellow: "bg-yellow-500/20 border-yellow-400/30 text-yellow-300",
    red: "bg-red-500/20 border-red-400/30 text-red-300",
    purple: "bg-purple-500/20 border-purple-400/30 text-purple-300"
  };

  return (
    <div className={`${colorClasses[color]} backdrop-blur-sm border rounded-lg p-4`}>
      <div className="flex items-center mb-2">
        <span className="text-lg mr-2">{icon}</span>
        <h4 className={`text-md font-semibold ${colorClasses[color].split(' ')[2]}`}>
          {title}
        </h4>
      </div>
      <p className="text-gray-200 text-sm whitespace-pre-wrap leading-relaxed">
        {content || "No analysis available for this aspect."}
      </p>
    </div>
  );
};

const SessionInsightsCard = ({ insights }) => {
  if (!insights) {
    return (
      <Card className="bg-transparent shadow-none border-none rounded-none">
        <CardContent className="p-0">
          <div className="bg-black/30 backdrop-blur-sm border border-white/20 rounded-lg p-4">
            <p className="text-gray-400">Session insights not available. This analysis requires multiple conversations in the same session.</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  const {
    consistency_analysis,
    behavioral_evolution,
    risk_trajectory, 
    conversation_dynamics
  } = insights;

  // Check if we have any actual content
  const hasContent = consistency_analysis || behavioral_evolution || risk_trajectory || conversation_dynamics;

  if (!hasContent) {
    return (
      <Card className="bg-transparent shadow-none border-none rounded-none">
        <CardContent className="p-0">
          <div className="bg-black/30 backdrop-blur-sm border border-white/20 rounded-lg p-4">
            <p className="text-gray-400">Session insights will appear after multiple analyses in the same session.</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="bg-transparent shadow-none border-none rounded-none">
      <CardContent className="p-0 space-y-4">
        
        {/* Header with session indicator */}
        <div className="bg-black/40 backdrop-blur-sm border border-white/20 rounded-lg p-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <span className="text-xl mr-2">🔄</span>
              <h3 className="text-lg font-semibold text-white">Multi-Conversation Session Analysis</h3>
            </div>
            <Badge variant="outline" className="bg-green-500/20 text-green-300 border-green-400/30">
              Session Active
            </Badge>
          </div>
        </div>

        {/* Consistency Analysis */}
        {consistency_analysis && (
          <InsightSection
            title="Consistency Analysis"
            content={consistency_analysis}
            icon="🎯"
            color="blue"
          />
        )}

        {/* Behavioral Evolution */}
        {behavioral_evolution && (
          <InsightSection
            title="Behavioral Evolution"
            content={behavioral_evolution}
            icon="📈"
            color="green"
          />
        )}

        {/* Risk Trajectory */}
        {risk_trajectory && (
          <InsightSection
            title="Risk Trajectory"
            content={risk_trajectory}
            icon="⚠️"
            color="yellow"
          />
        )}

        {/* Conversation Dynamics */}
        {conversation_dynamics && (
          <InsightSection
            title="Conversation Dynamics"
            content={conversation_dynamics}
            icon="💬"
            color="purple"
          />
        )}

        {/* Footer note */}
        <div className="bg-black/20 backdrop-blur-sm border border-white/10 rounded-lg p-3">
          <p className="text-gray-400 text-xs">
            💡 Session insights become more accurate with additional conversations in the same session.
          </p>
        </div>
      </CardContent>
    </Card>
  );
};

export default SessionInsightsCard;
