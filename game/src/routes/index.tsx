import { createFileRoute } from "@tanstack/react-router";
import { WorkoutApp } from "@/components/workout-app";

export const Route = createFileRoute("/")({ component: Home });

function Home() {
  return <WorkoutApp />;
}
