"use client";

interface Props {
  currentStep: number;

  totalSteps: number;
}

export function WorkflowProgress({
  currentStep,
  totalSteps,
}: Props) {
  const percent =
    totalSteps > 0
      ? Math.min(
          Math.round(
            (currentStep /
              totalSteps) *
              100
          ),
          100
        )
      : 0;

  return (
    <div>
      <div className="mb-2 flex justify-between text-sm">
        <span>
          Progress
        </span>

        <span>
          {percent}%
        </span>
      </div>

      <div className="h-2 rounded bg-secondary">
        <div
          className="h-2 rounded bg-primary"
          style={{
            width:
              `${percent}%`,
          }}
        />
      </div>
    </div>
  );
}