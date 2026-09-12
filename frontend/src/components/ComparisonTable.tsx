import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";
import type { ModelAnalysis } from "../types/tokenizer";

interface ComparisonTableProps {
  results: ModelAnalysis[];
}

const ROWS: { key: keyof ModelAnalysis; label: string }[] = [
  { key: "token_count", label: "Token count" },
  { key: "unique_token_count", label: "Unique tokens" },
  { key: "characters_per_token", label: "Characters per token" },
  { key: "tokens_per_word", label: "Tokens per word" },
];

export function ComparisonTable({ results }: ComparisonTableProps) {
  if (results.length < 2) {
    return null;
  }

  const chartData = ROWS.filter((r) => r.key === "token_count").length
    ? results.map((r) => ({ name: r.display_name, tokens: r.token_count }))
    : [];

  return (
    <div className="comparison-table">
      <h3>Tokenizer Comparison</h3>
      <p className="comparison-table__disclaimer">
        Different token counts reflect different vocabularies and tokenization strategies — this does not mean
        one tokenizer is "better" overall.
      </p>

      <table>
        <thead>
          <tr>
            <th>Metric</th>
            {results.map((r) => (
              <th key={r.model}>{r.display_name}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {ROWS.map((row) => (
            <tr key={row.key}>
              <td>{row.label}</td>
              {results.map((r) => (
                <td key={r.model}>{r[row.key]}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>

      <div className="comparison-table__chart">
        <ResponsiveContainer width="100%" height={220}>
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" />
            <XAxis dataKey="name" tick={{ fill: "var(--text-secondary)", fontSize: 12 }} />
            <YAxis tick={{ fill: "var(--text-secondary)", fontSize: 12 }} allowDecimals={false} />
            <Tooltip
              contentStyle={{ background: "var(--surface)", border: "1px solid var(--border-color)" }}
            />
            <Bar dataKey="tokens" fill="var(--accent)" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
