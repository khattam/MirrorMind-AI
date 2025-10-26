# Debate Metrics

This directory contains automatically collected debate analytics.

## Files

- `debate_metrics.json` - All recorded debate statistics

## Metrics Collected

For each debate, we track:

### Basic Stats
- **Debate ID** - Unique identifier with timestamp
- **Dilemma Title** - The ethical question debated
- **Total Turns** - Number of argument rounds
- **Total Words** - Combined word count across all arguments
- **Number of Agents** - How many agents participated

### Word Analysis
- **Average Words per Turn** - Overall debate verbosity
- **Average Words per Agent** - Individual agent verbosity
- **Agent Word Counts** - Total words by each agent
- **Most Verbose Agent** - Who spoke the most

### Debate Dynamics
- **Stance Changes** - How many times each agent changed position
- **Intensity Score** - Debate engagement metric (words/turn)
- **Agent Turn Counts** - Number of turns per agent

### Verdict
- **Final Recommendation** - Which option won (A or B)
- **Confidence** - Judge's confidence level (0-100)
- **Ethical Scores** - Breakdown by ethical dimensions

## Viewing Metrics

### Command Line
```bash
cd backend
python view_metrics.py
```

### API Endpoints
```bash
# Get all metrics
GET http://localhost:8000/api/metrics

# Get summary statistics
GET http://localhost:8000/api/metrics/summary
```

### Direct File Access
```bash
cat backend/data/debate_metrics.json | python -m json.tool
```

## Example Metrics

```json
{
  "debate_id": "debate_20241225_143022",
  "timestamp": "2024-12-25T14:30:22.123456",
  "dilemma_title": "AI Diagnosis Override",
  "total_turns": 9,
  "total_words": 1247,
  "num_agents": 3,
  "agents": ["Deon", "Conse", "Virtue"],
  "avg_words_per_turn": 138.56,
  "most_verbose_agent": "Conse",
  "intensity_score": 138.56,
  "final_recommendation": "B",
  "confidence": 75
}
```

## Privacy

All metrics are stored locally and never transmitted externally. This data is for your analysis only.
