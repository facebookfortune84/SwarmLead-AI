"use client";

const templates = [
  {
    name:
      "Cold Outreach",

    description:
      "Initial prospecting sequence.",
  },

  {
    name:
      "Follow-Up",

    description:
      "Re-engagement sequence.",
  },

  {
    name:
      "Product Demo",

    description:
      "Demo scheduling campaign.",
  },

  {
    name:
      "Customer Reactivation",

    description:
      "Previous client outreach.",
  },
];

export function CampaignTemplateGrid() {
  return (
    <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
      {templates.map(
        (
          template
        ) => (
          <div
            key={
              template.name
            }
            className="rounded-lg border p-4"
          >
            <div className="font-medium">
              {
                template.name
              }
            </div>

            <div className="mt-2 text-sm text-muted-foreground">
              {
                template.description
              }
            </div>
          </div>
        )
      )}
    </div>
  );
}