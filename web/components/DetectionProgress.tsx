"use client";

interface Props {
  stage: string;
  message: string;
}

const STAGES = [
  { id: "queued", label: "Request received" },
  { id: "downloading_model", label: "Preparing model" },
  { id: "loading_model", label: "Loading model" },
  { id: "predicting", label: "Analyzing image" },
];

export default function DetectionProgress({ stage, message }: Props) {
  const currentIndex = STAGES.findIndex((item) => item.id === stage);

  return (
    <div
      className="rounded-xl border border-accent/30 bg-surface-light p-4"
      role="status"
      aria-live="polite"
    >
      <div className="flex items-center gap-3">
        <span className="h-4 w-4 animate-spin rounded-full border-2 border-gray-600 border-t-accent" />
        <p className="text-sm font-medium text-white">{message}</p>
      </div>
      <ol className="mt-4 grid grid-cols-2 gap-2 text-xs sm:grid-cols-4">
        {STAGES.map((item, index) => {
          const isCurrent = item.id === stage;
          const isComplete = currentIndex > index || stage === "completed";
          return (
            <li
              key={item.id}
              className={isCurrent || isComplete ? "text-accent" : "text-gray-500"}
              aria-current={isCurrent ? "step" : undefined}
            >
              <span className="mr-1">{isComplete ? "✓" : isCurrent ? "●" : "○"}</span>
              {item.label}
            </li>
          );
        })}
      </ol>
    </div>
  );
}
