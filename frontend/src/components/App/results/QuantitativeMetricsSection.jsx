import React from 'react';
import { Card, CardContent } from "@/components/ui/card";
import { ResponsiveContainer, RadialBarChart, RadialBar, PolarAngleAxis, Text } from 'recharts';

const MetricCard = ({ title, value, unit, description, color = "blue", comparison }) => (
  <div className={`bg-black/20 backdrop-blur-sm p-3 rounded-lg border border-${color}-400/30 hover:border-${color}-400/50 transition-all duration-300`}>
    <div className="flex justify-between items-center mb-1">
      <span className={`text-${color}-300 font-medium text-sm`}>{title}</span>
      <span className={`text-${color}-200 font-bold`}>
        {value !== null && value !== undefined ? `${value}${unit || ''}` : 'N/A'}
      </span>
    </div>
    {comparison && (
      <div className="text-xs text-gray-400 mb-1">{comparison}</div>
    )}
    <div className="text-xs text-gray-400">{description}</div>
  </div>
);

const SpeechPatternsCard = ({ linguisticAnalysis, audioQuality }) => {
  if (!linguisticAnalysis) return null;

  return (
    <Card className="bg-white/10 backdrop-blur-md border-white/20 shadow-xl">
      <CardContent className="p-6">
        <h3 className="text-xl font-semibold text-white mb-4">🎵 Speech Pattern Analysis</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          
          {/* Core Speech Metrics */}
          <MetricCard
            title="Speech Rate"
            value={linguisticAnalysis.speech_rate_wpm}
            unit=" WPM"
            description="Words per minute - normal range is 140-180 WPM"
            color="blue"
            comparison={linguisticAnalysis.speech_rate_wpm && 
              (linguisticAnalysis.speech_rate_wpm < 120 ? "Slow pace may indicate hesitation" :
               linguisticAnalysis.speech_rate_wpm > 200 ? "Fast pace may indicate nervousness" :
               "Normal speaking pace")}
          />

          <MetricCard
            title="Word Count"
            value={linguisticAnalysis.word_count}
            description="Total words spoken in the analysis"
            color="green"
          />

          <MetricCard
            title="Sentence Count"
            value={linguisticAnalysis.sentence_count}
            description="Number of complete sentences identified"
            color="purple"
          />

          <MetricCard
            title="Avg Words/Sentence"
            value={linguisticAnalysis.avg_words_per_sentence?.toFixed(1)}
            description="Average sentence length - longer may indicate complexity"
            color="indigo"
            comparison={linguisticAnalysis.avg_words_per_sentence && 
              (linguisticAnalysis.avg_words_per_sentence > 20 ? "Complex sentence structure" :
               linguisticAnalysis.avg_words_per_sentence < 8 ? "Simple sentence structure" :
               "Moderate sentence structure")}
          />

          <MetricCard
            title="Avg Word Length"
            value={linguisticAnalysis.avg_word_length?.toFixed(1)}
            unit=" chars"
            description="Average word length indicates vocabulary complexity"
            color="cyan"
            comparison={linguisticAnalysis.avg_word_length && 
              (linguisticAnalysis.avg_word_length > 5.5 ? "Complex vocabulary" :
               linguisticAnalysis.avg_word_length < 4.5 ? "Simple vocabulary" :
               "Moderate vocabulary")}
          />

          <MetricCard
            title="Audio Duration"
            value={audioQuality?.duration?.toFixed(1)}
            unit=" sec"
            description="Total audio length analyzed"
            color="gray"
          />
        </div>
      </CardContent>
    </Card>
  );
};

