import React from 'react';
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

const ValidationStatus = ({ result, className = "" }) => {
  if (!result) {
    return null;
  }

  // Use the validation function from useAnalysisResults hook
  const validation = {
    isValid: true,
    errors: [],
    warnings: [],
    hasAdvancedAnalysis: !!(result.manipulation_assessment || result.argument_analysis || result.enhanced_understanding),
    hasSessionInsights: !!result.session_insights,
    hasAudioAnalysis: !!result.audio_analysis
  };

  // Check for missing data
  if (typeof result.credibility_score !== 'number') {
    validation.warnings.push('Missing credibility score');
  }
  
  if (!result.transcript && !result.speaker_transcripts) {
    validation.errors.push('No transcript data available');
    validation.isValid = false;
  }
  
  if (!result.gemini_summary) {
    validation.warnings.push('Missing Gemini summary analysis');
  }

  const getStatusColor = () => {
    if (validation.errors.length > 0) return 'red';
    if (validation.warnings.length > 0) return 'yellow';
    return 'green';
  };

  const getStatusIcon = () => {
    if (validation.errors.length > 0) return '❌';
    if (validation.warnings.length > 0) return '⚠️';
    return '✅';
  };

  const getStatusText = () => {
    if (validation.errors.length > 0) return 'Analysis Issues Detected';
    if (validation.warnings.length > 0) return 'Analysis Complete with Warnings';
    return 'Analysis Complete';
  };

  return (
    <Card className={`bg-black/20 backdrop-blur-sm border border-${getStatusColor()}-500/30 ${className}`}>
      <CardContent className="p-4">
        <div className="flex items-center justify-between mb-3">
          <h4 className="text-sm font-medium text-white flex items-center">
            <span className="mr-2">{getStatusIcon()}</span>
            Analysis Status
          </h4>
          <Badge className={`bg-${getStatusColor()}-500/30 text-${getStatusColor()}-200 border-${getStatusColor()}-400/50`}>
            {getStatusText()}
          </Badge>
        </div>

        {/* Feature availability indicators */}
        <div className="grid grid-cols-2 gap-2 text-xs">
          <div className={`flex items-center ${result.transcript || result.speaker_transcripts ? 'text-green-400' : 'text-gray-500'}`}>
            <span className="mr-1">{result.transcript || result.speaker_transcripts ? '✓' : '○'}</span>
            Transcript
          </div>
          <div className={`flex items-center ${typeof result.credibility_score === 'number' ? 'text-green-400' : 'text-gray-500'}`}>
            <span className="mr-1">{typeof result.credibility_score === 'number' ? '✓' : '○'}</span>
            Credibility Score
          </div>
          <div className={`flex items-center ${validation.hasAdvancedAnalysis ? 'text-green-400' : 'text-gray-500'}`}>
            <span className="mr-1">{validation.hasAdvancedAnalysis ? '✓' : '○'}</span>
            Advanced Analysis
          </div>
          <div className={`flex items-center ${validation.hasAudioAnalysis ? 'text-green-400' : 'text-gray-500'}`}>
            <span className="mr-1">{validation.hasAudioAnalysis ? '✓' : '○'}</span>
            Audio Analysis
          </div>
          <div className={`flex items-center ${validation.hasSessionInsights ? 'text-green-400' : 'text-gray-500'}`}>
            <span className="mr-1">{validation.hasSessionInsights ? '✓' : '○'}</span>
            Session Insights
          </div>
          <div className={`flex items-center ${result.recommendations ? 'text-green-400' : 'text-gray-500'}`}>
            <span className="mr-1">{result.recommendations ? '✓' : '○'}</span>
            Recommendations
          </div>
        </div>

        {/* Show errors and warnings */}
        {(validation.errors.length > 0 || validation.warnings.length > 0) && (
          <div className="mt-3 space-y-1">
            {validation.errors.map((error, index) => (
              <div key={`error-${index}`} className="text-xs text-red-400 bg-red-900/20 p-1 rounded">
                ❌ {error}
              </div>
            ))}
            {validation.warnings.map((warning, index) => (
              <div key={`warning-${index}`} className="text-xs text-yellow-400 bg-yellow-900/20 p-1 rounded">
                ⚠️ {warning}
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default ValidationStatus;
