import type { ModelAnalysis } from "../types/tokenizer";

interface StatisticsCardProps {
  analysis: ModelAnalysis;
}

const STAT_LABELS: { key: keyof ModelAnalysis; label: string; hint?: string }[] = [
  { key: "character_count", label: "Characters" },
  { key: "word_count", label: "Words", hint: "Whitespace-delimited" },
  { key: "token_count", label: "Tokens" },
  { key: "unique_token_count", label: "Unique tokens" },
  { key: "characters_per_token", label: "Chars / token" },
  { key: "tokens_per_word", label: "Tokens / word" },
];

export function StatisticsCard({ analysis }: StatisticsCardProps) {
  return (
    <div className="statistics-card">
      <h4 className="statistics-card__title">{analysis.display_name}</h4>
      <div className="statistics-card__grid">
        {STAT_LABELS.map(({ key, label, hint }) => (
          <div key={key} className="statistics-card__stat">
            <span className="statistics-card__value">{analysis[key]}</span>
            <span className="statistics-card__label">{label}</span>
            {hint && <span className="statistics-card__hint">{hint}</span>}
          </div>
        ))}
      </div>
    </div>
  );
}
