import React from 'react';
import { Card, CardContent } from "@/components/ui/card";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import ManipulationAssessmentCard from './ManipulationAssessmentCard';
import ArgumentAnalysisCard from './ArgumentAnalysisCard';
import SpeakerAttitudeCard from './SpeakerAttitudeCard';

const AnalysisErrorCard = ({ geminiData }) => (
  <Card className="bg-white/10 backdrop-blur-md border-white/20 shadow-xl h-fit">
    <CardContent className="p-6">
      <h3 className="text-xl font-semibold text-white mb-4">❌ Analysis Error</h3>
      <div className="bg-red-500/20 backdrop-blur-sm border border-red-400/30 rounded-lg p-4">
        <p className="text-red-200">
          {geminiData?.error || 'Failed to process AI analysis'}
        </p>
        {geminiData?.gemini_summary && (
          <div className="mt-3 pt-3 border-t border-red-400/30">
            <p className="text-red-100 text-sm">{geminiData.gemini_summary}</p>
          </div>
        )}
      </div>
    </CardContent>
  </Card>
);

const GeminiSummaryCard = ({ summary }) => {
  if (typeof summary === 'object') {
    return (
      <div className="space-y-3">
        {summary.tone && (
          <div className="bg-black/20 backdrop-blur-sm p-3 rounded-lg border border-purple-400/30">
            <span className="font-semibold text-purple-300">🎭 Tone Analysis:</span>
            <p className="text-gray-200 mt-1 whitespace-pre-wrap">{summary.tone}</p>
          </div>
        )}
        {summary.motivation && (
          <div className="bg-black/20 backdrop-blur-sm p-3 rounded-lg border border-blue-400/30">
            <span className="font-semibold text-blue-300">🎯 Motivation Assessment:</span>
            <p className="text-gray-200 mt-1 whitespace-pre-wrap">{summary.motivation}</p>
          </div>
        )}
        {summary.credibility && (
          <div className="bg-black/20 backdrop-blur-sm p-3 rounded-lg border border-green-400/30">
            <span className="font-semibold text-green-300">✅ Credibility Analysis:</span>
            <p className="text-gray-200 mt-1 whitespace-pre-wrap">{summary.credibility}</p>
          </div>
        )}
        {summary.emotional_state && (
          <div className="bg-black/20 backdrop-blur-sm p-3 rounded-lg border border-yellow-400/30">
            <span className="font-semibold text-yellow-300">😊 Emotional State:</span>
            <p className="text-gray-200 mt-1 whitespace-pre-wrap">{summary.emotional_state}</p>
          </div>
        )}
        {summary.communication_style && (
          <div className="bg-black/20 backdrop-blur-sm p-3 rounded-lg border border-cyan-400/30">
            <span className="font-semibold text-cyan-300">💬 Communication Style:</span>
            <p className="text-gray-200 mt-1 whitespace-pre-wrap">{summary.communication_style}</p>
          </div>
        )}
      </div>
    );
  }
  return (
    <p className="text-gray-200 leading-relaxed whitespace-pre-wrap">{summary}</p>
  );
};

const SessionInsightsCard = ({ insights }) => {
  return (
    <div className="space-y-3">
      {insights.consistency_analysis && (
        <div className="bg-blue-500/10 backdrop-blur-sm p-3 rounded-lg border border-blue-400/30">
          <span className="font-semibold text-blue-300">🔍 Consistency Analysis:</span>
          <p className="text-gray-200 mt-1 whitespace-pre-wrap">{insights.consistency_analysis}</p>
        </div>
      )}
      {insights.behavioral_evolution && (
        <div className="bg-orange-500/10 backdrop-blur-sm p-3 rounded-lg border border-orange-400/30">
          <span className="font-semibold text-orange-300">📈 Behavioral Evolution:</span>
          <p className="text-gray-200 mt-1 whitespace-pre-wrap">{insights.behavioral_evolution}</p>
        </div>
      )}
      {insights.risk_trajectory && (
        <div className="bg-red-500/10 backdrop-blur-sm p-3 rounded-lg border border-red-400/30">
          <span className="font-semibold text-red-300">⚠️ Risk Trajectory:</span>
          <p className="text-gray-200 mt-1 whitespace-pre-wrap">{insights.risk_trajectory}</p>
        </div>
      )}
      {insights.conversation_dynamics && (
        <div className="bg-green-500/10 backdrop-blur-sm p-3 rounded-lg border border-green-400/30">
          <span className="font-semibold text-green-300">💬 Conversation Dynamics:</span>
          <p className="text-gray-200 mt-1 whitespace-pre-wrap">{insights.conversation_dynamics}</p>
        </div>
      )}
    </div>
  );
};

