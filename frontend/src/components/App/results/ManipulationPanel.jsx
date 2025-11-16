import React from 'react';
import { ResponsiveContainer, RadialBarChart, RadialBar, Legend, Tooltip as RechartTooltip, BarChart, Bar, XAxis, YAxis, CartesianGrid } from 'recharts';
import Tooltip from '@/components/ui/tooltip';
import ManipulationAssessmentCard from './ManipulationAssessmentCard';

const normalizeServiceToAssessment = (svc) => {
  if (!svc) return null;
  // Some service payloads may use 'score' (0..1) or 'manipulation_score' (0..100)
  let manipulation_score = svc.manipulation_score ?? svc.score ?? svc.manipulation_score_percent;
  if (typeof manipulation_score === 'number' && manipulation_score <= 1) {
    manipulation_score = Math.round(manipulation_score * 100);
  }
  return {
    manipulation_score: manipulation_score ?? 0,
    manipulation_tactics: svc.tactics || svc.manipulation_tactics || svc.flags || [],
    manipulation_explanation: svc.explanation || svc.rationale || svc.manipulation_explanation || '',
    example_phrases: svc.examples || svc.example_phrases || [],
  };
};

const tacticsToChartData = (tactics) => {
  if (!tactics || tactics.length === 0) return [];
  const counts = {};
  tactics.forEach((t) => {
    const key = typeof t === 'string' ? t : t.name || JSON.stringify(t);
    counts[key] = (counts[key] || 0) + 1;
  });
  return Object.entries(counts).map(([name, value]) => ({ name, value }));
};

const ManipulationPanel = ({ serviceData, finalAssessment }) => {
  const assessment = finalAssessment || normalizeServiceToAssessment(serviceData);
  const score = assessment ? Math.max(0, Math.min(100, assessment.manipulation_score || 0)) : 0;
  const tactics = assessment ? assessment.manipulation_tactics || [] : [];
  const chartData = tacticsToChartData(tactics);

  return (
    <div className="space-y-4">
      <h4 className="text-lg font-semibold text-purple-300 mb-2">Influence Signals</h4>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="md:col-span-1 bg-gray-800/40 rounded p-4">
          <div className="text-sm text-gray-400 mb-1">Manipulation Score</div>
          <div style={{ height: 150 }}>
            <ResponsiveContainer width="100%" height={150}>
              <RadialBarChart cx="50%" cy="50%" innerRadius="60%" outerRadius="100%" barSize={10} data={[{ name: 'score', value: score, fill: '#a78bfa' }]} startAngle={180} endAngle={-180}>
                <RadialBar minAngle={15} background dataKey="value" cornerRadius={10} />
                <Legend payload={[{ value: `${score}%`, type: 'square', color: '#a78bfa' }]} layout="vertical" verticalAlign="middle" align="center" />
                <Tooltip />
              </RadialBarChart>
            </ResponsiveContainer>
          </div>
          <div className="text-center mt-2 text-white font-semibold">{score}/100</div>
        </div>

        <div className="md:col-span-2 bg-gray-800/40 rounded p-4">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-sm text-gray-400">Detected Tactics</div>
              <div className="text-white font-medium">{tactics.length} tactics</div>
            </div>
            <div className="text-xs text-gray-400 flex items-center gap-2">Top tactics used in the analysis</div>
          </div>

          {chartData.length > 0 ? (
            <div style={{ height: 140 }} className="mt-4">
              <ResponsiveContainer width="100%" height={140}>
                <BarChart data={chartData} margin={{ left: 0, right: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#2d2d2d" />
                  <XAxis dataKey="name" tick={{ fill: '#cbd5e1', fontSize: 12 }} />
                  <YAxis tick={{ fill: '#cbd5e1', fontSize: 12 }} />
                  <RechartTooltip contentStyle={{ background: '#1f2937', border: 'none' }} itemStyle={{ color: '#fff' }} />
                  <Bar dataKey="value" fill="#a78bfa" barSize={20} />
                </BarChart>
              </ResponsiveContainer>
            </div>
            ) : (
              <p className="text-gray-400 mt-4">No tactics identified yet.</p>
            )}

            {/* Tactic chips */}
            {chartData.length > 0 && (
              <div className="flex flex-wrap gap-2 mt-4">
                {chartData.map((d) => (
                  <Tooltip key={d.name} text={`Found ${d.value} instance(s)`}> 
                    <div className="text-xs bg-black/30 border border-white/10 px-2 py-1 rounded text-gray-300">{d.name} • {d.value}</div>
                  </Tooltip>
                ))}
              </div>
            )}

          <div className="mt-4">
            <h5 className="text-sm text-gray-300">Rationale & Examples</h5>
            <p className="text-gray-300 text-sm mt-2">{assessment?.manipulation_explanation || 'No rationale provided.'}</p>
            {assessment?.example_phrases && assessment.example_phrases.length > 0 && (
              <ul className="list-disc ml-5 mt-2 text-sm text-gray-300">
                {assessment.example_phrases.map((p, idx) => (
                  <li key={idx}>{p}</li>
                ))}
              </ul>
            )}
          </div>
        </div>
      </div>

      {/* Existing card that shows a full breakdown */}
      <ManipulationAssessmentCard assessment={assessment} />
    </div>
  );
};

export default ManipulationPanel;