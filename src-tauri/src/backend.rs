/// backend.rs — Python FastAPI server process manager.
///
/// Spawns the FastAPI server (`router/endpoint.py`) using the virtual
/// environment's Python interpreter when available, falling back to the
/// system `python` / `python3` binary.
///
/// Stdout and stderr are forwarded to the Tauri log sink with the
/// `[backend]` prefix so they appear alongside native Rust log output.
use std::path::PathBuf;
use std::process::{Child, Command, Stdio};
use std::sync::{Arc, Mutex};

use log::{error, info, warn};

/// Resolves the Python executable to use.
///
/// Preference order (Windows):
/// 1. `<repo_root>/router/venv/Scripts/python.exe`
/// 2. `python` (system PATH)
fn resolve_python(repo_root: &PathBuf) -> String {
    let venv_python = repo_root
        .join("router")
        .join("venv")
        .join("Scripts")
        .join("python.exe");

    if venv_python.exists() {
        info!("[backend] Using venv Python: {}", venv_python.display());
        venv_python.to_string_lossy().into_owned()
    } else {
        warn!("[backend] venv not found, falling back to system `python`");
        "python".to_string()
    }
}

/// Spawns the Python FastAPI process and returns the [`Child`] handle.
///
/// # Arguments
/// * `repo_root` – absolute path to the repository root directory.
pub fn spawn(repo_root: &PathBuf) -> std::io::Result<Child> {
    let python = resolve_python(repo_root);
    let script = repo_root.join("router").join("endpoint.py");

    info!(
        "[backend] Launching: {} {}",
        python,
        script.display()
    );

    let child = Command::new(&python)
        .arg(&script)
        // Run with the `router/` directory as cwd so relative imports work.
        .current_dir(repo_root.join("router"))
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()?;

    info!("[backend] Python FastAPI process spawned (PID {})", child.id());
    Ok(child)
}

/// Thread-safe handle for the backend child process.
#[derive(Clone)]
pub struct BackendManager {
    child: Arc<Mutex<Option<Child>>>,
    repo_root: PathBuf,
}

impl BackendManager {
    pub fn new(repo_root: PathBuf) -> Self {
        Self {
            child: Arc::new(Mutex::new(None)),
            repo_root,
        }
    }

    /// Start the backend. No-ops if already running.
    pub fn start(&self) {
        let mut guard = self.child.lock().expect("backend mutex poisoned");
        if guard.is_some() {
            info!("[backend] Already running — skipping start.");
            return;
        }
        match spawn(&self.repo_root) {
            Ok(c) => {
                *guard = Some(c);
                info!("[backend] Started.");
            }
            Err(e) => error!("[backend] Failed to start: {e}"),
        }
    }

    /// Kill the backend process if it is running.
    pub fn stop(&self) {
        let mut guard = self.child.lock().expect("backend mutex poisoned");
        if let Some(mut c) = guard.take() {
            match c.kill() {
                Ok(_) => info!("[backend] Process killed (was PID {}).", c.id()),
                Err(e) => warn!("[backend] Kill failed: {e}"),
            }
            let _ = c.wait();
        }
    }

    /// Returns `true` when the managed process is still alive.
    pub fn is_running(&self) -> bool {
        let mut guard = self.child.lock().expect("backend mutex poisoned");
        if let Some(ref mut c) = *guard {
            match c.try_wait() {
                Ok(None) => true,         // still running
                Ok(Some(status)) => {
                    warn!("[backend] Process exited unexpectedly: {status}");
                    *guard = None;
                    false
                }
                Err(e) => {
                    warn!("[backend] try_wait error: {e}");
                    false
                }
            }
        } else {
            false
        }
    }
}
