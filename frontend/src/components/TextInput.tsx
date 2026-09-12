import { ChangeEvent } from "react";

const MAX_CHARACTERS = 20_000;
const WARN_THRESHOLD = 0.9;

interface TextInputProps {
  value: string;
  onChange: (value: string) => void;
  disabled?: boolean;
}

export function TextInput({ value, onChange, disabled }: TextInputProps) {
  const charCount = value.length;
  const isTooLong = charCount > MAX_CHARACTERS;
  const isNearLimit = charCount > MAX_CHARACTERS * WARN_THRESHOLD;

  function handleChange(event: ChangeEvent<HTMLTextAreaElement>) {
    onChange(event.target.value);
  }

  return (
    <div className="text-input">
      <div className="text-input__header">
        <label htmlFor="analyzer-text-input" className="text-input__label">
          Text to analyze
        </label>
        <button
          type="button"
          className="text-input__clear"
          onClick={() => onChange("")}
          disabled={disabled || value.length === 0}
        >
          Clear
        </button>
      </div>
      <textarea
        id="analyzer-text-input"
        className="text-input__area"
        placeholder="Type or paste text here to see how it gets tokenized..."
        value={value}
        onChange={handleChange}
        disabled={disabled}
        rows={8}
        aria-describedby="char-count-hint"
      />
      <div
        id="char-count-hint"
        className={
          "text-input__footer" +
          (isTooLong ? " text-input__footer--error" : isNearLimit ? " text-input__footer--warning" : "")
        }
      >
        <span>
          {charCount.toLocaleString()} / {MAX_CHARACTERS.toLocaleString()} characters
        </span>
        {isTooLong && <span>Text is too long. Please shorten it before analyzing.</span>}
      </div>
    </div>
  );
}

export { MAX_CHARACTERS };
