import { useState } from "react";
import type { TokenizeResult, TokenDetail } from "../types/tokenizer";

const RENDER_LIMIT = 500;

interface TokenViewerProps {
  result: TokenizeResult;
}

/** Renders whitespace-only or empty tokens visibly instead of collapsing to nothing. */
function displayText(text: string): string {
  if (text.trim() === "") {
    return text.length === 0 ? "∅" : "·".repeat(text.length);
  }
  return text;
}

export function TokenViewer({ result }: TokenViewerProps) {
  const [activeToken, setActiveToken] = useState<TokenDetail | null>(null);
  const visibleTokens = result.tokens.slice(0, RENDER_LIMIT);
  const truncated = result.tokens.length > RENDER_LIMIT;

  return (
    <div className="token-viewer">
      <div className="token-viewer__header">
        <h4>{result.display_name}</h4>
        <span className="token-viewer__count">{result.token_count} tokens</span>
      </div>

      <div className="token-viewer__tokens" role="list">
        {visibleTokens.map((token) => (
          <button
            key={token.position}
            type="button"
            role="listitem"
            className="token-viewer__token"
            onMouseEnter={() => setActiveToken(token)}
            onFocus={() => setActiveToken(token)}
            onClick={() => setActiveToken(token)}
            aria-label={`Token ${token.position}: "${token.text}", id ${token.token_id}`}
          >
            {displayText(token.text)}
          </button>
        ))}
      </div>

      {truncated && (
        <p className="token-viewer__truncated-note">
          Showing the first {RENDER_LIMIT} of {result.tokens.length} tokens for performance.
        </p>
      )}

      <div className="token-viewer__detail" aria-live="polite">
        {activeToken ? (
          <>
            <strong>Token:</strong> "{activeToken.text}" &nbsp;|&nbsp;
            <strong>ID:</strong> {activeToken.token_id} &nbsp;|&nbsp;
            <strong>Position:</strong> {activeToken.position}
          </>
        ) : (
          <span className="token-viewer__detail-hint">Hover or click a token to see its details.</span>
        )}
      </div>
    </div>
  );
}
