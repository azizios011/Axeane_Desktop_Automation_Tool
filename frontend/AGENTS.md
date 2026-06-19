# AGENTS.md - Technical Guide for Frontend Development

## 🤖 System Overview for Agents
The Axeane Flow frontend is a "Controlled Interface." It manages the user's intent and displays data, but delegates all heavy lifting (Parsing, Accounting Math, and Playwright Automation) to a Python Sidecar. 

**The Golden Rule:** Maintain "Logic Symmetry" with the Python codebase. If the Python logic changes in `Rules.py`, the Frontend `ReviewTab` must be updated to visualize that change.

---

## 🛠️ Modular Pattern Reference

### 1. Adding a New Data Field
- **Where**: Add the constant to `metadata/`.
- **Logic**: Update the interface in `types/axeane.ts`.
- **UI**: Add the input to the corresponding `Tab.tsx`.

### 2. Adding a New API Call
- **Where**: Add the route to `metadata/apiConfig.ts`.
- **Logic**: Add the fetch function to `services/endpoint.ts`.
- **Consumer**: Call it within the appropriate module in `modules/`.

---

## 🔄 Core Data Workflows

### 📥 The Import Flow
1. **Selection**: `ImportTab` triggers `handleBrowse`.
2. **Transfer**: `useImportModule` calls `AxeaneAPI.uploadFile`.
3. **Session**: The Python backend returns a `session_id`. **This ID must be stored** to authorize all subsequent calls (Parse, Review, Execute).
4. **Preview**: The `rawData` state is populated. The table must render dynamically based on the headers returned by the backend.

### 🔧 The Review (Formula) Flow
- **Trigger**: Once parsing is complete, `ReviewTab` calls `getFormulas(sessionId)`.
- **Visual Branching**: 
  - `card.match_type === 'specific'` -> Render with **Green Theme** (Green-700/Green-50).
  - `card.match_type === 'default'` -> Render with **Orange Theme** (Orange-600/Orange-50).
- **Balancing**: The UI should visually distinguish Debits (Red) and Credits (Green).

### 🏁 The Execution Flow
- **Execution**: `startAutomation` sends the browser config and session ID to the backend.
- **Polling**: `useExecutionModule` initiates a `setInterval` (800ms) to poll `/api/status`.
- **Log Streaming**: New logs from the API response are appended to the `logs` array. 
- **Auto-Scroll**: The `terminalRef` must use `scrollTop = scrollHeight` on every state update to ensure the latest log is visible.

---

## 🎨 Design Tokens (Tailwind 4)
We use a high-density Material 3 layout:
- **Spacing**: Use `p-6` for main containers, `p-2` or `p-3` for dense table rows.
- **Typography**: 
  - `text-[10px] font-black uppercase`: Used for labels and category tags.
  - `font-mono`: Required for all monetary amounts, references, and account numbers.
- **Shadows**: Use `shadow-lg shadow-primary/20` for primary action buttons to give them depth.

---

## 📡 The Agnostic API Contract
The frontend communicates via `fetch` to `localhost:8000`. 
- **Decoupling**: The frontend does not know about Python threads. It assumes the backend is asynchronous and uses the `/status` endpoint to track long-running jobs.
- **Error Handling**: Every API call should return a typed `APIResponse`. Errors must be displayed in the UI using the `status.color` logic in modules.

## ⚠️ Critical Implementation Notes
- **Sidebar Layout**: The sidebar is `shrink-0`. The main content area is `flex-1`. Do not use `absolute` or `fixed` positioning for the main content area, or it will overlap the sidebar.
- **Component Lifecycle**: Ensure all `setInterval` instances in the Execution module are cleared on unmount to prevent memory leaks during tab switching.
