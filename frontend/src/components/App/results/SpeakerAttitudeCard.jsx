import React from 'react';
import { Card, CardContent } from "@/components/ui/card";
import { CheckCircle, XCircle } from 'lucide-react';


const ListItem = ({ item }) => (
  <li className="text-gray-300 text-sm bg-black/20 p-2 rounded-md border border-white/10">
    {item}
  </li>
);

const SpeakerAttitudeCard = ({ attitude }) => {
  if (!attitude) {
    return (
      <Card className="bg-transparent shadow-none border-none rounded-none">
        <CardContent className="p-0">
          <div className="bg-black/30 backdrop-blur-sm border border-white/20 rounded-lg p-4">
            <p className="text-gray-400">Speaker attitude data not available.</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  const {
    respect_level_score = 50,
    sarcasm_detected = false,
    sarcasm_confidence_score = 0,
    tone_indicators_respect_sarcasm = []
  } = attitude;

  return (
    <Card className="bg-transparent shadow-none border-none rounded-none">
      <CardContent className="p-0 space-y-4"> {/* Added space-y-4 here */}
        {/* Removed the intermediate div */}
        <div>
          <h4 className="text-md font-semibold text-cyan-300 mb-2">Respect Level Score</h4>
          <div className="flex items-center">
            <div className="w-full bg-gray-700 rounded-full h-2.5 mr-3">
              <div
                className="bg-cyan-500 h-2.5 rounded-full"
                style={{ width: `${respect_level_score}%` }}
              ></div>
            </div>
            <span className="text-cyan-200 font-bold">{respect_level_score}/100</span>
          </div>
          <p className="text-xs text-gray-400 mt-1">Higher score indicates more respectful tone.</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <h4 className="text-md font-semibold text-yellow-300 mb-2">Sarcasm Detected</h4>
            <div className="flex items-center space-x-2">
              {sarcasm_detected ?
                <CheckCircle className="w-5 h-5 text-yellow-400" /> :
                <XCircle className="w-5 h-5 text-gray-400" />
              }
              <span className={`text-lg font-semibold ${sarcasm_detected ? 'text-yellow-200' : 'text-gray-300'}`}>
                {sarcasm_detected ? "Yes" : "No"}
              </span>
            </div>
          </div>

          {sarcasm_detected && (
            <div>
              <h4 className="text-md font-semibold text-yellow-300 mb-2">Sarcasm Confidence</h4>
              <div className="flex items-center">
                <div className="w-full bg-gray-700 rounded-full h-2.5 mr-3">
                  <div
                    className="bg-yellow-500 h-2.5 rounded-full"
                    style={{ width: `${sarcasm_confidence_score}%` }}
                  ></div>
                </div>
                <span className="text-yellow-200 font-bold">{sarcasm_confidence_score}/100</span>
              </div>
            </div>
          )}
        </div>

        <div>
          <h4 className="text-md font-semibold text-pink-300 mb-2">Tone Indicators (Respect/Sarcasm)</h4>
          {tone_indicators_respect_sarcasm.length > 0 ? (
            <ul className="space-y-1 list-disc list-inside pl-1">
              {tone_indicators_respect_sarcasm.map((indicator, index) => <ListItem key={index} item={indicator} />)}
            </ul>
          ) : (
            <p className="text-gray-400 text-sm">None provided.</p>
          )}
        </div>      </CardContent>
    </Card>
  );
};

export default SpeakerAttitudeCard;
