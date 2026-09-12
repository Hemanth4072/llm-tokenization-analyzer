import type { ModelId, ModelSummary } from "../types/tokenizer";

interface ModelSelectorProps {
  models: ModelSummary[];
  selected: ModelId[];
  onChange: (selected: ModelId[]) => void;
  disabled?: boolean;
}

export function ModelSelector({ models, selected, onChange, disabled }: ModelSelectorProps) {
  function toggle(modelId: ModelId) {
    if (selected.includes(modelId)) {
      onChange(selected.filter((id) => id !== modelId));
    } else {
      onChange([...selected, modelId]);
    }
  }

  function selectBoth() {
    onChange(models.map((m) => m.id));
  }

  const bothSelected = models.length > 0 && selected.length === models.length;

  return (
    <fieldset className="model-selector" disabled={disabled}>
      <legend className="model-selector__legend">Tokenizers</legend>
      <div className="model-selector__options">
        {models.map((model) => (
          <label key={model.id} className="model-selector__option">
            <input
              type="checkbox"
              checked={selected.includes(model.id)}
              onChange={() => toggle(model.id)}
            />
            <span>{model.name}</span>
          </label>
        ))}
        <button
          type="button"
          className={"model-selector__compare-btn" + (bothSelected ? " model-selector__compare-btn--active" : "")}
          onClick={selectBoth}
        >
          Compare Both
        </button>
      </div>
    </fieldset>
  );
}