const LinguisticAnalysisCard = ({ analysis }) => {
  return (
    <div className="space-y-3">
      {analysis.speech_patterns && (
        <div className="bg-black/20 backdrop-blur-sm p-3 rounded-lg border border-blue-400/30">
          <span className="font-semibold text-blue-300">🎵 Speech Patterns:</span>
          <p className="text-gray-200 mt-1 whitespace-pre-wrap">{analysis.speech_patterns}</p>
        </div>
      )}
      {analysis.word_choice && (
        <div className="bg-black/20 backdrop-blur-sm p-3 rounded-lg border border-purple-400/30">
          <span className="font-semibold text-purple-300">📖 Word Choice:</span>
          <p className="text-gray-200 mt-1 whitespace-pre-wrap">{analysis.word_choice}</p>
        </div>
      )}
      {analysis.emotional_consistency && (
        <div className="bg-black/20 backdrop-blur-sm p-3 rounded-lg border border-yellow-400/30">
          <span className="font-semibold text-yellow-300">💭 Emotional Consistency:</span>
          <p className="text-gray-200 mt-1 whitespace-pre-wrap">{analysis.emotional_consistency}</p>
        </div>
      )}
      {analysis.detail_level && (
        <div className="bg-black/20 backdrop-blur-sm p-3 rounded-lg border border-green-400/30">
          <span className="font-semibold text-green-300">🔍 Detail Level:</span>
          <p className="text-gray-200 mt-1 whitespace-pre-wrap">{analysis.detail_level}</p>
        </div>
      )}
    </div>
  );
};

const SpeakerSpecificAnalysisCard = ({ analysis }) => {
  return (
    <div className="space-y-4">
      {Object.entries(analysis).map(([speaker, flags], index) => (
        <div key={index} className="bg-black/30 backdrop-blur-sm border border-white/20 rounded-lg p-4">
          <h4 className="text-white font-semibold mb-3">{speaker}</h4>
          {Array.isArray(flags) && flags.length > 0 ? (
            <div className="space-y-2">
              {flags.map((flag, flagIndex) => (
                <div key={flagIndex} className="bg-red-500/20 backdrop-blur-sm p-3 rounded-lg border border-red-400/30">
                  <span className="text-red-200">⚠️ {flag}</span>
                </div>
              ))}
            </div>
          ) : (
            <div className="bg-green-500/20 backdrop-blur-sm p-3 rounded-lg border border-green-400/30">
              <span className="text-green-200">✅ No significant indicators detected</span>
            </div>
          )}
        </div>
      ))}
    </div>
  );
};

const SpeakerTranscriptsCard = ({ transcripts }) => {
  return (
    <div className="space-y-3 max-h-96 overflow-y-auto">
      {Object.entries(transcripts).map(([speaker, transcript], index) => (
        <div key={index} className="bg-black/30 backdrop-blur-sm border border-white/20 rounded-lg p-4">
          <div className="flex items-center mb-2">
            <span className="bg-purple-900/50 text-purple-300 font-bold rounded-full w-8 h-8 flex items-center justify-center text-sm mr-3">
              {speaker.charAt(0).toUpperCase()}
            </span>
            <span className="text-white font-medium">{speaker}</span>
          </div>
          <p className="text-gray-200 leading-relaxed whitespace-pre-wrap text-sm pl-11">
            {transcript}
          </p>
        </div>
      ))}
    </div>
  );
};

const RecommendationsCard = ({ recommendations }) => {
  if (Array.isArray(recommendations)) {
    return (
      <div className="space-y-3">
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
    );
  }
  return (
    <p className="text-gray-200 leading-relaxed whitespace-pre-wrap">{recommendations}</p>
  );
};

