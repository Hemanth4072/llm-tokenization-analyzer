import type {
  ModelsResponse,
  HealthResponse,
  TokenizeResponse,
  AnalyzeResponse,
  CompareResponse,
  ContextAnalysisResponse,
  CostEstimateResponse,
  ApiErrorBody,
  ModelId,
} from "../types/tokenizer";
import { ApiError } from "../types/tokenizer";

const BASE_URL = "/api";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${BASE_URL}${path}`, {
      headers: { "Content-Type": "application/json" },
      ...options,
    });
  } catch {
    throw new ApiError("Could not reach the server. Is the backend running?", 0);
  }

  if (!response.ok) {
    let detail = `Request failed with status ${response.status}.`;
    try {
      const body = (await response.json()) as ApiErrorBody | { detail?: unknown };
      if (typeof body.detail === "string") {
        detail = body.detail;
      }
    } catch {
      // Response wasn't JSON; fall back to the generic message above.
    }
    throw new ApiError(detail, response.status);
  }

  return (await response.json()) as T;
}

export function getHealth(): Promise<HealthResponse> {
  return request<HealthResponse>("/health");
}

export function getModels(): Promise<ModelsResponse> {
  return request<ModelsResponse>("/models");
}

export function tokenizeText(text: string, models: ModelId[]): Promise<TokenizeResponse> {
  return request<TokenizeResponse>("/tokenize", {
    method: "POST",
    body: JSON.stringify({ text, models }),
  });
}

export function analyzeText(text: string, models: ModelId[]): Promise<AnalyzeResponse> {
  return request<AnalyzeResponse>("/analyze", {
    method: "POST",
    body: JSON.stringify({ text, models }),
  });
}

export function compareText(text: string, models: ModelId[]): Promise<CompareResponse> {
  return request<CompareResponse>("/compare", {
    method: "POST",
    body: JSON.stringify({ text, models }),
  });
}

export function getContextAnalysis(
  model: ModelId,
  tokenCount: number,
  maxTokens: number
): Promise<ContextAnalysisResponse> {
  return request<ContextAnalysisResponse>("/context-analysis", {
    method: "POST",
    body: JSON.stringify({ model, token_count: tokenCount, max_tokens: maxTokens }),
  });
}

export function getCostEstimate(
  tokenCount: number,
  pricePer1000Tokens: number
): Promise<CostEstimateResponse> {
  return request<CostEstimateResponse>("/cost-estimate", {
    method: "POST",
    body: JSON.stringify({ token_count: tokenCount, price_per_1000_tokens: pricePer1000Tokens }),
  });
}
