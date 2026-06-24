/// tunnel.rs — Process orchestrator and health watchdog.
///
/// [`TunnelManager`] owns both child-process managers ([`BackendManager`]
/// and [`FrontendManager`]) and drives a background watchdog thread that:
///
/// 1. Performs TCP connectivity probes on the two service ports.
/// 2. If a port goes down it tries to restart the responsible manager.
/// 3. Logs every state transition so operators can trace restarts.
///
/// # Port assignments
/// | Service   | Port |
/// |-----------|------|
/// | Python FastAPI backend | 8000 |
/// | Next.js dev server     | 3000 |
///
/// # Lifecycle
/// ```
/// let tunnel = TunnelManager::new(repo_root);
/// tunnel.start();          // spawns both processes + watchdog thread
/// // …Tauri runs…
/// tunnel.stop();           // kills both processes, joins watchdog
/// ```
use std::net::TcpStream;
use std::path::PathBuf;
use std::sync::{
    atomic::{AtomicBool, Ordering},
    Arc,
};
use std::thread;
use std::time::Duration;

use log::{info, warn};

use crate::backend::BackendManager;
use crate::frontend::FrontendManager;

/// How long to wait between watchdog probe cycles.
const WATCHDOG_INTERVAL: Duration = Duration::from_secs(5);

/// TCP connection timeout for port probes.
const PROBE_TIMEOUT: Duration = Duration::from_secs(2);

/// Backend FastAPI port.
const BACKEND_PORT: u16 = 8000;

/// Next.js dev server port.
const FRONTEND_PORT: u16 = 3000;

/// Returns `true` when a TCP connection to `localhost:<port>` succeeds
/// within [`PROBE_TIMEOUT`].
fn port_is_open(port: u16) -> bool {
    let addr = format!("127.0.0.1:{port}");
    TcpStream::connect_timeout(
        &addr.parse().expect("invalid socket address"),
        PROBE_TIMEOUT,
    )
    .is_ok()
}

/// The central orchestrator.
///
/// Clone-safe: the inner state is wrapped in [`Arc`] so the watchdog thread
/// can share ownership with the main Tauri thread.
#[derive(Clone)]
pub struct TunnelManager {
    backend: BackendManager,
    #[cfg(debug_assertions)]
    frontend: FrontendManager,
    running: Arc<AtomicBool>,
}

impl TunnelManager {
    /// Create a new [`TunnelManager`].
    ///
    /// Processes are **not** started until [`start`](Self::start) is called.
    pub fn new(repo_root: PathBuf) -> Self {
        Self {
            backend: BackendManager::new(repo_root.clone()),
            #[cfg(debug_assertions)]
            frontend: FrontendManager::new(repo_root),
            running: Arc::new(AtomicBool::new(false)),
        }
    }

    /// Start both subprocess managers and the background watchdog thread.
    ///
    /// Calling `start()` more than once is safe — the watchdog checks the
    /// `running` flag and returns immediately on subsequent calls.
    pub fn start(&self) {
        if self.running.swap(true, Ordering::SeqCst) {
            info!("[tunnel] Already running.");
            return;
        }

        info!("[tunnel] Starting managed processes…");

        // Always start the backend.
        self.backend.start();

        // The Next.js dev server is started by Tauri CLI via `beforeDevCommand`.
        // We do NOT spawn it here — the watchdog loop below will restart it
        // automatically if it ever crashes during the session.

        // Spawn the watchdog thread.
        let running = Arc::clone(&self.running);
        let backend = self.backend.clone();
        #[cfg(debug_assertions)]
        let frontend = self.frontend.clone();

        thread::spawn(move || {
            info!("[tunnel] Watchdog thread started.");
            let mut backend_grace_cycles = 6;
            #[cfg(debug_assertions)]
            let mut frontend_grace_cycles = 0;

            while running.load(Ordering::SeqCst) {
                thread::sleep(WATCHDOG_INTERVAL);

                // --- Backend health check ---
                if !backend.is_running() {
                    warn!("[tunnel] ⚠  Backend process not running — starting…");
                    backend.start();
                    backend_grace_cycles = 6;
                } else if !port_is_open(BACKEND_PORT) {
                    if backend_grace_cycles > 0 {
                        backend_grace_cycles -= 1;
                        info!(
                            "[tunnel] Backend starting up (port {BACKEND_PORT} closed, grace cycles left: {backend_grace_cycles})"
                        );
                    } else {
                        warn!(
                            "[tunnel] ⚠  Port {BACKEND_PORT} unreachable after grace period — \
                             attempting backend restart…"
                        );
                        backend.stop();
                        backend.start();
                        backend_grace_cycles = 6;
                    }
                } else {
                    backend_grace_cycles = 0; // Port is open, ensure grace is cleared
                }

                // --- Frontend health check (debug only) ---
                #[cfg(debug_assertions)]
                {
                    if !port_is_open(FRONTEND_PORT) {
                        if frontend_grace_cycles > 0 {
                            frontend_grace_cycles -= 1;
                            info!(
                                "[tunnel] Frontend starting up (port {FRONTEND_PORT} closed, grace cycles left: {frontend_grace_cycles})"
                            );
                        } else {
                            if frontend.is_running() {
                                warn!(
                                    "[tunnel] ⚠  Port {FRONTEND_PORT} unreachable but process is active — \
                                     attempting frontend restart…"
                                );
                                frontend.stop();
                                frontend.start();
                            } else {
                                warn!(
                                    "[tunnel] ⚠  Port {FRONTEND_PORT} unreachable and process not active — \
                                     starting frontend…"
                                );
                                frontend.start();
                            }
                            frontend_grace_cycles = 6;
                        }
                    } else {
                        frontend_grace_cycles = 0; // Port is open, ensure grace is cleared
                    }
                }
            }

            info!("[tunnel] Watchdog thread exiting.");
        });

        info!("[tunnel] Orchestration active.");
    }

    /// Stop the watchdog and gracefully kill all managed processes.
    ///
    /// This is called from Tauri's window-close / app-exit hook to ensure
    /// no orphan processes are left behind.
    pub fn stop(&self) {
        info!("[tunnel] Shutting down…");

        // Signal the watchdog to exit.
        self.running.store(false, Ordering::SeqCst);

        // Kill child processes.
        self.backend.stop();

        #[cfg(debug_assertions)]
        self.frontend.stop();

        info!("[tunnel] All processes stopped.");
    }
}
