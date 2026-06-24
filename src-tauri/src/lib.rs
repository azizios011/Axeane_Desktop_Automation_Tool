mod backend;
mod frontend;
mod tunnel;

use std::env;
use std::path::PathBuf;

use tauri::Manager;
use tunnel::TunnelManager;

/// Resolve the repository root at runtime.
///
/// Strategy (in order):
/// 1. Walk from the current working directory upward until we find a directory
///    that contains both a `router/` sub-directory and a `frontend/` sub-directory.
///    `cargo tauri dev` sets cwd to the workspace root, so this succeeds on the
///    first check.
/// 2. Walk upward from the executable path as a fallback for production bundles.
fn repo_root() -> PathBuf {
    fn contains_marker(path: &PathBuf) -> bool {
        path.join("router").is_dir() && path.join("frontend").is_dir()
    }

    // Try cwd first (works perfectly with `cargo tauri dev`).
    let cwd = env::current_dir().unwrap_or_else(|_| PathBuf::from("."));
    if contains_marker(&cwd) {
        log::info!("[lib] Repo root (cwd): {}", cwd.display());
        return cwd;
    }

    // Walk up from the executable.
    if let Ok(exe) = env::current_exe() {
        let mut candidate = exe;
        while let Some(parent) = candidate.parent().map(PathBuf::from) {
            if contains_marker(&parent) {
                log::info!("[lib] Repo root (exe walk): {}", parent.display());
                return parent;
            }
            if parent == candidate {
                break;
            }
            candidate = parent;
        }
    }

    log::warn!("[lib] Could not locate repo root — using cwd as fallback.");
    cwd
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .setup(|app| {
            // ── Logging plugin ──────────────────────────────────────────
            if cfg!(debug_assertions) {
                app.handle().plugin(
                    tauri_plugin_log::Builder::default()
                        .level(log::LevelFilter::Info)
                        .build(),
                )?;
            }

            // ── Process orchestration ────────────────────────────────────
            let root = repo_root();
            log::info!("[lib] Repo root resolved to: {}", root.display());

            let tunnel = TunnelManager::new(root);
            tunnel.start();

            // Store the tunnel in Tauri's managed state so the window-event
            // handler can access it for clean teardown.
            app.manage(tunnel);

            Ok(())
        })
        // ── Clean teardown on window close ───────────────────────────────
        .on_window_event(|window, event| {
            if let tauri::WindowEvent::Destroyed = event {
                log::info!("[lib] Window destroyed — stopping tunnel…");
                let tunnel = window.app_handle().state::<TunnelManager>();
                tunnel.stop();
            }
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
