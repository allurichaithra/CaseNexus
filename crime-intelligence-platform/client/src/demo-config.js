// CaseNexus Golden Demo Configuration
// Use these exact IDs during the hackathon pitch demo.

export const DEMO_CONFIG = {
  // Case Link Demo: FIR 1792 → FIR 2823
  // Confidence: 0.80, Narrative: 1.0 (identical modus operandi)
  // Same district (1001), different police stations
  // Ground truth: CyberPhishing series
  caseLinkDemo: {
    sourceCaseId: 1792,
    targetCaseId: 2823,
    confidence: 0.80,
    signals: ['narrative_match', 'geographic_proximity', 'crime_head_match'],
  },

  // Cross-Jurisdiction Demo: FIR 803 → FIR 2917
  // Confidence: 0.90, Narrative: 1.0
  // Different districts — demonstrates cross-jurisdiction linking
  crossJurisdictionDemo: {
    sourceCaseId: 803,
    targetCaseId: 2917,
    confidence: 0.90,
    signals: ['narrative_match', 'crime_head_match'],
  },

  // Entity Resolution Demo: "Sunita Kulkarni"
  // Appears across 56 FIRs — demonstrates repeat-offender detection
  entityDemo: {
    name: 'Sunita Kulkarni',
    caseCount: 56,
    sampleCaseIds: [93, 105, 188, 200, 209],
  },
};
