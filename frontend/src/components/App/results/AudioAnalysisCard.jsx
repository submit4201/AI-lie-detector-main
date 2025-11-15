import React from 'react';
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

const AudioInsightSection = ({ title, content, icon, color = "blue" }) => {
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
        {content || "No audio analysis available for this aspect."}
      </p>
    </div>
  );
};

const AudioAnalysisCard = ({ audioAnalysis }) => {
  if (!audioAnalysis) {
    return (
      <Card className="bg-transparent shadow-none border-none rounded-none">
        <CardContent className="p-0">
          <div className="bg-black/30 backdrop-blur-sm border border-white/20 rounded-lg p-4">
            <p className="text-gray-400">Audio analysis not available. This requires audio file processing.</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  const {
    vocal_stress_indicators,
    speaking_rate_variations,
    pitch_analysis,
    pause_patterns,
    voice_quality
  } = audioAnalysis;

  // Check if we have any actual audio analysis content
  const hasContent = vocal_stress_indicators || speaking_rate_variations || 
                    pitch_analysis || pause_patterns || voice_quality;

  if (!hasContent) {
    return (
      <Card className="bg-transparent shadow-none border-none rounded-none">
        <CardContent className="p-0">
          <div className="bg-black/30 backdrop-blur-sm border border-white/20 rounded-lg p-4">
            <p className="text-gray-400">Audio analysis will appear when audio files are processed.</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="bg-transparent shadow-none border-none rounded-none">
      <CardContent className="p-0 space-y-4">
        
        {/* Header with audio indicator */}
        <div className="bg-black/40 backdrop-blur-sm border border-white/20 rounded-lg p-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <span className="text-xl mr-2">🎵</span>
              <h3 className="text-lg font-semibold text-white">Audio-Based Analysis</h3>
            </div>
            <Badge variant="outline" className="bg-purple-500/20 text-purple-300 border-purple-400/30">
              Voice Analysis
            </Badge>
          </div>
        </div>

        {/* Vocal Stress Indicators */}
        {vocal_stress_indicators && (
          <AudioInsightSection
            title="Vocal Stress Indicators"
            content={vocal_stress_indicators}
            icon="😰"
            color="red"
          />
        )}

        {/* Speaking Rate Variations */}
        {speaking_rate_variations && (
          <AudioInsightSection
            title="Speaking Rate Variations"
            content={speaking_rate_variations}
            icon="⚡"
            color="yellow"
          />
        )}

        {/* Pitch Analysis */}
        {pitch_analysis && (
          <AudioInsightSection
            title="Pitch Analysis"
            content={pitch_analysis}
            icon="🎼"
            color="blue"
          />
        )}

        {/* Pause Patterns */}
        {pause_patterns && (
          <AudioInsightSection
            title="Pause Patterns"
            content={pause_patterns}
            icon="⏸️"
            color="green"
          />
        )}

        {/* Voice Quality */}
        {voice_quality && (
          <AudioInsightSection
            title="Voice Quality Assessment"
            content={voice_quality}
            icon="🔊"
            color="purple"
          />
        )}

        {/* Footer note */}
        <div className="bg-black/20 backdrop-blur-sm border border-white/10 rounded-lg p-3">
          <p className="text-gray-400 text-xs">
            🎤 Audio analysis provides deeper insights beyond text, analyzing vocal patterns, stress, and authenticity markers.
          </p>
        </div>
      </CardContent>
    </Card>
  );
};

export default AudioAnalysisCard;
