import { useEffect, useMemo, useState } from "react";
import type { ModelId, ModelSummary, TokenizeResult, ModelAnalysis } from "../types/tokenizer";
import { getModels, getHealth, tokenizeText, analyzeText } from "../services/api";
import { ApiError } from "../types/tokenizer";
import { LANGUAGE_SAMPLES } from "../constants/samples";

import { TextInput } from "../components/TextInput";
import { ModelSelector } from "../components/ModelSelector";
import { TokenViewer } from "../components/TokenViewer";
import { StatisticsCard } from "../components/StatisticsCard";
import { ComparisonTable } from "../components/ComparisonTable";
import { ContextAnalyzer } from "../components/ContextAnalyzer";
import { CostEstimator } from "../components/CostEstimator";

type ApiStatus = "checking" | "online" | "offline";

export function Dashboard() {
  const [apiStatus, setApiStatus] = useState<ApiStatus>("checking");
  const [models, setModels] = useState<ModelSummary[]>([]);
  const [modelsError, setModelsError] = useState<string | null>(null);

  const [text, setText] = useState("");
  const [selectedModels, setSelectedModels] = useState<ModelId[]>([]);

  const [tokenizeResults, setTokenizeResults] = useState<TokenizeResult[]>([]);
  const [analysisResults, setAnalysisResults] = useState<ModelAnalysis[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [requestError, setRequestError] = useState<string | null>(null);
  const [hasAnalyzed, setHasAnalyzed] = useState(false);

  // Load backend health + supported models once on mount.
  useEffect(() => {
    getHealth()
      .then(() => setApiStatus("online"))
      .catch(() => setApiStatus("offline"));

    getModels()
      .then((data) => {
        setModels(data.models);
        setSelectedModels(data.models.length > 0 ? [data.models[0].id] : []);
      })
      .catch((err: Error) => setModelsError(err.message));
  }, []);

  const tokenCountsByModel = useMemo(() => {
    const map: Partial<Record<ModelId, number>> = {};
    for (const r of tokenizeResults) map[r.model] = r.token_count;
    return map;
  }, [tokenizeResults]);

  const trimmedText = text.trim();
  const canAnalyze = trimmedText.length > 0 && selectedModels.length > 0 && !isLoading;

  async function handleAnalyze() {
    if (!canAnalyze) return;
    setIsLoading(true);
    setRequestError(null);
    try {
      const [tokenizeRes, analyzeRes] = await Promise.all([
        tokenizeText(text, selectedModels),
        analyzeText(text, selectedModels),
      ]);
      setTokenizeResults(tokenizeRes.results);
      setAnalysisResults(analyzeRes.results);
      setHasAnalyzed(true);
    } catch (err) {
      const message = err instanceof ApiError ? err.message : "Something went wrong while analyzing the text.";
      setRequestError(message);
    } finally {
      setIsLoading(false);
    }
  }

  function loadSample(sampleText: string) {
    setText(sampleText);
  }

  return (
    <div className="dashboard">
      <header className="dashboard__header">
        <div>
          <h1>LLM Tokenization Analyzer</h1>
          <p className="dashboard__subtitle">
            See exactly how GPT-2 and BERT break your text into tokens - the real units these models actually
            read.
          </p>
        </div>
        <div className={`dashboard__status dashboard__status--${apiStatus}`}>
          <span className="dashboard__status-dot" />
          {apiStatus === "checking" && "Checking API..."}
          {apiStatus === "online" && "API online"}
          {apiStatus === "offline" && "API offline"}
        </div>
      </header>

      {apiStatus === "offline" && (
        <div className="dashboard__banner dashboard__banner--error">
          Can't reach the backend right now. Make sure the FastAPI server is running, then refresh.
        </div>
      )}

      {modelsError && (
        <div className="dashboard__banner dashboard__banner--error">
          Couldn't load available models: {modelsError}
        </div>
      )}

      <section className="dashboard__panel">
        <TextInput value={text} onChange={setText} disabled={isLoading} />

        <div className="dashboard__samples">
          <span className="dashboard__samples-label">Try a sample:</span>
          {LANGUAGE_SAMPLES.map((sample) => (
            <button
              key={sample.code}
              type="button"
              className="dashboard__sample-btn"
              onClick={() => loadSample(sample.text)}
              disabled={isLoading}
            >
              {sample.label}
            </button>
          ))}
        </div>

        <ModelSelector models={models} selected={selectedModels} onChange={setSelectedModels} disabled={isLoading} />

        <button type="button" className="dashboard__analyze-btn" onClick={handleAnalyze} disabled={!canAnalyze}>
          {isLoading ? "Analyzing..." : "Analyze"}
        </button>

        {!isLoading && trimmedText.length === 0 && (
          <p className="dashboard__hint">Enter some text above to get started.</p>
        )}
        {!isLoading && trimmedText.length > 0 && selectedModels.length === 0 && (
          <p className="dashboard__hint dashboard__hint--warning">Select at least one tokenizer to analyze.</p>
        )}
        {requestError && <p className="dashboard__hint dashboard__hint--error">{requestError}</p>}
      </section>

      {hasAnalyzed && !isLoading && (
        <>
          <section className="dashboard__panel">
            <h2>Tokenization</h2>
            <div className="dashboard__token-viewers">
              {tokenizeResults.map((result) => (
                <TokenViewer key={result.model} result={result} />
              ))}
            </div>
          </section>

          <section className="dashboard__panel">
            <h2>Statistics</h2>
            <div className="dashboard__stat-cards">
              {analysisResults.map((analysis) => (
                <StatisticsCard key={analysis.model} analysis={analysis} />
              ))}
            </div>
          </section>

          <ComparisonTable results={analysisResults} />

          <section className="dashboard__panel">
            <ContextAnalyzer models={models} tokenCountsByModel={tokenCountsByModel} />
          </section>

          <section className="dashboard__panel">
            <CostEstimator results={analysisResults} />
          </section>
        </>
      )}
    </div>
  );
}
