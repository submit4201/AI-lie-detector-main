import React, { useState } from 'react';
import { Card, CardContent } from "@/components/ui/card";

const TabButton = ({ isActive, onClick, children, icon }) => (
  <button
    onClick={onClick}
    className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-all duration-200 ${
      isActive 
        ? 'bg-blue-500/30 text-blue-300 border border-blue-400/50' 
        : 'bg-black/20 text-gray-400 hover:bg-white/10 hover:text-white border border-transparent'
    }`}
  >
    <span>{icon}</span>
    <span className="font-medium">{children}</span>
  </button>
);

const MetricCard = ({ title, value, unit, description, color = "blue", comparison, trend }) => (
  <div className={`bg-black/20 backdrop-blur-sm p-4 rounded-lg border border-${color}-400/30 hover:border-${color}-400/50 transition-all duration-200`}>
    <div className="flex justify-between items-start mb-2">
      <span className={`text-${color}-300 font-medium text-sm`}>{title}</span>
      <div className="text-right">
        <span className={`text-${color}-200 font-bold text-lg`}>
          {value !== null && value !== undefined ? `${value}${unit || ''}` : 'N/A'}
        </span>
        {trend && (
          <div className={`text-xs ${trend > 0 ? 'text-green-400' : trend < 0 ? 'text-red-400' : 'text-gray-400'}`}>
            {trend > 0 ? '↗' : trend < 0 ? '↘' : '→'} {Math.abs(trend).toFixed(1)}%
          </div>
        )}
      </div>
    </div>
    {comparison && (
      <div className="text-xs text-gray-300 mb-2 p-2 bg-white/5 rounded">
        💡 {comparison}
      </div>
    )}
    <div className="text-xs text-gray-400">{description}</div>
  </div>
);

const ProgressBar = ({ value, max = 100, color = "blue", label }) => (
  <div className="space-y-2">
    <div className="flex justify-between text-sm">
      <span className="text-gray-300">{label}</span>
      <span className={`text-${color}-300 font-medium`}>{value?.toFixed(1) || 0}/{max}</span>
    </div>
    <div className="w-full bg-black/30 rounded-full h-3">
      <div
        className={`h-3 rounded-full bg-gradient-to-r from-${color}-600 to-${color}-400 transition-all duration-500`}
        style={{width: `${Math.min((value || 0) / max * 100, 100)}%`}}
      ></div>
    </div>
  </div>
);

const ComprehensiveAnalysisSection = ({ result }) => {
  const [activeTab, setActiveTab] = useState('overview');
  if (!result || !result.linguistic_analysis) {
    return (
      <Card className="section-container analysis-breakdown">
        <CardContent className="p-6">
          <h3 className="text-xl font-semibold text-white mb-4">📊 Comprehensive Analysis</h3>
          <div className="bg-yellow-500/20 backdrop-blur-sm border border-yellow-400/30 rounded-lg p-4">
            <p className="text-yellow-200">📊 Analysis data not available - please perform audio analysis first</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  const { linguistic_analysis, emotional_analysis, audio_quality, session_insights } = result;

  const tabs = [
    { id: 'overview', label: 'Overview', icon: '📊' },
    { id: 'speech', label: 'Speech Patterns', icon: '🎵' },
    { id: 'psychology', label: 'Psychology', icon: '🧠' },
    { id: 'deception', label: 'Deception Indicators', icon: '🎯' },
    { id: 'session', label: 'Session Analysis', icon: '📈' },
  ];

  const renderOverviewTab = () => (
    <div className="space-y-6">
      {/* Key Metrics Summary */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Deception Risk"
          value={result.deception_probability?.toFixed(1)}
          unit="%"
          description="Overall likelihood of deceptive behavior"
          color={result.deception_probability > 70 ? "red" : result.deception_probability > 40 ? "yellow" : "green"}
          comparison={
            result.deception_probability > 70 ? "High risk - multiple indicators present" :
            result.deception_probability > 40 ? "Moderate risk - some indicators detected" :
            "Low risk - minimal deception indicators"
          }
        />
        
        <MetricCard
          title="Confidence Level"
          value={(linguistic_analysis.confidence_ratio * 100).toFixed(1)}
          unit="%"
          description="Speaker's certainty vs uncertainty ratio"
          color="blue"
          comparison={
            linguistic_analysis.confidence_ratio > 0.7 ? "High confidence in statements" :
            linguistic_analysis.confidence_ratio > 0.4 ? "Moderate confidence level" :
            "Low confidence or high uncertainty"
          }
        />

        <MetricCard
          title="Speech Formality"
          value={linguistic_analysis.formality_score?.toFixed(1)}
          unit="/100"
          description="Language formality and professionalism"
          color="purple"
          comparison={
            linguistic_analysis.formality_score > 70 ? "Formal/professional language" :
            linguistic_analysis.formality_score > 40 ? "Semi-formal communication" :
            "Casual/informal speech patterns"
          }
        />

        <MetricCard
          title="Emotional State"
          value={emotional_analysis?.dominant_emotion || "Unknown"}
          description="Primary emotional state detected"
          color="cyan"
          comparison={emotional_analysis?.confidence ? `${(emotional_analysis.confidence * 100).toFixed(1)}% confidence` : ""}
        />
      </div>

      {/* Visual Analysis Summary */}
      <Card className="bg-black/20 backdrop-blur-sm border border-white/20">
        <CardContent className="p-6">
          <h4 className="text-lg font-semibold text-white mb-4">📈 Analysis Breakdown</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <ProgressBar 
                value={linguistic_analysis.formality_score} 
                color="purple" 
                label="Language Formality"
              />
              <ProgressBar 
                value={linguistic_analysis.complexity_score} 
                color="indigo" 
                label="Linguistic Complexity"
              />
              <ProgressBar 
                value={(linguistic_analysis.confidence_ratio * 100)} 
                color="blue" 
                label="Confidence Level"
              />
            </div>
            <div className="space-y-4">
              <ProgressBar 
                value={100 - (linguistic_analysis.hesitation_count * 5)} 
                color="green" 
                label="Speech Fluency"
              />
              <ProgressBar 
                value={audio_quality?.clarity_score * 100 || 0} 
                color="cyan" 
                label="Audio Quality"
              />
              <ProgressBar 
                value={100 - result.deception_probability} 
                color={result.deception_probability > 50 ? "red" : "green"} 
                label="Truthfulness Score"
              />
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );

  const renderSpeechTab = () => (
    <div className="space-y-6">
      {/* Core Speech Metrics */}
      <Card className="bg-black/20 backdrop-blur-sm border border-blue-400/30">
        <CardContent className="p-6">
          <h4 className="text-lg font-semibold text-blue-300 mb-4">🎵 Core Speech Patterns</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <MetricCard
              title="Speech Rate"
              value={linguistic_analysis.speech_rate_wpm}
              unit=" WPM"
              description="Words per minute (normal: 140-180)"
              color="blue"
              comparison={
                linguistic_analysis.speech_rate_wpm < 120 ? "Slow pace - possible hesitation" :
                linguistic_analysis.speech_rate_wpm > 200 ? "Fast pace - possible nervousness" :
                "Normal speaking pace"
              }
            />
            
            <MetricCard
              title="Word Count"
              value={linguistic_analysis.word_count}
              description="Total words in analysis"
              color="green"
            />
            
            <MetricCard
              title="Sentence Structure"
              value={linguistic_analysis.avg_words_per_sentence?.toFixed(1)}
              unit=" words/sentence"
              description="Average sentence complexity"
              color="purple"
              comparison={
                linguistic_analysis.avg_words_per_sentence > 20 ? "Complex sentences" :
                linguistic_analysis.avg_words_per_sentence < 8 ? "Simple sentences" :
                "Moderate complexity"
              }
            />
          </div>
        </CardContent>
      </Card>

      {/* Hesitation Analysis */}
      <Card className="bg-black/20 backdrop-blur-sm border border-orange-400/30">
        <CardContent className="p-6">
          <h4 className="text-lg font-semibold text-orange-300 mb-4">⚡ Hesitation & Fluency</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <MetricCard
              title="Hesitation Markers"
              value={linguistic_analysis.hesitation_count}
              description="Um, uh, er, ah, like, you know"
              color="red"
              comparison={
                linguistic_analysis.hesitation_count > 10 ? "High hesitation detected" :
                linguistic_analysis.hesitation_count > 5 ? "Moderate hesitation" :
                "Fluent speech"
              }
            />
            
            <MetricCard
              title="Filler Words"
              value={linguistic_analysis.filler_count}
              description="Basic fillers: um, uh, er, ah"
              color="yellow"
            />
            
            <MetricCard
              title="Repetitions"
              value={linguistic_analysis.repetition_count}
              description="Word/phrase repetitions"
              color="pink"
            />
            
            <MetricCard
              title="Hesitation Rate"
              value={linguistic_analysis.hesitation_rate?.toFixed(1)}
              unit="/min"
              description="Hesitations per minute"
              color="orange"
              comparison={
                linguistic_analysis.hesitation_rate > 8 ? "Concerning frequency" :
                linguistic_analysis.hesitation_rate > 4 ? "Moderate frequency" :
                "Normal frequency"
              }
            />
          </div>
        </CardContent>
      </Card>
    </div>
  );

  const renderPsychologyTab = () => (
    <div className="space-y-6">
      {/* Confidence Analysis */}
      <Card className="bg-black/20 backdrop-blur-sm border border-green-400/30">
        <CardContent className="p-6">
          <h4 className="text-lg font-semibold text-green-300 mb-4">🎯 Confidence & Certainty</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <MetricCard
              title="Certainty Indicators"
              value={linguistic_analysis.certainty_count}
              description="Definitely, absolutely, sure, certain"
              color="green"
              comparison={
                linguistic_analysis.certainty_count > 8 ? "Very confident speaker" :
                linguistic_analysis.certainty_count > 4 ? "Moderately confident" :
                "Low confidence indicators"
              }
            />
            
            <MetricCard
              title="Uncertainty Qualifiers"
              value={linguistic_analysis.qualifier_count}
              description="Maybe, perhaps, might, probably"
              color="yellow"
              comparison={
                linguistic_analysis.qualifier_count > 8 ? "High uncertainty" :
                linguistic_analysis.qualifier_count > 4 ? "Some uncertainty" :
                "Low uncertainty"
              }
            />
            
            <div className="bg-black/20 backdrop-blur-sm p-4 rounded-lg border border-blue-400/30">
              <div className="text-blue-300 font-medium text-sm mb-3">Confidence Breakdown</div>
              <div className="space-y-3">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-400">Certain statements:</span>
                  <span className="text-green-300 font-semibold">{linguistic_analysis.certainty_count}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-400">Uncertain statements:</span>
                  <span className="text-yellow-300 font-semibold">{linguistic_analysis.qualifier_count}</span>
                </div>
                <ProgressBar 
                  value={linguistic_analysis.confidence_ratio * 100} 
                  color="blue" 
                  label="Overall Confidence"
                />
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Language Complexity */}
      <Card className="bg-black/20 backdrop-blur-sm border border-purple-400/30">
        <CardContent className="p-6">
          <h4 className="text-lg font-semibold text-purple-300 mb-4">🧠 Language Sophistication</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <ProgressBar 
                value={linguistic_analysis.formality_score} 
                color="purple" 
                label="Formality Score"
              />
              <div className="text-xs text-gray-400 mt-2">
                {linguistic_analysis.formality_score > 70 ? "🎓 Formal/Academic language" :
                 linguistic_analysis.formality_score > 40 ? "💼 Semi-formal communication" :
                 "💬 Casual/informal speech"}
              </div>
            </div>
            
            <div className="space-y-4">
              <ProgressBar 
                value={linguistic_analysis.complexity_score} 
                color="indigo" 
                label="Complexity Score"
              />
              <div className="text-xs text-gray-400 mt-2">
                {linguistic_analysis.complexity_score > 70 ? "🔬 High linguistic sophistication" :
                 linguistic_analysis.complexity_score > 40 ? "📚 Moderate complexity" :
                 "📝 Simple language structure"}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Emotional Analysis */}
      {emotional_analysis && (
        <Card className="bg-black/20 backdrop-blur-sm border border-cyan-400/30">
          <CardContent className="p-6">
            <h4 className="text-lg font-semibold text-cyan-300 mb-4">😊 Emotional State</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <MetricCard
                title="Dominant Emotion"
                value={emotional_analysis.dominant_emotion || "Unknown"}
                description="Primary emotional state detected"
                color="cyan"
                comparison={`${((emotional_analysis.confidence || 0) * 100).toFixed(1)}% confidence`}
              />
              
              <MetricCard
                title="Emotional Intensity"
                value={((emotional_analysis.intensity || 0) * 100).toFixed(1)}
                unit="%"
                description="Strength of emotional expression"
                color="pink"
              />
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );

  const renderDeceptionTab = () => (
    <div className="space-y-6">
      {/* Overall Risk Assessment */}
      <Card className="bg-black/20 backdrop-blur-sm border border-red-400/30">
        <CardContent className="p-6">
          <h4 className="text-lg font-semibold text-red-300 mb-4">🚨 Deception Risk Assessment</h4>
          <div className="text-center mb-6">
            <div className="text-6xl font-bold text-white mb-2">
              {result.deception_probability?.toFixed(1) || "N/A"}%
            </div>
            <div className={`text-lg font-semibold ${
              result.deception_probability > 70 ? "text-red-300" :
              result.deception_probability > 40 ? "text-yellow-300" :
              "text-green-300"
            }`}>
              {result.deception_probability > 70 ? "🔴 HIGH RISK" :
               result.deception_probability > 40 ? "🟡 MODERATE RISK" :
               "🟢 LOW RISK"}
            </div>
          </div>
          
          <div className="w-full bg-black/30 rounded-full h-4 mb-4">
            <div
              className={`h-4 rounded-full transition-all duration-1000 ${
                result.deception_probability > 70 ? "bg-gradient-to-r from-red-600 to-red-400" :
                result.deception_probability > 40 ? "bg-gradient-to-r from-yellow-600 to-yellow-400" :
                "bg-gradient-to-r from-green-600 to-green-400"
              }`}
              style={{width: `${result.deception_probability || 0}%`}}
            ></div>
          </div>
        </CardContent>
      </Card>

      {/* Deception Indicators */}
      <Card className="bg-black/20 backdrop-blur-sm border border-orange-400/30">
        <CardContent className="p-6">
          <h4 className="text-lg font-semibold text-orange-300 mb-4">🎯 Key Indicators</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            
            {/* Stress Indicators */}
            <div className="space-y-3">
              <h5 className="text-sm font-semibold text-red-300">⚡ Stress Indicators</h5>
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-400">Hesitation frequency:</span>
                  <span className={`font-semibold ${
                    linguistic_analysis.hesitation_count > 10 ? "text-red-300" :
                    linguistic_analysis.hesitation_count > 5 ? "text-yellow-300" :
                    "text-green-300"
                  }`}>
                    {linguistic_analysis.hesitation_count > 10 ? "HIGH" :
                     linguistic_analysis.hesitation_count > 5 ? "MODERATE" :
                     "LOW"}
                  </span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-400">Speech rate variation:</span>
                  <span className={`font-semibold ${
                    linguistic_analysis.speech_rate_wpm < 120 || linguistic_analysis.speech_rate_wpm > 200 ? "text-yellow-300" : "text-green-300"
                  }`}>
                    {linguistic_analysis.speech_rate_wpm < 120 || linguistic_analysis.speech_rate_wpm > 200 ? "ABNORMAL" : "NORMAL"}
                  </span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-400">Word repetitions:</span>
                  <span className={`font-semibold ${
                    linguistic_analysis.repetition_count > 5 ? "text-red-300" :
                    linguistic_analysis.repetition_count > 2 ? "text-yellow-300" :
                    "text-green-300"
                  }`}>
                    {linguistic_analysis.repetition_count > 5 ? "HIGH" :
                     linguistic_analysis.repetition_count > 2 ? "MODERATE" :
                     "LOW"}
                  </span>
                </div>
              </div>
            </div>

            {/* Confidence Indicators */}
            <div className="space-y-3">
              <h5 className="text-sm font-semibold text-blue-300">🎯 Confidence Patterns</h5>
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-400">Certainty level:</span>
                  <span className={`font-semibold ${
                    linguistic_analysis.confidence_ratio > 0.7 ? "text-green-300" :
                    linguistic_analysis.confidence_ratio > 0.4 ? "text-yellow-300" :
                    "text-red-300"
                  }`}>
                    {linguistic_analysis.confidence_ratio > 0.7 ? "HIGH" :
                     linguistic_analysis.confidence_ratio > 0.4 ? "MODERATE" :
                     "LOW"}
                  </span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-400">Qualification usage:</span>
                  <span className={`font-semibold ${
                    linguistic_analysis.qualifier_count > 8 ? "text-red-300" :
                    linguistic_analysis.qualifier_count > 4 ? "text-yellow-300" :
                    "text-green-300"
                  }`}>
                    {linguistic_analysis.qualifier_count > 8 ? "EXCESSIVE" :
                     linguistic_analysis.qualifier_count > 4 ? "MODERATE" :
                     "MINIMAL"}
                  </span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-400">Language formality:</span>
                  <span className={`font-semibold ${
                    linguistic_analysis.formality_score > 70 ? "text-blue-300" :
                    linguistic_analysis.formality_score > 40 ? "text-yellow-300" :
                    "text-gray-300"
                  }`}>
                    {linguistic_analysis.formality_score > 70 ? "FORMAL" :
                     linguistic_analysis.formality_score > 40 ? "SEMI-FORMAL" :
                     "INFORMAL"}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );

  const renderSessionTab = () => (
    <div className="space-y-6">
      {/* Session Insights */}
      {session_insights ? (
        <Card className="bg-black/20 backdrop-blur-sm border border-green-400/30">
          <CardContent className="p-6">
            <h4 className="text-lg font-semibold text-green-300 mb-4">📈 AI Session Analysis</h4>
            <div className="space-y-4">
              
              {session_insights.consistency_analysis && (
                <div className="bg-white/5 p-4 rounded-lg border-l-4 border-green-400">
                  <span className="font-semibold text-green-300">🎯 Consistency Analysis:</span>
                  <p className="text-gray-200 mt-2 text-sm leading-relaxed">
                    {session_insights.consistency_analysis}
                  </p>
                </div>
              )}

              {session_insights.behavioral_evolution && (
                <div className="bg-white/5 p-4 rounded-lg border-l-4 border-blue-400">
                  <span className="font-semibold text-blue-300">📊 Behavioral Evolution:</span>
                  <p className="text-gray-200 mt-2 text-sm leading-relaxed">
                    {session_insights.behavioral_evolution}
                  </p>
                </div>
              )}

              {session_insights.risk_trajectory && (
                <div className="bg-white/5 p-4 rounded-lg border-l-4 border-yellow-400">
                  <span className="font-semibold text-yellow-300">⚠️ Risk Trajectory:</span>
                  <p className="text-gray-200 mt-2 text-sm leading-relaxed">
                    {session_insights.risk_trajectory}
                  </p>
                </div>
              )}

              {session_insights.conversation_dynamics && (
                <div className="bg-white/5 p-4 rounded-lg border-l-4 border-purple-400">
                  <span className="font-semibold text-purple-300">💬 Conversation Dynamics:</span>
                  <p className="text-gray-200 mt-2 text-sm leading-relaxed">
                    {session_insights.conversation_dynamics}
                  </p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      ) : (
        <Card className="bg-black/20 backdrop-blur-sm border border-blue-400/30">
          <CardContent className="p-6">
            <h4 className="text-lg font-semibold text-blue-300 mb-4">📈 Session Analysis</h4>
            <div className="bg-blue-500/20 backdrop-blur-sm border border-blue-400/30 rounded-lg p-4">
              <p className="text-blue-200">
                📊 Session insights will be available after multiple analyses in the same session
              </p>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Current Analysis Summary */}
      <Card className="bg-black/20 backdrop-blur-sm border border-cyan-400/30">
        <CardContent className="p-6">
          <h4 className="text-lg font-semibold text-cyan-300 mb-4">📋 Current Analysis Summary</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <MetricCard
              title="Analysis Timestamp"
              value={new Date().toLocaleTimeString()}
              description="When this analysis was performed"
              color="cyan"
            />
            
            <MetricCard
              title="Audio Duration"
              value={audio_quality?.duration?.toFixed(1)}
              unit=" sec"
              description="Length of analyzed audio"
              color="blue"
            />
            
            <MetricCard
              title="Word Density"
              value={linguistic_analysis.speech_rate_wpm ? 
                (linguistic_analysis.word_count / (audio_quality?.duration / 60)).toFixed(1) : 
                "N/A"}
              unit=" words/min"
              description="Speaking efficiency"
              color="green"
            />
          </div>
        </CardContent>
      </Card>
    </div>
  );

  const renderTabContent = () => {
    switch (activeTab) {
      case 'overview': return renderOverviewTab();
      case 'speech': return renderSpeechTab();
      case 'psychology': return renderPsychologyTab();
      case 'deception': return renderDeceptionTab();
      case 'session': return renderSessionTab();
      default: return renderOverviewTab();
    }
  };
  return (
    <div className="space-y-6">
      {/* Tab Navigation */}
      <Card className="section-container analysis-breakdown glow-purple">
        <CardContent className="p-6">
          <h3 className="text-xl font-semibold text-white mb-4">📊 Comprehensive Analysis Dashboard</h3>
          <div className="flex flex-wrap gap-2">
            {tabs.map((tab) => (
              <TabButton
                key={tab.id}
                isActive={activeTab === tab.id}
                onClick={() => setActiveTab(tab.id)}
                icon={tab.icon}
              >
                {tab.label}
              </TabButton>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Tab Content */}
      <div className="min-h-[600px]">
        {renderTabContent()}
      </div>
    </div>
  );
};

export default ComprehensiveAnalysisSection;
