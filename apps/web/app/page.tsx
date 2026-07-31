import { Button } from "@/components/ui/button";

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-4">
      <h1 className="text-2xl font-semibold">obligo</h1>
      <p className="text-muted-foreground">Phase 1 walking skeleton — web is up.</p>
      <Button>shadcn/ui is wired in</Button>
    </main>
  );
}
