/**
 * Types mirror the backend Pydantic schemas exactly (see
 * backend/app/schemas/). Keeping these in sync is what lets the frontend
 * avoid `any` on API response objects.
 */

export type ModelId = "gpt2" | "bert-base-cased";

export interface ModelSummary {
  id: ModelId;
  name: string;
  default_context_window: number;
}

export interface ModelsResponse {
  models: ModelSummary[];
}

export interface HealthResponse {
  status: string;
}

export interface TokenDetail {
  text: string;
  token_id: number;
  position: number;
}

export interface TokenizeResult {
  model: ModelId;
  display_name: string;
  tokens: TokenDetail[];
  token_count: number;
  special_tokens_used: string[];
}

export interface TokenizeResponse {
  results: TokenizeResult[];
}

export interface ModelAnalysis {
  model: ModelId;
  display_name: string;
  character_count: number;
  word_count: number;
  token_count: number;
  unique_token_count: number;
  characters_per_token: number;
  tokens_per_word: number;
}

export interface AnalyzeResponse {
  results: ModelAnalysis[];
}

export interface CompareResponse {
  character_count: number;
  word_count: number;
  results: ModelAnalysis[];
}

export type ContextSeverity = "ok" | "warning" | "critical" | "over_limit";

export interface ContextAnalysisResponse {
  current_tokens: number;
  max_tokens: number;
  remaining_tokens: number;
  percentage_used: number;
  severity: ContextSeverity;
}

export interface CostEstimateResponse {
  token_count: number;
  price_per_1000_tokens: number;
  estimated_cost: number;
}

export interface ApiErrorBody {
  detail: string;
}

/** Thrown by the api client on any non-2xx response. */
export class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}
