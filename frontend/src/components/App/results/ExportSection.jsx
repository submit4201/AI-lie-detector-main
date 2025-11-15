import React, { useState } from 'react';
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

const ExportSection = ({ result, sessionHistory, sessionId }) => {
  const [exportFormat, setExportFormat] = useState('json');
  const [selectedSections, setSelectedSections] = useState({
    transcript: true,
    credibility: true,
    emotions: true,
    linguistic: true,
    riskAssessment: true,
    manipulation: true,
    argument: true,
    speakerAttitude: true,
    enhancedUnderstanding: true,
    audioAnalysis: true,
    recommendations: true,
    sessionInsights: true,
    sessionHistory: false,
  });
  if (!result) {
    return (
      <Card className="section-container export-section">
        <CardContent className="p-6">
          <h3 className="text-xl font-semibold text-gray-400 mb-4 flex items-center">
            <span className="mr-2">📥</span>
            Export Results
          </h3>
          <p className="text-gray-400 text-center py-4">No analysis results to export</p>
        </CardContent>
      </Card>
    );
  }

  const handleSectionToggle = (section) => {
    setSelectedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  const getExportData = () => {
    const exportData = {
      metadata: {
        exportDate: new Date().toISOString(),
        sessionId: sessionId,
        exportFormat: exportFormat,
        selectedSections: Object.keys(selectedSections).filter(key => selectedSections[key])
      }
    };

    // Add selected sections
    if (selectedSections.transcript) {
      exportData.transcript = result.transcript;
      exportData.speaker_transcripts = result.speaker_transcripts;
    }

    if (selectedSections.credibility) {
      exportData.credibility_analysis = {
        score: result.credibility_score,
        confidence_level: result.confidence_level,
        gemini_summary: result.gemini_summary
      };
    }

    if (selectedSections.emotions) {
      exportData.emotion_analysis = result.emotion_analysis;
    }

    if (selectedSections.linguistic) {
      exportData.linguistic_analysis = result.linguistic_analysis;
    }

    if (selectedSections.riskAssessment) {
      exportData.risk_assessment = result.risk_assessment;
      exportData.red_flags_per_speaker = result.red_flags_per_speaker;
    }

    if (selectedSections.manipulation) {
      exportData.manipulation_assessment = result.manipulation_assessment;
    }

    if (selectedSections.argument) {
      exportData.argument_analysis = result.argument_analysis;
    }

    if (selectedSections.speakerAttitude) {
      exportData.speaker_attitude = result.speaker_attitude;
    }

    if (selectedSections.enhancedUnderstanding) {
      exportData.enhanced_understanding = result.enhanced_understanding;
    }

    if (selectedSections.audioAnalysis) {
      exportData.audio_analysis = result.audio_analysis;
      exportData.audio_quality = result.audio_quality;
    }

    if (selectedSections.recommendations) {
      exportData.recommendations = result.recommendations;
    }

    if (selectedSections.sessionInsights) {
      exportData.session_insights = result.session_insights;
    }

    if (selectedSections.sessionHistory && sessionHistory) {
      exportData.session_history = sessionHistory;
    }

    return exportData;
  };

  const exportAsJSON = () => {
    const data = getExportData();
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(data, null, 2));
    const downloadAnchorNode = document.createElement('a');
    downloadAnchorNode.setAttribute("href", dataStr);
    downloadAnchorNode.setAttribute("download", `analysis_results_${sessionId || 'current'}_${Date.now()}.json`);
    document.body.appendChild(downloadAnchorNode);
    downloadAnchorNode.click();
    downloadAnchorNode.remove();
  };

  const exportAsCSV = () => {
    const data = getExportData();
    
    // Create CSV header and rows for quantitative data
    const csvData = [];
    csvData.push(['Metric', 'Value', 'Category']);
    
    // Add basic metrics
    if (data.credibility_analysis) {
      csvData.push(['Credibility Score', data.credibility_analysis.score || 'N/A', 'Credibility']);
      csvData.push(['Confidence Level', data.credibility_analysis.confidence_level || 'N/A', 'Credibility']);
    }

    // Add linguistic metrics
    if (data.linguistic_analysis) {
      const la = data.linguistic_analysis;
      csvData.push(['Speech Rate (WPM)', la.speech_rate_wpm || 'N/A', 'Linguistic']);
      csvData.push(['Formality Score', la.formality_score || 'N/A', 'Linguistic']);
      csvData.push(['Hesitation Count', la.hesitation_count || 'N/A', 'Linguistic']);
      csvData.push(['Repetition Count', la.repetition_count || 'N/A', 'Linguistic']);
      csvData.push(['Vocabulary Complexity', la.complexity_score || 'N/A', 'Linguistic']);
    }

    // Add emotion scores
    if (data.emotion_analysis && Array.isArray(data.emotion_analysis)) {
      data.emotion_analysis.forEach(emotion => {
        csvData.push([`Emotion: ${emotion.label}`, emotion.score, 'Emotion']);
      });
    }

    // Add assessment scores
    if (data.manipulation_assessment) {
      csvData.push(['Manipulation Score', data.manipulation_assessment.manipulation_score || 'N/A', 'Assessment']);
    }

    if (data.argument_analysis) {
      csvData.push(['Argument Coherence', data.argument_analysis.overall_argument_coherence_score || 'N/A', 'Assessment']);
    }

    if (data.speaker_attitude) {
      csvData.push(['Respect Level', data.speaker_attitude.respect_level_score || 'N/A', 'Assessment']);
      csvData.push(['Sarcasm Detected', data.speaker_attitude.sarcasm_detected ? 'Yes' : 'No', 'Assessment']);
    }

    // Convert to CSV string
    const csvString = csvData.map(row => row.map(cell => `"${cell}"`).join(',')).join('\n');
    
    const dataStr = "data:text/csv;charset=utf-8," + encodeURIComponent(csvString);
    const downloadAnchorNode = document.createElement('a');
    downloadAnchorNode.setAttribute("href", dataStr);
    downloadAnchorNode.setAttribute("download", `analysis_metrics_${sessionId || 'current'}_${Date.now()}.csv`);
    document.body.appendChild(downloadAnchorNode);
    downloadAnchorNode.click();
    downloadAnchorNode.remove();
  };

  const exportAsText = () => {
    const data = getExportData();
    let textReport = `AI LIE DETECTOR ANALYSIS REPORT\n`;
    textReport += `Generated: ${new Date().toLocaleString()}\n`;
    textReport += `Session ID: ${sessionId || 'N/A'}\n`;
    textReport += `\n${'='.repeat(50)}\n\n`;

    if (data.transcript) {
      textReport += `TRANSCRIPT:\n${data.transcript}\n\n`;
    }

    if (data.credibility_analysis) {
      textReport += `CREDIBILITY ANALYSIS:\n`;
      textReport += `Score: ${data.credibility_analysis.score || 'N/A'}%\n`;
      textReport += `Confidence: ${data.credibility_analysis.confidence_level || 'N/A'}\n\n`;
    }

    if (data.risk_assessment) {
      textReport += `RISK ASSESSMENT:\n`;
      textReport += `Overall Risk: ${data.risk_assessment.overall_risk || 'N/A'}\n`;
      if (data.risk_assessment.risk_factors) {
        textReport += `Risk Factors:\n`;
        data.risk_assessment.risk_factors.forEach(factor => {
          textReport += `  • ${factor}\n`;
        });
      }
      textReport += `\n`;
    }

    if (data.recommendations && Array.isArray(data.recommendations)) {
      textReport += `RECOMMENDATIONS:\n`;
      data.recommendations.forEach(rec => {
        textReport += `  • ${rec}\n`;
      });
      textReport += `\n`;
    }

    const dataStr = "data:text/plain;charset=utf-8," + encodeURIComponent(textReport);
    const downloadAnchorNode = document.createElement('a');
    downloadAnchorNode.setAttribute("href", dataStr);
    downloadAnchorNode.setAttribute("download", `analysis_report_${sessionId || 'current'}_${Date.now()}.txt`);
    document.body.appendChild(downloadAnchorNode);
    downloadAnchorNode.click();
    downloadAnchorNode.remove();
  };

  const handleExport = () => {
    switch (exportFormat) {
      case 'json':
        exportAsJSON();
        break;
      case 'csv':
        exportAsCSV();
        break;
      case 'txt':
        exportAsText();
        break;
      default:
        exportAsJSON();
    }
  };

  const getSectionLabel = (key) => {
    const labels = {
      transcript: 'Transcript',
      credibility: 'Credibility Analysis',
      emotions: 'Emotion Analysis',
      linguistic: 'Linguistic Metrics',
      riskAssessment: 'Risk Assessment',
      manipulation: 'Manipulation Assessment',
      argument: 'Argument Analysis',
      speakerAttitude: 'Speaker Attitude',
      enhancedUnderstanding: 'Enhanced Understanding',
      audioAnalysis: 'Audio Analysis',
      recommendations: 'Recommendations',
      sessionInsights: 'Session Insights',
      sessionHistory: 'Session History'
    };
    return labels[key] || key;
  };

  const selectedCount = Object.values(selectedSections).filter(Boolean).length;
  return (
    <Card className="section-container export-section">
      <CardContent className="p-6">
        <h3 className="text-xl font-semibold text-green-300 mb-4 flex items-center">
          <span className="mr-2">📥</span>
          Export Analysis Results
        </h3>

        {/* Format Selection */}
        <div className="mb-6">
          <h4 className="text-lg font-medium text-gray-200 mb-3">Export Format</h4>
          <div className="flex flex-wrap gap-2">
            {[
              { value: 'json', label: 'JSON (Complete Data)', icon: '📄' },
              { value: 'csv', label: 'CSV (Metrics Only)', icon: '📊' },
              { value: 'txt', label: 'Text Report', icon: '📝' }
            ].map(format => (
              <button
                key={format.value}
                onClick={() => setExportFormat(format.value)}
                className={`flex items-center space-x-2 px-4 py-2 rounded-lg border transition-all ${
                  exportFormat === format.value
                    ? 'bg-green-500/30 border-green-400/50 text-green-200'
                    : 'bg-black/20 border-gray-600/30 text-gray-300 hover:border-green-400/30'
                }`}
              >
                <span>{format.icon}</span>
                <span>{format.label}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Section Selection */}
        <div className="mb-6">
          <div className="flex justify-between items-center mb-3">
            <h4 className="text-lg font-medium text-gray-200">Select Sections to Export</h4>
            <Badge variant="outline" className="text-green-300">
              {selectedCount} selected
            </Badge>
          </div>
          
          <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
            {Object.entries(selectedSections).map(([key, selected]) => (
              <label
                key={key}
                className={`flex items-center space-x-2 p-2 rounded cursor-pointer transition-all ${
                  selected
                    ? 'bg-green-500/20 border border-green-400/30'
                    : 'bg-black/20 border border-gray-600/30 hover:border-green-400/20'
                }`}
              >
                <input
                  type="checkbox"
                  checked={selected}
                  onChange={() => handleSectionToggle(key)}
                  className="text-green-500"
                />
                <span className={`text-sm ${selected ? 'text-green-200' : 'text-gray-300'}`}>
                  {getSectionLabel(key)}
                </span>
              </label>
            ))}
          </div>

          <div className="flex justify-between mt-3">
            <button
              onClick={() => setSelectedSections(Object.keys(selectedSections).reduce((acc, key) => ({...acc, [key]: true}), {}))}
              className="text-sm text-green-400 hover:text-green-300"
            >
              Select All
            </button>
            <button
              onClick={() => setSelectedSections(Object.keys(selectedSections).reduce((acc, key) => ({...acc, [key]: false}), {}))}
              className="text-sm text-gray-400 hover:text-gray-300"
            >
              Deselect All
            </button>
          </div>
        </div>

        {/* Export Button */}
        <div className="flex justify-center">
          <button
            onClick={handleExport}
            disabled={selectedCount === 0}
            className={`flex items-center space-x-2 px-6 py-3 rounded-lg font-medium transition-all ${
              selectedCount > 0
                ? 'bg-green-500/30 border border-green-400/50 text-green-200 hover:bg-green-500/40'
                : 'bg-gray-500/20 border border-gray-600/30 text-gray-500 cursor-not-allowed'
            }`}
          >
            <span>📥</span>
            <span>Export {exportFormat.toUpperCase()}</span>
          </button>
        </div>

        {/* Export Info */}
        <div className="mt-4 text-xs text-gray-400 text-center">
          <p>Exports will include selected sections and metadata</p>
          <p>File name format: analysis_results_[session]_[timestamp].[format]</p>
        </div>
      </CardContent>
    </Card>
  );
};

export default ExportSection;