const HesitationAnalysisCard = ({ linguisticAnalysis }) => {
  if (!linguisticAnalysis) return null;

  return (
    <Card className="bg-white/10 backdrop-blur-md border-white/20 shadow-xl">
      <CardContent className="p-6">
        <h3 className="text-xl font-semibold text-white mb-4">⚡ Hesitation & Uncertainty Analysis</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          
          <MetricCard
            title="Hesitation Count"
            value={linguisticAnalysis.hesitation_count}
            description="Um, uh, er, ah, like, you know"
            color="red"
            comparison={linguisticAnalysis.hesitation_count > 10 ? "High hesitation" :
                       linguisticAnalysis.hesitation_count > 5 ? "Moderate hesitation" :
                       "Low hesitation"}
          />

          <MetricCard
            title="Hesitation Rate"
            value={linguisticAnalysis.hesitation_rate?.toFixed(1)}
            unit="/min"
            description="Hesitation markers per minute"
            color="orange"
            comparison={linguisticAnalysis.hesitation_rate && 
              (linguisticAnalysis.hesitation_rate > 8 ? "Concerning frequency" :
               linguisticAnalysis.hesitation_rate > 4 ? "Moderate frequency" :
               "Normal frequency")}
          />

          <MetricCard
            title="Filler Words"
            value={linguisticAnalysis.filler_count}
            description="Um, uh, er, ah only"
            color="yellow"
            comparison={linguisticAnalysis.filler_count > 8 ? "Excessive fillers" :
                       linguisticAnalysis.filler_count > 4 ? "Some fillers" :
                       "Few fillers"}
          />

          <MetricCard
            title="Repetitions"
            value={linguisticAnalysis.repetition_count}
            description="Word repetitions detected"
            color="pink"
            comparison={linguisticAnalysis.repetition_count > 5 ? "High repetition" :
                       linguisticAnalysis.repetition_count > 2 ? "Some repetition" :
                       "Low repetition"}
          />
        </div>
      </CardContent>
    </Card>
  );
};

