# AI bias and safety review

HireIQ is decision support, not an autonomous hiring decision-maker. The current recommendation is intentionally derived from interview evidence, not candidate demographics.

## Controls

- Do not collect or pass protected attributes to the evaluator prompt.
- Prompt and documentation instruct evaluators to ignore names, accents, age, gender, ethnicity, disability, and other protected or proxy attributes.
- Hiring managers must inspect the transcript and rationale before acting; the UI labels recommendations as support only.
- Rubric criteria are versioned in YAML and should be calibrated against job-related evidence.
- Monitor score distributions and false-negative/false-positive rates by authorized, privacy-preserving audit groups outside the model prompt.
- Provide human override, an appeal path, and an audit log before production use.
- Delete raw audio after transcription; retain only the minimum transcript and metadata necessary for the retention policy.

## Known limitations

The demo confidence score is a heuristic, not a validated speech or personality measure. Sentiment is not a proxy for competence. Before production deployment, run accessibility testing, multilingual evaluation, adverse-impact review, security review, and job-specific validation with a diverse panel.
