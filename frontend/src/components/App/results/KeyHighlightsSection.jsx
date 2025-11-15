import React from 'react';
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge"; // For risk assessment
import {
  deriveConversationGuidanceFromServices,
  deriveCredibilityScoreFromServices,
  deriveRecommendationsFromServices,
  deriveRedFlagsFromServices,
  deriveRiskAssessmentFromServices,
  deriveSummaryFromServices,
  getServicesFromResult,
} from "@/lib/serviceSelectors";

// Utility function to truncate text
const getConciseText = (text, maxLength = 80) => {
  if (!text || typeof text !== 'string') return '';
  return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
};

const KeyHighlightsSection = ({ result, services, getCredibilityColor, getCredibilityLabel }) => {
  if (!result) {
    return null;
  }

  const serviceMap = services || getServicesFromResult(result);
  const credibility_score = deriveCredibilityScoreFromServices(serviceMap, result.credibility_score);
  const risk_assessment = deriveRiskAssessmentFromServices(serviceMap, result.risk_assessment);
  const red_flags_per_speaker = deriveRedFlagsFromServices(serviceMap, result.red_flags_per_speaker);
  const gemini_summary = deriveSummaryFromServices(serviceMap, result.gemini_summary);
  const recommendations = deriveRecommendationsFromServices(serviceMap, result.recommendations);
  const enhanced_understanding = deriveConversationGuidanceFromServices(serviceMap, result.enhanced_understanding);
  const fallbackCredibilityColor = getCredibilityColor || (() => "text-gray-300");
  const fallbackCredibilityLabel = getCredibilityLabel || (() => "N/A");

  const getRiskColorClasses = (riskLevel) => {
    if (riskLevel === 'high') return 'bg-red-500/30 text-red-200 border-red-400/50';
    if (riskLevel === 'medium') return 'bg-yellow-500/30 text-yellow-200 border-yellow-400/50';
    if (riskLevel === 'low') return 'bg-green-500/30 text-green-200 border-green-400/50';
    return 'bg-gray-500/30 text-gray-200 border-gray-400/50';
  };

  const getCredibilityGradientClass = (score) => {
    const level = score / 100;
    if (level < 0.4) return "bg-gradient-to-r from-red-700 to-red-500"; // Low (0-39)
    if (level < 0.7) return "bg-gradient-to-r from-yellow-600 to-yellow-400"; // Medium (40-69)
    return "bg-gradient-to-r from-green-600 to-green-400"; // High (70-100)
  };

  // getConciseText was added in a previous step, ensure it's preserved.
  // For brevity, assuming getConciseText is correctly defined above this part of the diff.
  // If it's not, the diff would need to include it or be adjusted.
  // For this operation, we are focusing on adding getCredibilityGradientClass
  // and modifying the progress bar.

  const allRedFlags = red_flags_per_speaker
    ? Object.values(red_flags_per_speaker).flat()
    : [];
  return (
    <Card className="section-container glow-purple bg-gradient-to-br from-purple-600/20 via-blue-600/20 to-indigo-600/20 backdrop-blur-lg border-white/20 shadow-2xl">
      <CardContent className="p-6">
        <h2 className="text-2xl font-bold text-white mb-6 text-center">✨ Key Highlights ✨</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">

          {/* 1. Overall Credibility Score */}
          {credibility_score !== undefined && credibility_score !== null && (
            <div className="bg-black/30 backdrop-blur-sm border border-white/20 rounded-lg p-5 flex flex-col items-center justify-center text-center">
              <h3 className="text-lg font-semibold text-white mb-3">🎯 Overall Credibility</h3>
              <div className={`text-5xl font-bold ${fallbackCredibilityColor(credibility_score / 100)} mb-2`}>
                {credibility_score}/100
              </div>
              <div className={`text-xl font-semibold ${fallbackCredibilityColor(credibility_score / 100)} mb-3`}>
                {fallbackCredibilityLabel(credibility_score / 100)}
              </div>              <div className="w-full bg-black/30 rounded-full h-2.5">
                <div
                  className={`h-2.5 rounded-full ${getCredibilityGradientClass(credibility_score)}`}
                  style={{ width: `${credibility_score}%` }}
                ></div>
              </div>
            </div>
          )}

          {/* 2. Overall Risk Assessment */}
          {risk_assessment?.overall_risk && (
            <div className="bg-black/30 backdrop-blur-sm border border-white/20 rounded-lg p-5 flex flex-col items-center justify-center text-center">
              <h3 className="text-lg font-semibold text-white mb-3">⚠️ Overall Risk</h3>
              <Badge className={`px-6 py-3 text-2xl font-bold ${getRiskColorClasses(risk_assessment.overall_risk)}`}>
                {risk_assessment.overall_risk.toUpperCase()}
              </Badge>
              <p className="text-xs text-gray-400 mt-3">
                Deception risk based on detected patterns and behavioral indicators.
              </p>
            </div>
          )}

          {/* 3. AI Insights Summary (Fallback if specific fields are missing) */}
          {gemini_summary && (
            <div className="bg-black/30 backdrop-blur-sm border border-white/20 rounded-lg p-5 md:col-span-2 lg:col-span-1">
              <h3 className="text-lg font-semibold text-white mb-3 text-center">💡 AI Insights Summary</h3>
              <div className="text-sm text-gray-300 space-y-2 text-center">
                {gemini_summary.credibility && (
                  <p><strong className="text-purple-300">Credibility:</strong> {getConciseText(gemini_summary.credibility, 80)}</p>
                )}
                {gemini_summary.key_concerns && (
                  <p><strong className="text-yellow-300">Concerns:</strong> {getConciseText(gemini_summary.key_concerns, 80)}</p>
                )}
                {(!gemini_summary.credibility && !gemini_summary.key_concerns && typeof gemini_summary === 'string') &&
                  <p>{gemini_summary.substring(0, 160)}{gemini_summary.length > 160 ? '...' : ''}</p>
                }
              </div>
            </div>
          )}

          {/* 4. Key Deception Indicators (If any) */}
          {allRedFlags.length > 0 && (
             <div className="bg-black/30 backdrop-blur-sm border border-white/20 rounded-lg p-5 md:col-span-2 lg:col-span-3"> {/* Spans more columns */}
              <h3 className="text-lg font-semibold text-white mb-3 text-center">🚩 Key Deception Indicators</h3>
              <div className="space-y-2 max-h-32 overflow-y-auto">
                {allRedFlags.map((flag, index) => (
                  <div key={index} className="bg-red-500/20 backdrop-blur-sm border border-red-400/30 rounded-md p-2">
                    <p className="text-red-200 text-sm">⚠️ {flag}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
           {allRedFlags.length === 0 && red_flags_per_speaker && ( // Only show if red_flags_per_speaker was checked
             <div className="bg-black/30 backdrop-blur-sm border border-white/20 rounded-lg p-5 md:col-span-2 lg:col-span-3">
              <h3 className="text-lg font-semibold text-white mb-3 text-center">🚩 Key Deception Indicators</h3>
              <div className="bg-green-500/20 backdrop-blur-sm border border-green-400/30 rounded-md p-3 text-center">
                <p className="text-green-200 text-sm">✅ No significant deception indicators detected across speakers.</p>
              </div>
            </div>
          )}
        </div>

        {/* Actionable Recommendations Section */}
        {(recommendations && recommendations.length > 0) && (
          <div className="md:col-span-2 lg:col-span-3 mt-6">
            <h3 className="text-xl font-semibold text-white mb-4 text-left flex items-center">
              <span className="mr-2">💡</span> Actionable Recommendations
            </h3>
            <div className="bg-black/30 backdrop-blur-sm border border-white/20 rounded-lg p-4 space-y-3">
              {recommendations.map((rec, index) => (
                <div key={index} className="bg-black/20 backdrop-blur-sm p-3 rounded-lg border-l-4 border-green-400">
                  <div className="flex items-start">
                    <span className="bg-green-900/50 text-green-300 font-bold rounded-full w-6 h-6 flex items-center justify-center text-sm mr-3 mt-0.5 shrink-0">
                      {index + 1}
                    </span>
                    <p className="text-gray-200 leading-relaxed">{rec}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
        {(!recommendations || recommendations.length === 0) && (
           <div className="md:col-span-2 lg:col-span-3 mt-6">
            <h3 className="text-xl font-semibold text-white mb-4 text-left flex items-center">
              <span className="mr-2">💡</span> Actionable Recommendations
            </h3>
            <div className="bg-black/30 backdrop-blur-sm border border-white/20 rounded-lg p-4">
              <p className="text-gray-400 text-center">No specific recommendations provided at this time.</p>
            </div>
          </div>
        )}

        {/* Conversation Guidance Section */}
        {enhanced_understanding && (
          <div className="md:col-span-2 lg:col-span-3 mt-6">
            <h3 className="text-xl font-semibold text-white mb-4 text-left flex items-center">
              <span className="mr-2">🗣️</span> Conversation Guidance
            </h3>
            <div className="bg-black/30 backdrop-blur-sm border border-white/20 rounded-lg p-4 space-y-4">
              {enhanced_understanding.suggested_follow_up_questions && enhanced_understanding.suggested_follow_up_questions.length > 0 && (
                <div>
                  <h4 className="text-lg font-medium text-blue-300 mb-2">Suggested Follow-up Questions:</h4>
                  <ul className="space-y-2">
                    {enhanced_understanding.suggested_follow_up_questions.map((q, index) => (
                      <li key={index} className="bg-black/20 p-3 rounded-md border-l-4 border-blue-400 text-sm text-gray-300">
                        <span className="mr-2 text-blue-400">❓</span>{q}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {enhanced_understanding.key_inconsistencies && enhanced_understanding.key_inconsistencies.length > 0 && (
                <div>
                  <h4 className="text-lg font-medium text-red-300 mb-2">Key Inconsistencies:</h4>
                  <div className="space-y-1">
                    {enhanced_understanding.key_inconsistencies.map((item, index) => (
                      <div key={index} className="bg-black/20 p-2 rounded-md text-sm text-gray-300 flex items-start">
                        <span className="mr-2 text-red-400">⚠️</span>{item}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {enhanced_understanding.areas_of_evasiveness && enhanced_understanding.areas_of_evasiveness.length > 0 && (
                <div>
                  <h4 className="text-lg font-medium text-yellow-300 mb-2">Areas of Evasiveness:</h4>
                   <div className="space-y-1">
                    {enhanced_understanding.areas_of_evasiveness.map((item, index) => (
                      <div key={index} className="bg-black/20 p-2 rounded-md text-sm text-gray-300 flex items-start">
                        <span className="mr-2 text-yellow-400">🤫</span>{item}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {enhanced_understanding.unverified_claims && enhanced_understanding.unverified_claims.length > 0 && (
                <div>
                  <h4 className="text-lg font-medium text-purple-300 mb-2">Unverified Claims:</h4>
                  <div className="space-y-1">
                    {enhanced_understanding.unverified_claims.map((item, index) => (
                      <div key={index} className="bg-black/20 p-2 rounded-md text-sm text-gray-300 flex items-start">
                        <span className="mr-2 text-purple-400">🧐</span>{item}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {(!enhanced_understanding.suggested_follow_up_questions || enhanced_understanding.suggested_follow_up_questions.length === 0) &&
               (!enhanced_understanding.key_inconsistencies || enhanced_understanding.key_inconsistencies.length === 0) &&
               (!enhanced_understanding.areas_of_evasiveness || enhanced_understanding.areas_of_evasiveness.length === 0) &&
               (!enhanced_understanding.unverified_claims || enhanced_understanding.unverified_claims.length === 0) &&
                <p className="text-gray-400 text-center">No specific conversation guidance points identified.</p>
              }
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default KeyHighlightsSection;
