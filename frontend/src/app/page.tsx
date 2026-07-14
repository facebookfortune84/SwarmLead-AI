import { Card } from "@/components/ui/card";

export default function HomePage() {
  return (
    <main className="p-8">
      <Card className="p-6">
        <h1 className="text-3xl font-bold">
          SwarmLead-AI
        </h1>

        <p className="mt-3 text-muted-foreground">
          Frontend initialized successfully.
        </p>
      </Card>
    </main>
  );
}
