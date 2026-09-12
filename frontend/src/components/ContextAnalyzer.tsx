import { useEffect, useState } from "react";
import type { ModelId, ModelSummary, ContextAnalysisResponse } from "../types/tokenizer";
import { getContextAnalysis } from "../services/api";

interface ContextAnalyzerProps {
  models: ModelSummary[];
  tokenCountsByModel: Partial<Record<ModelId, number>>;
}

const SEVERITY_LABEL: Record<ContextAnalysisResponse["severity"], string> = {
  ok: "Comfortable",
  warning: "Getting close",
  critical: "Nearly full",
  over_limit: "Over the limit",
};

export function ContextAnalyzer({ models, tokenCountsByModel }: ContextAnalyzerProps) {
  const [selectedModel, setSelectedModel] = useState<ModelId | "">(models[0]?.id ?? "");
  const [maxTokens, setMaxTokens] = useState<number>(models[0]?.default_context_window ?? 1024);
  const [result, setResult] = useState<ContextAnalysisResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!selectedModel) return;
    const model = models.find((m) => m.id === selectedModel);
    if (model) setMaxTokens(model.default_context_window);
    // Only re-run when the selected model changes, not on every models array identity change.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedModel]);

  useEffect(() => {
    const tokenCount = selectedModel ? tokenCountsByModel[selectedModel] : undefined;
    if (!selectedModel || tokenCount === undefined || maxTokens <= 0) {
      setResult(null);
      return;
    }

    let cancelled = false;
    getContextAnalysis(selectedModel, tokenCount, maxTokens)
      .then((data) => {
        if (!cancelled) {
          setResult(data);
          setError(null);
        }
      })
      .catch((err: Error) => {
        if (!cancelled) setError(err.message);
      });

    return () => {
      cancelled = true;
    };
  }, [selectedModel, maxTokens, tokenCountsByModel]);

  if (models.length === 0) return null;

  return (
    <div className="context-analyzer">
      <h3>Context Window Analysis</h3>
      <div className="context-analyzer__controls">
        <label>
          Model
          <select value={selectedModel} onChange={(e) => setSelectedModel(e.target.value as ModelId)}>
            {models.map((m) => (
              <option key={m.id} value={m.id}>
                {m.name}
              </option>
            ))}
          </select>
        </label>
        <label>
          Configured max context (tokens)
          <input
            type="number"
            min={1}
            value={maxTokens}
            onChange={(e) => setMaxTokens(Number(e.target.value))}
          />
        </label>
      </div>
      <p className="context-analyzer__note">
        This limit is configurable and not a universal fact — set it to match whatever model context size you
        want to reason about.
      </p>

      {error && <p className="context-analyzer__error">{error}</p>}

      {result && (
        <div className={`context-analyzer__result context-analyzer__result--${result.severity}`}>
          <div className="context-analyzer__bar-track">
            <div
              className="context-analyzer__bar-fill"
              style={{ width: `${Math.min(result.percentage_used, 100)}%` }}
            />
          </div>
          <div className="context-analyzer__summary">
            <span>
              {result.current_tokens} / {result.max_tokens} tokens
            </span>
            <span>{result.percentage_used}% utilized</span>
            <span className="context-analyzer__severity">{SEVERITY_LABEL[result.severity]}</span>
          </div>
        </div>
      )}
    </div>
  );
}
