import React from 'react';
import { ResponsiveContainer, RadialBarChart, RadialBar, Legend, Tooltip as RechartTooltip } from 'recharts';
import ArgumentAnalysisCard from './ArgumentAnalysisCard';
import ConfidenceChip from '@/components/ui/ConfidenceChip';
import Tooltip from '@/components/ui/tooltip';

const mapServiceToCard = (svc) => {
  if (!svc) return null;
  // The service might return score 0..1 or 0..100
  let overall_argument_coherence_score = svc.overall_argument_coherence_score ?? svc.score ?? svc.argument_score;
  if (typeof overall_argument_coherence_score === 'number' && overall_argument_coherence_score <= 1) {
    overall_argument_coherence_score = Math.round(overall_argument_coherence_score * 100);
  }
  return {
    argument_strengths: svc.strengths || svc.argument_strengths || svc.strengths || [],
    argument_weaknesses: svc.weaknesses || svc.argument_weaknesses || svc.weaknesses || [],
    overall_argument_coherence_score: overall_argument_coherence_score || 0,
  };
};

const ArgumentStructurePanel = ({ serviceData, finalArgument }) => {
  const analysis = finalArgument || mapServiceToCard(serviceData);
  const score = analysis ? Math.max(0, Math.min(100, analysis.overall_argument_coherence_score || 0)) : 0;

  const claims = (serviceData && serviceData.key_arguments) || (analysis && analysis.key_arguments) || [];

  return (
    <div className="space-y-4">
      <h4 className="text-lg font-semibold text-blue-300 mb-2">Argument Structure</h4>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-gray-800/40 rounded p-4 md:col-span-1">
          <div className="text-sm text-gray-400 mb-1">Argument Coherence</div>
          <div style={{ height: 120 }}>
            <ResponsiveContainer width="100%" height={120}>
              <RadialBarChart cx="50%" cy="50%" innerRadius="60%" outerRadius="100%" barSize={10} data={[{ name: 'score', value: score, fill: '#60a5fa' }]} startAngle={180} endAngle={-180}>
                <RadialBar minAngle={15} background dataKey="value" cornerRadius={10} />
                <Legend payload={[{ value: `${score}%`, type: 'square', color: '#60a5fa' }]} layout="vertical" verticalAlign="middle" align="center" />
                <RechartTooltip />
              </RadialBarChart>
            </ResponsiveContainer>
          </div>
          <div className="text-center mt-2 text-white font-semibold">{score}/100</div>
        </div>

        <div className="bg-gray-800/40 rounded p-4 md:col-span-2">
          <h5 className="text-sm text-gray-300">Claims & Evidence</h5>
          {claims.length === 0 ? (
            <p className="text-gray-400 mt-2">No key arguments identified.</p>
          ) : (
            <ul className="space-y-2 mt-2 text-sm text-gray-300">
              {claims.map((c, idx) => (
                <li key={idx} className="bg-black/20 rounded p-3 border border-white/10">
                  <div className="font-medium">Claim: {c.claim || c.text || '—'}</div>
                  {c.evidence && <div className="text-gray-400 text-xs mt-1">Evidence: {c.evidence}</div>}
                  {c.confidence && (
                    <div className="text-xs mt-1">Confidence: <ConfidenceChip value={Math.round((c.confidence||0)*100)} /></div>
                  )}
                  {c.claim && <div className="text-xs mt-1"> <Tooltip text={c.evidence || 'No evidence provided'}>More info</Tooltip></div>}
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>

      <ArgumentAnalysisCard analysis={analysis} />
    </div>
  );
};

export default ArgumentStructurePanel;