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
import EnhancedUnderstandingCard from './EnhancedUnderstandingCard';
import SessionInsightsCard from './SessionInsightsCard';
import QuantitativeMetricsCard from './QuantitativeMetricsCard';
import AudioAnalysisCard from './AudioAnalysisCard';
import VerificationSuggestionsCard from './VerificationSuggestionsCard';

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
        {summary.communication_style && (
          <div className="bg-black/20 backdrop-blur-sm p-3 rounded-lg border border-green-400/30">
            <span className="font-semibold text-green-300">💬 Communication Style:</span>
            <p className="text-gray-200 mt-1 whitespace-pre-wrap">{summary.communication_style}</p>
          </div>
        )}
        {summary.emotional_state && (
          <div className="bg-black/20 backdrop-blur-sm p-3 rounded-lg border border-yellow-400/30">
            <span className="font-semibold text-yellow-300">😊 Emotional State:</span>
            <p className="text-gray-200 mt-1 whitespace-pre-wrap">{summary.emotional_state}</p>
          </div>
        )}
        {summary.strengths && (
          <div className="bg-green-500/20 backdrop-blur-sm p-3 rounded-lg border border-green-400/30">
            <span className="font-semibold text-green-300">✅ Strengths:</span>
            <p className="text-gray-200 mt-1 whitespace-pre-wrap">{summary.strengths}</p>
          </div>  
        )}
        {summary.key_concerns && (
          <div className="bg-red-500/20 backdrop-blur-sm p-3 rounded-lg border border-red-400/30">
            <span className="font-semibold text-red-300">⚠️ Key Concerns:</span>
            <p className="text-gray-200 mt-1 whitespace-pre-wrap">{summary.key_concerns}</p>
          </div>
        )}
      </div>
    );
  }

  // Handle string case
  return (
    <div className="bg-black/30 backdrop-blur-sm border border-white/20 rounded-lg p-4">
      <p className="text-gray-200 whitespace-pre-wrap">{summary}</p>
    </div>
  );
};

const LinguisticAnalysisCard = ({ analysis }) => (
  <div className="space-y-3">
    {analysis.speech_patterns && (
      <div className="bg-black/20 backdrop-blur-sm p-3 rounded-lg border border-blue-400/30">
        <span className="font-semibold text-blue-300">🎵 Speech Patterns:</span>
        <p className="text-gray-200 mt-1 whitespace-pre-wrap">{analysis.speech_patterns}</p>
      </div>
    )}
    {analysis.word_choice && (
      <div className="bg-black/20 backdrop-blur-sm p-3 rounded-lg border border-purple-400/30">
        <span className="font-semibold text-purple-300">🗣️ Word Choice:</span>
        <p className="text-gray-200 mt-1 whitespace-pre-wrap">{analysis.word_choice}</p>
      </div>
    )}
    {analysis.emotional_consistency && (
      <div className="bg-black/20 backdrop-blur-sm p-3 rounded-lg border border-yellow-400/30">
        <span className="font-semibold text-yellow-300">😊 Emotional Consistency:</span>
        <p className="text-gray-200 mt-1 whitespace-pre-wrap">{analysis.emotional_consistency}</p>
      </div>
    )}
    {analysis.grammar_complexity && (
      <div className="bg-black/20 backdrop-blur-sm p-3 rounded-lg border border-green-400/30">
        <span className="font-semibold text-green-300">📝 Grammar Complexity:</span>
        <p className="text-gray-200 mt-1 whitespace-pre-wrap">{analysis.grammar_complexity}</p>
      </div>
    )}
  </div>
);