const ConfidenceAnalysisCard = ({ linguisticAnalysis }) => {
  if (!linguisticAnalysis) return null;

  const confidencePercentage = (linguisticAnalysis.confidence_ratio * 100).toFixed(1);

  return (
    <Card className="bg-white/10 backdrop-blur-md border-white/20 shadow-xl">
      <CardContent className="p-6">
        <h3 className="text-xl font-semibold text-white mb-4">🎯 Confidence & Certainty Analysis</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          
          <MetricCard
            title="Certainty Indicators"
            value={linguisticAnalysis.certainty_count}
            description="Definitely, absolutely, sure, certain"
            color="green"
            comparison={linguisticAnalysis.certainty_count > 8 ? "Very confident" :
                       linguisticAnalysis.certainty_count > 4 ? "Moderately confident" :
                       "Low confidence indicators"}
          />

          <MetricCard
            title="Uncertainty Qualifiers"
            value={linguisticAnalysis.qualifier_count}
            description="Maybe, perhaps, might, probably"
            color="yellow"
            comparison={linguisticAnalysis.qualifier_count > 8 ? "High uncertainty" :
                       linguisticAnalysis.qualifier_count > 4 ? "Some uncertainty" :
                       "Low uncertainty"}
          />

          <MetricCard
            title="Confidence Ratio"
            value={confidencePercentage}
            unit="%"
            description="Certainty vs uncertainty ratio"
            color="blue"
            comparison={linguisticAnalysis.confidence_ratio > 0.7 ? "High confidence speech" :
                       linguisticAnalysis.confidence_ratio > 0.4 ? "Balanced confidence" :
                       "Low confidence speech"}
          />

          <div className="bg-black/20 backdrop-blur-sm p-3 rounded-lg border border-blue-400/30">
            <div className="text-blue-300 font-medium text-sm mb-2">Confidence Breakdown</div>
            <div className="space-y-2">
              <div className="flex justify-between text-xs">
                <span className="text-gray-400">Certain statements:</span>
                <span className="text-green-300">{linguisticAnalysis.certainty_count}</span>
              </div>
              <div className="flex justify-between text-xs">
                <span className="text-gray-400">Uncertain statements:</span>
                <span className="text-yellow-300">{linguisticAnalysis.qualifier_count}</span>
              </div>
              <div className="w-full bg-white/20 rounded-full h-2 mt-2">
                <div
                  className="h-2 rounded-full bg-gradient-to-r from-green-500 to-yellow-500"
                  style={{width: `${confidencePercentage}%`}}
                ></div>
              </div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

const ScoreChart = ({ score, name, color, textColor, unit = "/100" }) => {
  const chartData = [{ name: name, value: score || 0, fill: color }];
  const percentage = score || 0;

  return (
    <div style={{ width: '100%', height: 150 }}> {/* Ensure height is sufficient */}
      <ResponsiveContainer>
        <RadialBarChart
          cx="50%"
          cy="70%" // Adjust to make space for title if needed, or keep centered
          innerRadius="60%"
          outerRadius="100%"
          barSize={12}
          data={chartData}
          startAngle={180}
          endAngle={0}
        >
          <PolarAngleAxis
            type="number"
            domain={[0, 100]}
            angleAxisId={0}
            tick={false}
          />
          <RadialBar
            background={{ fill: '#333' }} // Darker background for the track
            dataKey="value"
            cornerRadius={6}
            angleAxisId={0}
          />
          {/* Custom label to display the score in the center */}
          <Text
            x="50%"
            y="70%" // Adjust y to be in the center of the semi-circle
            textAnchor="middle"
            dominantBaseline="middle"
            className="fill-current font-bold text-xl"
            style={{ fill: textColor }} // Use textColor prop for dynamic color
          >
            {`${percentage.toFixed(1)}${unit}`}
          </Text>
        </RadialBarChart>
      </ResponsiveContainer>
    </div>
  );
};


const ComplexityAnalysisCard = ({ linguisticAnalysis }) => {
  if (!linguisticAnalysis) return null;

  return (
    <Card className="bg-white/10 backdrop-blur-md border-white/20 shadow-xl">
      <CardContent className="p-6">
        <h3 className="text-xl font-semibold text-white mb-4">🧠 Language Complexity Analysis</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          
          {/* Formality Score */}
          <div className="bg-black/20 backdrop-blur-sm p-4 rounded-lg border border-purple-400/30 flex flex-col">
            <span className="text-purple-300 font-medium text-center mb-2">Formality Score</span>
            <ScoreChart
              score={linguisticAnalysis.formality_score}
              name="Formality"
              color="#a855f7" // Purple-500
              textColor="#c084fc" // Purple-400
            />
            <div className="text-xs text-gray-400 text-center mt-2">
              {linguisticAnalysis.formality_score > 70 ? "Formal language usage" :
               linguisticAnalysis.formality_score > 40 ? "Moderate formality" :
               "Informal language usage"}
            </div>
            <div className="text-xs text-gray-400 mt-1 text-center">
              Based on formal terms, politeness markers, and professional language
            </div>
          </div>

          {/* Complexity Score */}
          <div className="bg-black/20 backdrop-blur-sm p-4 rounded-lg border border-indigo-400/30 flex flex-col">
            <span className="text-indigo-300 font-medium text-center mb-2">Complexity Score</span>
            <ScoreChart
              score={linguisticAnalysis.complexity_score}
              name="Complexity"
              color="#6366f1" // Indigo-500
              textColor="#818cf8" // Indigo-400
            />
            <div className="text-xs text-gray-400 text-center mt-2">
              {linguisticAnalysis.complexity_score > 70 ? "High linguistic complexity" :
               linguisticAnalysis.complexity_score > 40 ? "Moderate complexity" :
               "Simple language structure"}
            </div>
            <div className="text-xs text-gray-400 mt-1 text-center">
              Based on vocabulary sophistication, sentence structure, and word variety
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

const QuantitativeMetricsSection = ({ result }) => {
  if (!result || !result.linguistic_analysis) {
    return (
      <Card className="bg-white/10 backdrop-blur-md border-white/20 shadow-xl">
        <CardContent className="p-6">
          <h3 className="text-xl font-semibold text-white mb-4">📊 Quantitative Analysis</h3>
          <div className="bg-yellow-500/20 backdrop-blur-sm border border-yellow-400/30 rounded-lg p-4">
            <p className="text-yellow-200">📊 Quantitative metrics not available - structured analysis required</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Speech Patterns */}
      <SpeechPatternsCard 
        linguisticAnalysis={result.linguistic_analysis} 
        audioQuality={result.audio_quality}
      />
      
      {/* Hesitation Analysis */}
      <HesitationAnalysisCard linguisticAnalysis={result.linguistic_analysis} />
      
      {/* Confidence Analysis */}
      <ConfidenceAnalysisCard linguisticAnalysis={result.linguistic_analysis} />
      
      {/* Complexity Analysis */}
      <ComplexityAnalysisCard linguisticAnalysis={result.linguistic_analysis} />
    </div>
  );
};

export default QuantitativeMetricsSection;
