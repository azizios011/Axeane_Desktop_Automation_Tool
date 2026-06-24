/// frontend.rs — Next.js development server process manager.
///
/// This module is only meaningful during debug / development runs.
/// In release builds Tauri loads the pre-built static export from the
/// `../dist` folder, so the dev server is never spawned.
///
/// The process is launched as `cmd /c npm run dev` inside the `frontend/`
/// workspace directory so that Next.js can pick up `next.config.ts` and
/// the locally installed `node_modules`.
use std::path::PathBuf;
use std::process::{Child, Command, Stdio};
use std::sync::{Arc, Mutex};

use log::{error, info, warn};

/// Spawns `npm run dev` in the `frontend/` directory.
///
/// # Arguments
/// * `repo_root` – absolute path to the repository root directory.
pub fn spawn(repo_root: &PathBuf) -> std::io::Result<Child> {
    let frontend_dir = repo_root.join("frontend");

    info!(
        "[frontend] Launching `npm run dev` in {}",
        frontend_dir.display()
    );

    // Use `cmd /c` so that `npm` (a batch script on Windows) is found via PATH.
    let child = Command::new("cmd")
        .args(["/c", "npm", "run", "dev"])
        .current_dir(&frontend_dir)
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()?;

    info!(
        "[frontend] Next.js dev server spawned (PID {}).",
        child.id()
    );
    Ok(child)
}

/// Thread-safe handle for the frontend child process.
#[derive(Clone)]
pub struct FrontendManager {
    child: Arc<Mutex<Option<Child>>>,
    repo_root: PathBuf,
}

impl FrontendManager {
    pub fn new(repo_root: PathBuf) -> Self {
        Self {
            child: Arc::new(Mutex::new(None)),
            repo_root,
        }
    }

    /// Start the Next.js dev server. No-ops if already running.
    pub fn start(&self) {
        let mut guard = self.child.lock().expect("frontend mutex poisoned");
        if guard.is_some() {
            info!("[frontend] Already running — skipping start.");
            return;
        }
        match spawn(&self.repo_root) {
            Ok(c) => {
                *guard = Some(c);
                info!("[frontend] Started.");
            }
            Err(e) => error!("[frontend] Failed to start: {e}"),
        }
    }

    /// Kill the Next.js dev server process if it is running.
    pub fn stop(&self) {
        let mut guard = self.child.lock().expect("frontend mutex poisoned");
        if let Some(mut c) = guard.take() {
            match c.kill() {
                Ok(_) => info!("[frontend] Process killed (was PID {}).", c.id()),
                Err(e) => warn!("[frontend] Kill failed: {e}"),
            }
            let _ = c.wait();
        }
    }

    /// Returns `true` when the managed process is still alive.
    pub fn is_running(&self) -> bool {
        let mut guard = self.child.lock().expect("frontend mutex poisoned");
        if let Some(ref mut c) = *guard {
            match c.try_wait() {
                Ok(None) => true,
                Ok(Some(status)) => {
                    warn!("[frontend] Process exited unexpectedly: {status}");
                    *guard = None;
                    false
                }
                Err(e) => {
                    warn!("[frontend] try_wait error: {e}");
                    false
                }
            }
        } else {
            false
        }
    }
}
