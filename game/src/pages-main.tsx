import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { WorkoutApp } from "@/components/workout-app";
import "@/styles.css";

const root = document.getElementById("root");
if (root) {
  createRoot(root).render(
    <StrictMode>
      <WorkoutApp />
    </StrictMode>,
  );
}