const SpeakerSpecificAnalysisCard = ({ analysis }) => (
  <div className="space-y-4">
    {Object.entries(analysis).map(([speaker, data], index) => (
      <div key={index} className="bg-black/20 backdrop-blur-sm border border-white/20 rounded-lg p-4">
        <h4 className="text-lg font-semibold text-white mb-3">👤 {speaker}</h4>
        <div className="space-y-3">
          {data.behavior_patterns && (
            <div className="bg-blue-500/10 backdrop-blur-sm p-3 rounded-lg border border-blue-400/30">
              <span className="font-semibold text-blue-300">🔍 Behavior Patterns:</span>
              <p className="text-gray-200 mt-1 text-sm">{data.behavior_patterns}</p>
            </div>
          )}
          {data.credibility_indicators && (
            <div className="bg-green-500/10 backdrop-blur-sm p-3 rounded-lg border border-green-400/30">
              <span className="font-semibold text-green-300">✅ Credibility:</span>
              <p className="text-gray-200 mt-1 text-sm">{data.credibility_indicators}</p>
            </div>
          )}
          {data.deception_flags && data.deception_flags.length > 0 && (
            <div className="bg-red-500/10 backdrop-blur-sm p-3 rounded-lg border border-red-400/30">
              <span className="font-semibold text-red-300">🚩 Deception Flags:</span>
              <ul className="text-gray-200 mt-1 text-sm space-y-1">
                {data.deception_flags.map((flag, flagIndex) => (
                  <li key={flagIndex}>• {flag}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>
    ))}
  </div>
);

const SpeakerTranscriptsCard = ({ transcripts }) => (
  <div className="space-y-4">
    {Object.entries(transcripts).map(([speaker, transcript], index) => (
      <div key={index} className="bg-black/20 backdrop-blur-sm border border-white/20 rounded-lg p-4">
        <h4 className="text-lg font-semibold text-white mb-3">👤 {speaker}</h4>
        <div className="bg-black/40 rounded-lg p-3 max-h-96 overflow-y-auto">
          <p className="text-gray-200 text-sm whitespace-pre-wrap font-mono leading-relaxed">
            {transcript}
          </p>
        </div>
      </div>
    ))}
  </div>
);

const RecommendationsCard = ({ recommendations }) => {
  if (Array.isArray(recommendations)) {
    return (
      <div className="space-y-3">
        {recommendations.map((rec, index) => (
          <div key={index} className="bg-blue-500/20 backdrop-blur-sm border border-blue-400/30 rounded-lg p-4">
            <p className="text-blue-100">{rec}</p>
          </div>
        ))}
      </div>
    );
  }

  if (typeof recommendations === 'string') {
    return (
      <div className="bg-blue-500/20 backdrop-blur-sm border border-blue-400/30 rounded-lg p-4">
        <p className="text-blue-100 whitespace-pre-wrap">{recommendations}</p>
      </div>
    );
  }

  // Handle object case with specific recommendation types
  return (
    <div className="space-y-3">
      {Object.entries(recommendations).map(([type, content], index) => (
        <div key={index} className="bg-blue-500/20 backdrop-blur-sm border border-blue-400/30 rounded-lg p-4">
          <span className="font-semibold text-blue-300 capitalize">{type.replace('_', ' ')}:</span>
          <p className="text-blue-100 mt-1">{content}</p>
        </div>
      ))}
    </div>
  );
};

const DebugInfoCard = ({ metadata }) => (
  <div className="bg-black/30 backdrop-blur-sm border border-white/20 rounded-lg p-4">
    <div className="space-y-2 text-xs">
      <div className="grid grid-cols-2 gap-4">
        <div>
          <span className="text-gray-400">Processing Time:</span>
          <span className="text-gray-200 ml-2">{metadata?.processing_time || 'N/A'}</span>
        </div>
        <div>
          <span className="text-gray-400">Model Used:</span>
          <span className="text-gray-200 ml-2">{metadata?.model_version || 'N/A'}</span>
        </div>
        <div>
          <span className="text-gray-400">Analysis Confidence:</span>
          <span className="text-gray-200 ml-2">{metadata?.confidence_level || 'N/A'}</span>
        </div>
        <div>
          <span className="text-gray-400">Data Points:</span>
          <span className="text-gray-200 ml-2">{metadata?.data_points || 'N/A'}</span>
        </div>
      </div>
    </div>
  </div>
);

const AIDeepAnalysisSection = ({ result }) => {
  if (!result) return null;

  const {
    gemini_data,
    linguistic_analysis,
    speaker_analysis,
    transcript_analysis,
    manipulation_assessment,
    argument_analysis,
    speaker_attitude,
    recommendations,
    enhanced_understanding,
    session_insights,
    quantitative_metrics,
    audio_analysis,
    metadata
  } = result;

  if (gemini_data?.error) {
    return <AnalysisErrorCard geminiData={gemini_data} />;
  }

  const defaultOpenValues = ["item-ai-summary", "item-linguistic-analysis"];

  return (
    <div className="space-y-6 h-fit">
      <Accordion type="multiple" defaultValue={defaultOpenValues} className="space-y-4">
        
        {/* AI Summary */}
        {gemini_data?.gemini_summary && (
          <AccordionItem value="item-ai-summary" className="bg-white/10 backdrop-blur-md border-white/20 shadow-xl rounded-lg">
            <AccordionTrigger className="text-xl font-semibold text-white p-6 hover:bg-slate-700/30 rounded-md">
              🤖 AI Deep Analysis Summary
            </AccordionTrigger>
            <AccordionContent className="pt-0 pb-6 px-6">
              <GeminiSummaryCard summary={gemini_data.gemini_summary} />
            </AccordionContent>
          </AccordionItem>
        )}

        {/* Linguistic Analysis */}
        {linguistic_analysis && (
          <AccordionItem value="item-linguistic-analysis" className="bg-white/10 backdrop-blur-md border-white/20 shadow-xl rounded-lg">
            <AccordionTrigger className="text-xl font-semibold text-white p-6 hover:bg-slate-700/30 rounded-md">
              📊 Linguistic Analysis
            </AccordionTrigger>
            <AccordionContent className="pt-0 pb-6 px-6">
              <LinguisticAnalysisCard analysis={linguistic_analysis} />
            </AccordionContent>
          </AccordionItem>
        )}

        {/* Speaker-Specific Analysis */}
        {speaker_analysis && Object.keys(speaker_analysis).length > 0 && (
          <AccordionItem value="item-speaker-analysis" className="bg-white/10 backdrop-blur-md border-white/20 shadow-xl rounded-lg">
            <AccordionTrigger className="text-xl font-semibold text-white p-6 hover:bg-slate-700/30 rounded-md">
              👥 Speaker Analysis
            </AccordionTrigger>
            <AccordionContent className="pt-0 pb-6 px-6">
              <SpeakerSpecificAnalysisCard analysis={speaker_analysis} />
            </AccordionContent>
          </AccordionItem>
        )}

        {/* Transcripts */}
        {transcript_analysis && Object.keys(transcript_analysis).length > 0 && (
          <AccordionItem value="item-transcripts" className="bg-white/10 backdrop-blur-md border-white/20 shadow-xl rounded-lg">
            <AccordionTrigger className="text-xl font-semibold text-white p-6 hover:bg-slate-700/30 rounded-md">
              📝 Speaker Transcripts
            </AccordionTrigger>
            <AccordionContent className="pt-0 pb-6 px-6">
              <SpeakerTranscriptsCard transcripts={transcript_analysis} />
            </AccordionContent>
          </AccordionItem>
        )}

        {/* Manipulation Assessment */}
        {manipulation_assessment && (
          <AccordionItem value="item-manipulation" className="bg-white/10 backdrop-blur-md border-white/20 shadow-xl rounded-lg">
            <AccordionTrigger className="text-xl font-semibold text-white p-6 hover:bg-slate-700/30 rounded-md">
              🎭 Manipulation Assessment
            </AccordionTrigger>
            <AccordionContent className="pt-0 pb-6 px-6">
              <ManipulationAssessmentCard assessment={manipulation_assessment} />
            </AccordionContent>
          </AccordionItem>
        )}

        {/* Argument Analysis */}
        {argument_analysis && (
          <AccordionItem value="item-arguments" className="bg-white/10 backdrop-blur-md border-white/20 shadow-xl rounded-lg">
            <AccordionTrigger className="text-xl font-semibold text-white p-6 hover:bg-slate-700/30 rounded-md">
              💭 Argument Analysis
            </AccordionTrigger>
            <AccordionContent className="pt-0 pb-6 px-6">
              <ArgumentAnalysisCard analysis={argument_analysis} />
            </AccordionContent>
          </AccordionItem>
        )}

        {/* Speaker Attitude */}
        {speaker_attitude && (
          <AccordionItem value="item-attitude" className="bg-white/10 backdrop-blur-md border-white/20 shadow-xl rounded-lg">
            <AccordionTrigger className="text-xl font-semibold text-white p-6 hover:bg-slate-700/30 rounded-md">
              😤 Speaker Attitude
            </AccordionTrigger>
            <AccordionContent className="pt-0 pb-6 px-6">
              <SpeakerAttitudeCard attitude={speaker_attitude} />
            </AccordionContent>
          </AccordionItem>
        )}

        {/* Enhanced Understanding */}
        {enhanced_understanding && (
          <AccordionItem value="item-enhanced-understanding" className="bg-white/10 backdrop-blur-md border-white/20 shadow-xl rounded-lg">
            <AccordionTrigger className="text-xl font-semibold text-white p-6 hover:bg-slate-700/30 rounded-md">
              🧠 Enhanced Understanding
            </AccordionTrigger>
            <AccordionContent className="pt-0 pb-6 px-6">
              <EnhancedUnderstandingCard understanding={enhanced_understanding} />
            </AccordionContent>
          </AccordionItem>
        )}

        {/* Session Insights */}
        {session_insights && (
          <AccordionItem value="item-session-insights" className="bg-white/10 backdrop-blur-md border-white/20 shadow-xl rounded-lg">
            <AccordionTrigger className="text-xl font-semibold text-white p-6 hover:bg-slate-700/30 rounded-md">
              🔄 Session Insights
            </AccordionTrigger>
            <AccordionContent className="pt-0 pb-6 px-6">
              <SessionInsightsCard insights={session_insights} />
            </AccordionContent>
          </AccordionItem>
        )}

        {/* Quantitative Metrics */}
        {(quantitative_metrics || linguistic_analysis) && (
          <AccordionItem value="item-quantitative-metrics" className="bg-white/10 backdrop-blur-md border-white/20 shadow-xl rounded-lg">
            <AccordionTrigger className="text-xl font-semibold text-white p-6 hover:bg-slate-700/30 rounded-md">
              📊 Quantitative Metrics
            </AccordionTrigger>
            <AccordionContent className="pt-0 pb-6 px-6">
              <QuantitativeMetricsCard analysis={quantitative_metrics || linguistic_analysis} />
            </AccordionContent>
          </AccordionItem>
        )}

        {/* Audio Analysis */}
        {audio_analysis && (
          <AccordionItem value="item-audio-analysis" className="bg-white/10 backdrop-blur-md border-white/20 shadow-xl rounded-lg">
            <AccordionTrigger className="text-xl font-semibold text-white p-6 hover:bg-slate-700/30 rounded-md">
              🎵 Audio Analysis
            </AccordionTrigger>
            <AccordionContent className="pt-0 pb-6 px-6">
              <AudioAnalysisCard audioAnalysis={audio_analysis} />
            </AccordionContent>
          </AccordionItem>
        )}

        {/* Recommendations */}
        {recommendations && (
          <AccordionItem value="item-recommendations" className="bg-white/10 backdrop-blur-md border-white/20 shadow-xl rounded-lg">
            <AccordionTrigger className="text-xl font-semibold text-white p-6 hover:bg-slate-700/30 rounded-md">
              💡 Recommendations
            </AccordionTrigger>
            <AccordionContent className="pt-0 pb-6 px-6">
              <RecommendationsCard recommendations={recommendations} />
            </AccordionContent>
          </AccordionItem>
        )}

        {/* Verification Suggestions */}
        <AccordionItem value="item-verification" className="bg-white/10 backdrop-blur-md border-white/20 shadow-xl rounded-lg">
          <AccordionTrigger className="text-xl font-semibold text-white p-6 hover:bg-slate-700/30 rounded-md">
            🔍 Verification & Action Steps
          </AccordionTrigger>
          <AccordionContent className="pt-0 pb-6 px-6">
            <VerificationSuggestionsCard result={result} />
          </AccordionContent>
        </AccordionItem>

        {/* Debug Information */}
        {metadata && (
          <AccordionItem value="item-debug" className="bg-white/10 backdrop-blur-md border-white/20 shadow-xl rounded-lg">
            <AccordionTrigger className="text-xl font-semibold text-white p-6 hover:bg-slate-700/30 rounded-md">
              🔧 Debug Information
            </AccordionTrigger>
            <AccordionContent className="pt-0 pb-6 px-6">
              <DebugInfoCard metadata={metadata} />
            </AccordionContent>
          </AccordionItem>
        )}
      </Accordion>
    </div>
  );
};

export default AIDeepAnalysisSection;
