@AGENTS.md

# CLAUDE.md - Frontend Context & Standards

## Project Vision
A decoupled, enterprise-grade accounting interface built to control a Python automation sidecar. It prioritizes data density, auditing transparency, and backend-agnostic communication.

## 🏗️ Architecture Layers

### 1. Metadata Layer (`/metadata`)
Contains static constants and default configurations.
- **Rule**: No hardcoded system strings or system paths (like Chrome paths or TVA rates) in components.
- **Key Files**: `cdpDefaults.ts`, `importSettings.ts`, `rulesDefinitions.ts`.

### 2. Module Layer (`/modules`)
Contains the "Controllers" (React Hooks) that manage view-specific state.
- **Rule**: Components should be "dumb" (UI only). Logic, API calls, and state transitions live here.
- **Key Files**: `useImportModule.ts`, `useExecutionModule.ts`.

### 3. Service Layer (`/services`)
Contains the pure HTTP communication logic.
- **Rule**: No Tauri-specific code or component state logic. This layer only returns typed JSON responses.
- **Key File**: `endpoint.ts`.

## 🎨 Coding Standards
- **Exports**: Use **Named Exports** for all views and modules (e.g., `export function SettingsTab()`). Avoid default exports except for `app/page.tsx`.
- **Components**: Functional components only. Use Lucide React for all iconography.
- **Styling**: Tailwind CSS 4. Use design tokens from `globals.css` (`bg-surface`, `text-primary`).
- **Layout**: Use **Flexbox** for the main app container. Sidebar must be `shrink-0`, main content must be `flex-1`.
- **Naming**: 
  - Modules: `use[ViewName]Module.ts`
  - Views: `[TabName]Tab.tsx` (Matching Python naming: Settings, PWA, Import, Review, Execution).

## 🧮 Accounting & Data Logic
- **Precision**: Always format currency (TND) with exactly 3 decimal places using `.toFixed(3)`.
- **Typography**: Always use `font-mono` for references, accounts, and monetary amounts.
- **Validation Colors**:
  - **Debits**: Tailwind `text-error` (Red).
  - **Credits**: Tailwind `text-green-700` (Green).
  - **Specific Match**: Green-themed cards.
  - **Default Match**: Orange-themed cards.

## 🛠️ Common Commands
- `npm run dev`: Start Turbopack development server.
- `npm run build`: Production build and optimization.
- `npm run lint`: Static code analysis.
