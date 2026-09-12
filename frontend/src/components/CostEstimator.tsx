import { useEffect, useState } from "react";
import type { ModelId, ModelAnalysis, CostEstimateResponse } from "../types/tokenizer";
import { getCostEstimate } from "../services/api";

interface CostEstimatorProps {
  results: ModelAnalysis[];
}

const DEFAULT_PRICE = 1.5; // per 1,000 tokens - a starting point only, not an authoritative provider price.

export function CostEstimator({ results }: CostEstimatorProps) {
  const [price, setPrice] = useState<number>(DEFAULT_PRICE);
  const [selectedModel, setSelectedModel] = useState<ModelId | "">(results[0]?.model ?? "");
  const [estimate, setEstimate] = useState<CostEstimateResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Keep the selected model valid as the set of tokenized results changes.
  useEffect(() => {
    if (results.length === 0) {
      setSelectedModel("");
      return;
    }
    if (!results.some((r) => r.model === selectedModel)) {
      setSelectedModel(results[0].model);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [results]);

  useEffect(() => {
    const active = results.find((r) => r.model === selectedModel);
    if (!active || price < 0) {
      setEstimate(null);
      return;
    }

    let cancelled = false;
    getCostEstimate(active.token_count, price)
      .then((data) => {
        if (!cancelled) {
          setEstimate(data);
          setError(null);
        }
      })
      .catch((err: Error) => {
        if (!cancelled) setError(err.message);
      });

    return () => {
      cancelled = true;
    };
  }, [selectedModel, price, results]);

  if (results.length === 0) return null;

  return (
    <div className="cost-estimator">
      <h3>Cost Estimator</h3>
      <p className="cost-estimator__note">
        This is a configurable estimate you control - it is not a real price quoted by GPT-2, BERT, or any
        provider's API.
      </p>

      <div className="cost-estimator__controls">
        <label>
          Model
          <select value={selectedModel} onChange={(e) => setSelectedModel(e.target.value as ModelId)}>
            {results.map((r) => (
              <option key={r.model} value={r.model}>
                {r.display_name}
              </option>
            ))}
          </select>
        </label>
        <label>
          Price per 1,000 tokens ($)
          <input
            type="number"
            min={0}
            step={0.01}
            value={price}
            onChange={(e) => setPrice(Number(e.target.value))}
          />
        </label>
      </div>

      {error && <p className="cost-estimator__error">{error}</p>}

      {estimate && (
        <div className="cost-estimator__result">
          <div className="cost-estimator__figure">
            <span className="cost-estimator__value">${estimate.estimated_cost.toFixed(6)}</span>
            <span className="cost-estimator__label">estimated cost</span>
          </div>
          <div className="cost-estimator__breakdown">
            {estimate.token_count.toLocaleString()} tokens × ${estimate.price_per_1000_tokens.toFixed(4)} / 1,000
          </div>
        </div>
      )}
    </div>
  );
}
