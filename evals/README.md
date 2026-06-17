# Evaluation Results

## How to run
```bash
python evals/run.py
```

## Results (latest run)

| Agent    | Precision | Recall | F1    |
|----------|-----------|--------|-------|
| Security | 100%      | 100%   | 100%  |
| Style    | 100%      | 100%   | 100%  |
| Tests    | 85.7%     | 85.7%  | 85.7% |
| **Overall** | —      | **96%** | —   |

False positive rate: 11.1% (1/9 clean diffs flagged)

## Methodology
- 34 test cases: 25 injected bugs + 9 adversarial clean diffs
- Scoring: deterministic keyword matching, no LLM judge
- Initial 100% results led to hardening the dataset with subtle bugs
  and adversarial cases, which exposed real failure modes
- Prompt engineering iteration improved test agent F1 from 71.4% to 85.7%