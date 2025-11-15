import React from 'react';
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

const MetricBar = ({ label, value, max, unit = '', color = 'blue' }) => {
  const percentage = max > 0 ? Math.min((value / max) * 100, 100) : 0;
  
  const colorClasses = {
    blue: 'bg-blue-500',
    green: 'bg-green-500', 
    yellow: 'bg-yellow-500',
    red: 'bg-red-500',
    purple: 'bg-purple-500'
  };

  return (
    <div className="mb-3">
      <div className="flex justify-between items-center mb-1">
        <span className="text-gray-300 text-sm font-medium">{label}</span>
        <span className="text-gray-200 text-sm font-bold">
          {typeof value === 'number' ? value.toFixed(1) : value}{unit}
        </span>
      </div>
      <div className="w-full bg-gray-700 rounded-full h-2">
        <div
          className={`${colorClasses[color]} h-2 rounded-full transition-all duration-300`}
          style={{ width: `${percentage}%` }}
        ></div>
      </div>
    </div>
  );
};

const MetricCard = ({ title, metrics, icon, color = 'blue' }) => {
  const borderColors = {
    blue: 'border-blue-400/30',
    green: 'border-green-400/30',
    yellow: 'border-yellow-400/30', 
    red: 'border-red-400/30',
    purple: 'border-purple-400/30'
  };

  const textColors = {
    blue: 'text-blue-300',
    green: 'text-green-300',
    yellow: 'text-yellow-300',
    red: 'text-red-300', 
    purple: 'text-purple-300'
  };

  return (
    <div className={`bg-black/20 backdrop-blur-sm border ${borderColors[color]} rounded-lg p-4`}>
      <div className="flex items-center mb-3">
        <span className="text-lg mr-2">{icon}</span>
        <h4 className={`text-md font-semibold ${textColors[color]}`}>{title}</h4>
      </div>
      <div className="space-y-2">
        {metrics.map((metric, index) => (
          <MetricBar key={index} {...metric} color={color} />
        ))}
      </div>
    </div>
  );
};

const QuantitativeMetricsCard = ({ analysis }) => {
  if (!analysis) {
    return (
      <Card className="bg-transparent shadow-none border-none rounded-none">
        <CardContent className="p-0">
          <div className="bg-black/30 backdrop-blur-sm border border-white/20 rounded-lg p-4">
            <p className="text-gray-400">Quantitative metrics not available.</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  // Extract quantitative metrics from linguistic analysis
  const speechMetrics = [
    { label: 'Words per Minute', value: analysis.speech_rate_wpm || 0, max: 300, unit: ' WPM' },
    { label: 'Average Word Length', value: analysis.avg_word_length || 0, max: 10, unit: ' chars' },
    { label: 'Words per Sentence', value: analysis.avg_words_per_sentence || 0, max: 30, unit: ' words' }
  ];

  const qualityMetrics = [
    { label: 'Formality Score', value: analysis.formality_score || 0, max: 100, unit: '/100' },
    { label: 'Complexity Score', value: analysis.complexity_score || 0, max: 100, unit: '/100' },
    { label: 'Confidence Ratio', value: (analysis.confidence_ratio || 0) * 100, max: 100, unit: '/100' }
  ];

  const hesitationMetrics = [
    { label: 'Hesitation Count', value: analysis.hesitation_count || 0, max: Math.max(20, (analysis.hesitation_count || 0) * 1.5), unit: '' },
    { label: 'Hesitation Rate', value: analysis.hesitation_rate || 0, max: 10, unit: '/min' },
    { label: 'Filler Word Count', value: analysis.filler_count || 0, max: Math.max(15, (analysis.filler_count || 0) * 1.5), unit: '' }
  ];

  const linguisticMetrics = [
    { label: 'Qualifier Count', value: analysis.qualifier_count || 0, max: Math.max(10, (analysis.qualifier_count || 0) * 1.5), unit: '' },
    { label: 'Certainty Indicators', value: analysis.certainty_count || 0, max: Math.max(10, (analysis.certainty_count || 0) * 1.5), unit: '' },
    { label: 'Repetitions', value: analysis.repetition_count || 0, max: Math.max(5, (analysis.repetition_count || 0) * 2), unit: '' }
  ];

  const basicStats = [
    { label: 'Total Words', value: analysis.word_count || 0, max: Math.max(500, (analysis.word_count || 0) * 1.2), unit: '' },
    { label: 'Total Sentences', value: analysis.sentence_count || 0, max: Math.max(50, (analysis.sentence_count || 0) * 1.2), unit: '' }
  ];

  return (
    <Card className="bg-transparent shadow-none border-none rounded-none">
      <CardContent className="p-0 space-y-4">
        
        {/* Header */}
        <div className="bg-black/40 backdrop-blur-sm border border-white/20 rounded-lg p-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <span className="text-xl mr-2">📊</span>
              <h3 className="text-lg font-semibold text-white">Quantitative Analysis Metrics</h3>
            </div>
            <Badge variant="outline" className="bg-blue-500/20 text-blue-300 border-blue-400/30">
              Data-Driven
            </Badge>
          </div>
        </div>

        {/* Basic Statistics */}
        <MetricCard
          title="Basic Statistics"
          metrics={basicStats}
          icon="📏"
          color="blue"
        />

        {/* Speech Patterns */}
        <MetricCard
          title="Speech Patterns"
          metrics={speechMetrics}
          icon="🎤"
          color="green"
        />

        {/* Quality Indicators */}
        <MetricCard
          title="Language Quality"
          metrics={qualityMetrics}
          icon="⭐"
          color="purple"
        />

        {/* Hesitation Analysis */}
        <MetricCard
          title="Hesitation Analysis"
          metrics={hesitationMetrics}
          icon="🤔"
          color="yellow"
        />

        {/* Linguistic Patterns */}
        <MetricCard
          title="Linguistic Patterns"
          metrics={linguisticMetrics}
          icon="🔍"
          color="red"
        />

        {/* Footer note */}
        <div className="bg-black/20 backdrop-blur-sm border border-white/10 rounded-lg p-3">
          <p className="text-gray-400 text-xs">
            📈 These metrics provide objective, quantitative insights into speech patterns and linguistic behavior.
          </p>
        </div>
      </CardContent>
    </Card>
  );
};

export default QuantitativeMetricsCard;