const DebugInfoCard = ({ metadata }) => {
  return (
    <div className="space-y-3">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {Object.entries(metadata).map(([key, value], index) => (
          <div key={index} className="bg-black/30 backdrop-blur-sm border border-gray-600/30 rounded-lg p-3">
            <span className="text-gray-400 text-sm font-medium block mb-1">
              {key.replace(/_/g, ' ').toUpperCase()}:
            </span>
            <span className="text-gray-200 text-sm">
              {typeof value === 'object' ? JSON.stringify(value, null, 2) : String(value)}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
};

const AIDeepAnalysisSection = ({ result }) => {
  // The analysis result contains all the data directly, not in a gemini_data field
  if (!result || result.error) {
    return <AnalysisErrorCard geminiData={result} />;
  }
4
    <div className="space-y-6">
      {/* Accordion for AI Deep Analysis */}
      <Accordion type="multiple" className="w-full space-y-4">          {/* AI Summary */}
        {result.gemini_summary && (
          <AccordionItem value="ai-summary" className="bg-white/10 backdrop-blur-md border-white/20 rounded-lg">
            <AccordionTrigger className="text-white font-semibold">
              🤖 AI Summary Analysis
            </AccordionTrigger>
            <AccordionContent className="text-gray-200">
              <GeminiSummaryCard summary={result.gemini_summary} />
            </AccordionContent>
          </AccordionItem>
        )}        {/* Session Insights */}
        {result.session_insights && (
          <AccordionItem value="session-insights" className="bg-white/10 backdrop-blur-md border-white/20 rounded-lg">
            <AccordionTrigger className="text-white font-semibold">
              🔍 Session Insights
            </AccordionTrigger>
            <AccordionContent className="text-gray-200">
              <SessionInsightsCard insights={result.session_insights} />
            </AccordionContent>
          </AccordionItem>
        )}        {/* Linguistic Analysis */}
        {result.linguistic_analysis && (
          <AccordionItem value="linguistic-analysis" className="bg-white/10 backdrop-blur-md border-white/20 rounded-lg">
            <AccordionTrigger className="text-white font-semibold">
              🎵 Linguistic Analysis
            </AccordionTrigger>
            <AccordionContent className="text-gray-200">
              <LinguisticAnalysisCard analysis={result.linguistic_analysis} />
            </AccordionContent>
          </AccordionItem>
        )}        {/* Speaker-Specific Analysis */}
        {result.speaker_specific_analysis && (
          <AccordionItem value="speaker-analysis" className="bg-white/10 backdrop-blur-md border-white/20 rounded-lg">
            <AccordionTrigger className="text-white font-semibold">
              👥 Speaker-Specific Analysis
            </AccordionTrigger>
            <AccordionContent className="text-gray-200">
              <SpeakerSpecificAnalysisCard analysis={result.speaker_specific_analysis} />
            </AccordionContent>
          </AccordionItem>
        )}        {/* Speaker Transcripts */}
        {result.speaker_transcripts && (
          <AccordionItem value="speaker-transcripts" className="bg-white/10 backdrop-blur-md border-white/20 rounded-lg">
            <AccordionTrigger className="text-white font-semibold">
              🗣️ Speaker Transcripts
            </AccordionTrigger>
            <AccordionContent className="text-gray-200">
              <SpeakerTranscriptsCard transcripts={result.speaker_transcripts} />
            </AccordionContent>
          </AccordionItem>
        )}        {/* Recommendations */}
        {result.recommendations && (
          <AccordionItem value="recommendations" className="bg-white/10 backdrop-blur-md border-white/20 rounded-lg">
            <AccordionTrigger className="text-white font-semibold">
              💡 Recommendations
            </AccordionTrigger>
            <AccordionContent className="text-gray-200">
              <RecommendationsCard recommendations={result.recommendations} />
            </AccordionContent>
          </AccordionItem>
        )}        {/* Debug Information */}
        {result.metadata && (
          <AccordionItem value="debug-info" className="bg-white/10 backdrop-blur-md border-white/20 rounded-lg">
            <AccordionTrigger className="text-white font-semibold">
              🐛 Debug Information
            </AccordionTrigger>
            <AccordionContent className="text-gray-200">
              <DebugInfoCard metadata={result.metadata} />
            </AccordionContent>
          </AccordionItem>
        )}

      </Accordion>      {/* Standalone Cards for Manipulation, Argument, and Attitude Analysis */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {result.manipulation_assessment && (
          <ManipulationAssessmentCard assessment={result.manipulation_assessment} />
        )}
        {result.argument_analysis && (
          <ArgumentAnalysisCard analysis={result.argument_analysis} />
        )}
        {result.speaker_attitude && (
          <SpeakerAttitudeCard attitude={result.speaker_attitude} />
        )}
      </div>
    </div>
  );
};

export default AIDeepAnalysisSection;
