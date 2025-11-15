import React, { useState } from 'react';
import { Card, CardContent } from "@/components/ui/card";

const DataDiagnosticPanel = ({ result, sessionHistory, sessionId }) => {
  const [showDiagnostics, setShowDiagnostics] = useState(false);

  if (!showDiagnostics) {
    return (
      <Card className="section-container mb-4">
        <CardContent className="p-4">
          <button
            onClick={() => setShowDiagnostics(true)}
            className="bg-blue-500/30 hover:bg-blue-500/50 text-blue-200 px-4 py-2 rounded-lg text-sm"
          >
            🔍 Show Data Diagnostics
          </button>
        </CardContent>
      </Card>
    );
  }

  const analyzeData = (data, path = '') => {
    const issues = [];
    const summary = {
      nullValues: 0,
      undefinedValues: 0,
      naValues: 0,
      emptyStrings: 0,
      emptyArrays: 0,
      emptyObjects: 0
    };

    const traverse = (obj, currentPath) => {
      if (obj === null) {
        issues.push(`${currentPath}: null`);
        summary.nullValues++;
      } else if (obj === undefined) {
        issues.push(`${currentPath}: undefined`);
        summary.undefinedValues++;
      } else if (obj === 'N/A' || obj === 'n/a') {
        issues.push(`${currentPath}: N/A value`);
        summary.naValues++;
      } else if (obj === '') {
        issues.push(`${currentPath}: empty string`);
        summary.emptyStrings++;
      } else if (Array.isArray(obj)) {
        if (obj.length === 0) {
          issues.push(`${currentPath}: empty array`);
          summary.emptyArrays++;
        } else {
          obj.forEach((item, index) => {
            traverse(item, `${currentPath}[${index}]`);
          });
        }
      } else if (typeof obj === 'object') {
        const keys = Object.keys(obj);
        if (keys.length === 0) {
          issues.push(`${currentPath}: empty object`);
          summary.emptyObjects++;
        } else {
          keys.forEach(key => {
            traverse(obj[key], currentPath ? `${currentPath}.${key}` : key);
          });
        }
      }
    };

    if (data) {
      traverse(data, path);
    }
    
    return { issues, summary };
  };

  const resultAnalysis = analyzeData(result, 'result');
  const sessionAnalysis = analyzeData(sessionHistory, 'sessionHistory');

  const getMissingRequiredFields = () => {
    const requiredFields = [
      'credibility_score',
      'transcript',
      'emotion_analysis',
      'linguistic_analysis',
      'audio_analysis',
      'manipulation_assessment',
      'argument_analysis',
      'speaker_attitude',
      'enhanced_understanding',
      'risk_assessment'
    ];

    const missing = [];
    requiredFields.forEach(field => {
      if (!result || result[field] === undefined || result[field] === null) {
        missing.push(field);
      }
    });

    return missing;
  };

  const missingFields = getMissingRequiredFields();

  return (
    <Card className="section-container mb-4">
      <CardContent className="p-6">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold text-blue-300">🔍 Data Diagnostics</h3>
          <button
            onClick={() => setShowDiagnostics(false)}
            className="text-gray-400 hover:text-white text-sm"
          >
            Hide
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Analysis Result Data */}
          <div className="bg-black/20 p-4 rounded-lg">
            <h4 className="font-semibold text-white mb-2">Analysis Result Data</h4>
            <div className="text-sm space-y-1">
              <div className="text-gray-300">
                Status: {result ? '✅ Present' : '❌ Missing'}
              </div>
              {result && (
                <>
                  <div className="text-gray-300">
                    Fields: {Object.keys(result).length}
                  </div>
                  <div className="text-gray-300">
                    Issues: {resultAnalysis.issues.length}
                  </div>
                </>
              )}
            </div>
            
            {missingFields.length > 0 && (
              <div className="mt-3">
                <div className="text-red-300 font-medium">Missing Required Fields:</div>
                <div className="text-red-200 text-xs">
                  {missingFields.join(', ')}
                </div>
              </div>
            )}
          </div>

          {/* Session Data */}
          <div className="bg-black/20 p-4 rounded-lg">
            <h4 className="font-semibold text-white mb-2">Session Data</h4>
            <div className="text-sm space-y-1">
              <div className="text-gray-300">
                Session ID: {sessionId || 'N/A'}
              </div>
              <div className="text-gray-300">
                History Items: {sessionHistory?.length || 0}
              </div>
              <div className="text-gray-300">
                Issues: {sessionAnalysis.issues.length}
              </div>
            </div>
          </div>
        </div>

        {/* Issues Summary */}
        {(resultAnalysis.issues.length > 0 || sessionAnalysis.issues.length > 0) && (
          <div className="mt-4">
            <h4 className="font-semibold text-yellow-300 mb-2">⚠️ Data Issues Found</h4>
            <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-lg p-3 max-h-60 overflow-y-auto">
              <div className="text-sm text-yellow-200">
                {[...resultAnalysis.issues, ...sessionAnalysis.issues].map((issue, index) => (
                  <div key={index} className="mb-1">{issue}</div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Raw Data Preview */}
        <div className="mt-4">
          <details className="bg-black/20 rounded-lg">
            <summary className="p-3 cursor-pointer text-gray-300 hover:text-white">
              📋 View Raw Data Structure
            </summary>
            <div className="p-3 bg-black/30 max-h-96 overflow-auto">
              <pre className="text-xs text-gray-300 whitespace-pre-wrap">
                {JSON.stringify({ result, sessionHistory, sessionId }, null, 2)}
              </pre>
            </div>
          </details>
        </div>

        {/* Recommendations */}
        <div className="mt-4 bg-blue-500/10 border border-blue-500/30 rounded-lg p-3">
          <h4 className="font-semibold text-blue-300 mb-2">💡 Recommendations</h4>
          <div className="text-sm text-blue-200 space-y-1">
            {missingFields.length > 0 && (
              <div>• Check backend API response for missing analysis fields</div>
            )}
            {resultAnalysis.summary.naValues > 0 && (
              <div>• Investigate why N/A values are being returned instead of actual data</div>
            )}
            {resultAnalysis.summary.nullValues > 0 && (
              <div>• Review backend processing for null value handling</div>
            )}
            <div>• Ensure audio analysis is running and returning data</div>
            <div>• Verify all analysis services are functioning correctly</div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default DataDiagnosticPanel;
