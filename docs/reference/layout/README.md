# Follow-along layout references (2026-11-21)

Reference mockups for the 5BX follow-along video overlay. They are design references, not production art.

- `layout-v3-approved-top-corners.png`: the approved layout. One camera with no zoom, the lying boy scaled up 1.537548x against standing, a Fraser-style slanted name card plus one tip in the top left, and a minimal ring timer in the top right.
- `layout-v4-top-vs-bottom-corners.png`: the top-corner layout (top row) compared with a bottom-corner variant (bottom row). Charles chose the top corners on 2026-11-21. The bottom corners crowd the lying boy's head and put the timer over the floor.

The specification lives in `sprites/config/theme.json` (`stage`, `overlay`). The background contrast rule (subtly darker behind the top corners so the white timer reads) is in `sprites/prompts/backgrounds.spec.json` (`contrast`) and `sprites/config/scene.json`.
