# Design

## Principles
- Answer first, evidence visible.
- Keep source context inspectable.
- Make model/provider state understandable.
- Artifacts are displayed beside the conversation.

## Interaction states
Loading, success, no evidence, model unavailable, database failure, and artifact rendering.

## Accessibility
Semantic headings, visible controls, responsive layout, keyboard-friendly form controls.

## Artifact security
Generated HTML is treated as untrusted and displayed in a sandboxed iframe without script permissions.
