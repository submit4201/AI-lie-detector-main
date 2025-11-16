
//**We are in frontend/src/utils/serviceSelectors.js
 // Utility functions to extract and derive data from service payloads
 // we need to make better efforts to document these functions and their expected inputs and outputs */
console.warn("we are in frontend/src/utils/serviceSelectors.js - make sure to keep these functions documented and updated as services evolve")
//** @param {*} services 
 // @param {*} serviceName 
 //@returns */

export const getServicePayload = (services = {}, serviceName) => {
  if (!services || typeof services !== 'object') {
    return null;
  }
  return services[serviceName] || null;
};

export const selectQuantitativeMetrics = (services = {}) => {
  const payload = getServicePayload(services, 'quantitative_metrics');
  if (!payload) {
    return null;
  }

  return {
    payload,
    numerical: payload?.local?.numerical_linguistic_metrics || null,
    interaction: payload?.gemini?.interaction_metrics || null,
  };
};

const normalizeNumber = (value, fallback = null) => {
  const parsed = Number(value);
  if (Number.isFinite(parsed)) {
    return parsed;
  }
  return fallback;
};

const mapNumericalMetricsToLegacyShape = (numerical) => {
  if (!numerical) {
    return null;
  }

  const mapped = {
    word_count: numerical.word_count,
    unique_word_count: numerical.unique_word_count,
    hesitation_count: numerical.hesitation_marker_count,
    filler_count: numerical.filler_word_count,
    qualifier_count: numerical.qualifier_count,
    certainty_count: numerical.certainty_indicator_count,
    repetition_count: numerical.repetition_count,
    sentence_count: numerical.sentence_count,
    avg_word_length: numerical.avg_word_length_chars,
    avg_sentence_length_words: numerical.avg_sentence_length_words,
    speech_rate_wpm: numerical.speech_rate_wpm,
    hesitation_rate: numerical.hesitation_rate_hpm,
    vocabulary_richness: numerical.vocabulary_richness_ttr,
    confidence_ratio: numerical.confidence_metric_ratio,
    formality_score: numerical.formality_score_calculated,
    complexity_score: numerical.complexity_score_calculated,
  };

  return mapped;
};

export const buildServiceBackedLinguisticAnalysis = (services, legacy) => {
  const quantitative = selectQuantitativeMetrics(services);
  if (!quantitative?.numerical) {
    return legacy || null;
  }

  const mapped = mapNumericalMetricsToLegacyShape(quantitative.numerical);
  if (!mapped) {
    return legacy || null;
  }

  return legacy ? { ...legacy, ...mapped } : mapped;
};

const toPercentageScore = (value) => {
  if (value === null || value === undefined) {
    return null;
  }
  const numeric = normalizeNumber(value, null);
  if (numeric === null) {
    return null;
  }
  if (numeric > 1) {
    return Math.round(numeric);
  }
  return Math.round(numeric * 100);
};

export const deriveCredibilityScoreFromServices = (services, fallback) => {
  const quantitative = selectQuantitativeMetrics(services);
  const interactionScore = quantitative?.interaction?.overall_sentiment_score;
  const derived = toPercentageScore(interactionScore);
  return derived ?? fallback ?? null;
};

const deriveRiskLevelFromSentiment = (label) => {
  if (!label) return null;
  const normalized = label.toLowerCase();
  if (normalized === 'negative') {
    return 'high';
  }
  if (normalized === 'neutral') {
    return 'medium';
  }
  return 'low';
};

export const deriveRiskAssessmentFromServices = (services, fallback) => {
  const quantitative = selectQuantitativeMetrics(services);
  const interaction = quantitative?.interaction;
  if (!interaction) {
    return fallback || null;
  }

  const derivedRisk = deriveRiskLevelFromSentiment(interaction.overall_sentiment_label);
  const riskAssessment = {
    overall_risk: derivedRisk || fallback?.overall_risk || 'unknown',
    risk_factors: interaction.notable_interaction_events || fallback?.risk_factors || [],
  };

  return fallback ? { ...fallback, ...riskAssessment } : riskAssessment;
};

export const deriveRedFlagsFromServices = (services, fallback) => {
  const quantitative = selectQuantitativeMetrics(services);
  const interaction = quantitative?.interaction;
  const events = interaction?.notable_interaction_events;
  if (!events || events.length === 0) {
    return fallback || null;
  }

  const existing = fallback && typeof fallback === 'object' ? fallback : {};
  return {
    ...existing,
    service_insights: events,
  };
};

export const deriveSummaryFromServices = (services, fallback) => {
  const quantitative = selectQuantitativeMetrics(services);
  const interaction = quantitative?.interaction;
  if (!interaction) {
    return fallback || null;
  }

  const summary = {
    credibility: fallback?.credibility,
    key_concerns: fallback?.key_concerns,
    interaction_takeaways: interaction.notable_interaction_events?.slice(0, 3) || [],
  };

  if (!summary.credibility && interaction.overall_sentiment_label) {
    summary.credibility = `Overall sentiment appears ${interaction.overall_sentiment_label}.`;
  }

  if (!summary.key_concerns && interaction.engagement_level) {
    summary.key_concerns = `Engagement level assessed as ${interaction.engagement_level}.`;
  }

  return summary;
};

export const deriveRecommendationsFromServices = (services, fallback) => {
  const quantitative = selectQuantitativeMetrics(services);
  const interaction = quantitative?.interaction;
  if (!interaction) {
    return fallback || null;
  }

  if (interaction.notable_interaction_events && interaction.notable_interaction_events.length) {
    const generated = interaction.notable_interaction_events.map((event) => `Investigate "${event}" further.`);
    return generated;
  }

  return fallback || null;
};

export const deriveConversationGuidanceFromServices = (services, fallback) => {
  const quantitative = selectQuantitativeMetrics(services);
  const interaction = quantitative?.interaction;
  if (!interaction) {
    return fallback || null;
  }

  const followUps = interaction.question_to_statement_ratio && interaction.question_to_statement_ratio > 0.4
    ? ['Ask clarifying questions about statements with high uncertainty.']
    : [];
  const inconsistencies = interaction.notable_interaction_events?.filter((event) => event.toLowerCase().includes('inconsist')) || [];

  const guidance = {
    suggested_follow_up_questions: followUps.length ? followUps : fallback?.suggested_follow_up_questions,
    key_inconsistencies: inconsistencies.length ? inconsistencies : fallback?.key_inconsistencies,
    areas_of_evasiveness: fallback?.areas_of_evasiveness,
    unverified_claims: fallback?.unverified_claims,
  };

  return fallback ? { ...fallback, ...guidance } : guidance;
};

export const buildServiceAwareEmotionAnalysis = (services, legacy) => {
  const quantitative = selectQuantitativeMetrics(services);
  const interaction = quantitative?.interaction;
  if (!interaction) {
    return legacy || null;
  }

  const derived = {
    dominant_emotion: interaction.overall_sentiment_label || legacy?.dominant_emotion,
    confidence: interaction.sentiment_confidence ?? legacy?.confidence,
    emotion_distribution: interaction.emotion_distribution || legacy?.emotion_distribution || [],
  };

  return legacy ? { ...legacy, ...derived } : derived;
};

export const getServicesFromResult = (result) => {
  if (!result) {
    return {};
  }
  if (result.services) {
    return result.services;
  }
  return {};
};
