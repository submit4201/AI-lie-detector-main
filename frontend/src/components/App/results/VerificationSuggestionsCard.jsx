import React from 'react';
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

const VerificationItem = ({ suggestion, priority = 'medium' }) => {
  const priorityColors = {
    high: 'bg-red-500/20 border-red-400/30 text-red-300',
    medium: 'bg-yellow-500/20 border-yellow-400/30 text-yellow-300',
    low: 'bg-blue-500/20 border-blue-400/30 text-blue-300'
  };

  const priorityIcons = {
    high: '🚨',
    medium: '⚠️',
    low: 'ℹ️'
  };

  return (
    <div className={`${priorityColors[priority]} backdrop-blur-sm border rounded-lg p-4`}>
      <div className="flex items-start">
        <span className="text-lg mr-3 mt-0.5">{priorityIcons[priority]}</span>
        <div className="flex-1">
          <p className="text-gray-200 text-sm leading-relaxed">{suggestion}</p>
          <div className="mt-2">
            <Badge 
              variant="outline" 
              className={`text-xs ${priorityColors[priority].split(' ')[2]} bg-black/20 border-current`}
            >
              {priority.charAt(0).toUpperCase() + priority.slice(1)} Priority
            </Badge>
          </div>
        </div>
      </div>
    </div>
  );
};

const VerificationSuggestionsCard = ({ result }) => {
  if (!result) {
    return (
      <Card className="bg-transparent shadow-none border-none rounded-none">
        <CardContent className="p-0">
          <div className="bg-black/30 backdrop-blur-sm border border-white/20 rounded-lg p-4">
            <p className="text-gray-400">Verification suggestions not available.</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  // Extract verification suggestions from various sources
  const recommendations = result.recommendations || [];
  const riskMitigation = result.risk_assessment?.mitigation_suggestions || [];
  const followUpQuestions = result.enhanced_understanding?.suggested_follow_up_questions || [];
  const unverifiedClaims = result.enhanced_understanding?.unverified_claims || [];

  // Categorize suggestions by priority based on content
  const categorizeSuggestions = (suggestions) => {
    return suggestions.map(suggestion => {
      const lowerSugg = suggestion.toLowerCase();
      if (lowerSugg.includes('urgent') || lowerSugg.includes('immediate') || 
          lowerSugg.includes('critical') || lowerSugg.includes('verify immediately')) {
        return { text: suggestion, priority: 'high' };
      } else if (lowerSugg.includes('follow up') || lowerSugg.includes('investigate') || 
                lowerSugg.includes('check') || lowerSugg.includes('confirm')) {
        return { text: suggestion, priority: 'medium' };
      } else {
        return { text: suggestion, priority: 'low' };
      }
    });
  };

  const categorizedRecommendations = categorizeSuggestions(recommendations);
  const categorizedMitigation = categorizeSuggestions(riskMitigation);

  // Check if we have any verification content
  const hasContent = recommendations.length > 0 || riskMitigation.length > 0 || 
                    followUpQuestions.length > 0 || unverifiedClaims.length > 0;

  if (!hasContent) {
    return (
      <Card className="bg-transparent shadow-none border-none rounded-none">
        <CardContent className="p-0">
          <div className="bg-black/30 backdrop-blur-sm border border-white/20 rounded-lg p-4">
            <p className="text-gray-400">No specific verification steps recommended at this time.</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="bg-transparent shadow-none border-none rounded-none">
      <CardContent className="p-0 space-y-6">
        
        {/* Header */}
        <div className="bg-black/40 backdrop-blur-sm border border-white/20 rounded-lg p-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <span className="text-xl mr-2">🔍</span>
              <h3 className="text-lg font-semibold text-white">Verification & Action Steps</h3>
            </div>
            <Badge variant="outline" className="bg-blue-500/20 text-blue-300 border-blue-400/30">
              Action Required
            </Badge>
          </div>
        </div>

        {/* Main Recommendations */}
        {categorizedRecommendations.length > 0 && (
          <div>
            <h4 className="text-md font-semibold text-blue-300 mb-3">
              📋 Primary Recommendations
            </h4>
            <div className="space-y-3">
              {categorizedRecommendations.map((rec, index) => (                <VerificationItem 
                  key={index}
                  suggestion={rec.text}
                  priority={rec.priority}
                />
              ))}
            </div>
          </div>
        )}

        {/* Risk Mitigation Steps */}
        {categorizedMitigation.length > 0 && (
          <div>
            <h4 className="text-md font-semibold text-yellow-300 mb-3">
              🛡️ Risk Mitigation Steps
            </h4>
            <div className="space-y-3">
              {categorizedMitigation.map((mitigation, index) => (                <VerificationItem 
                  key={index}
                  suggestion={mitigation.text}
                  priority={mitigation.priority}
                />
              ))}
            </div>
          </div>
        )}

        {/* Follow-up Questions */}
        {followUpQuestions.length > 0 && (
          <div>
            <h4 className="text-md font-semibold text-green-300 mb-3">
              ❓ Suggested Follow-up Questions
            </h4>
            <div className="space-y-3">
              {followUpQuestions.map((question, index) => (
                <div key={index} className="bg-green-500/20 backdrop-blur-sm border border-green-400/30 rounded-lg p-4">
                  <div className="flex items-start">
                    <span className="text-lg mr-3 mt-0.5">❓</span>
                    <p className="text-gray-200 text-sm leading-relaxed font-medium">
                      {question}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Unverified Claims */}
        {unverifiedClaims.length > 0 && (
          <div>
            <h4 className="text-md font-semibold text-red-300 mb-3">
              🔍 Claims Requiring Fact-Checking
            </h4>
            <div className="space-y-3">
              {unverifiedClaims.map((claim, index) => (
                <div key={index} className="bg-red-500/20 backdrop-blur-sm border border-red-400/30 rounded-lg p-4">
                  <div className="flex items-start">
                    <span className="text-lg mr-3 mt-0.5">🔍</span>
                    <div className="flex-1">
                      <p className="text-gray-200 text-sm leading-relaxed">
                        {claim}
                      </p>
                      <div className="mt-2">
                        <Badge variant="outline" className="text-xs text-red-300 bg-black/20 border-red-400/30">
                          Fact-Check Required
                        </Badge>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Summary */}
        <div className="bg-black/20 backdrop-blur-sm border border-white/10 rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <h4 className="text-sm font-semibold text-gray-300">Verification Summary</h4>
            <div className="flex gap-2">
              <Badge variant="outline" className="text-xs bg-red-500/20 text-red-300 border-red-400/30">
                {categorizedRecommendations.filter(r => r.priority === 'high').length + 
                 categorizedMitigation.filter(r => r.priority === 'high').length} High Priority
              </Badge>
              <Badge variant="outline" className="text-xs bg-yellow-500/20 text-yellow-300 border-yellow-400/30">
                {categorizedRecommendations.filter(r => r.priority === 'medium').length + 
                 categorizedMitigation.filter(r => r.priority === 'medium').length} Medium Priority
              </Badge>
            </div>
          </div>
          <p className="text-gray-400 text-xs">
            Complete these verification steps to ensure accurate assessment and mitigate identified risks.
          </p>
        </div>
      </CardContent>
    </Card>
  );
};

export default VerificationSuggestionsCard;
