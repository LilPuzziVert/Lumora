use std::sync::Arc;
use tokio::sync::RwLock;
use windows::Win32::Foundation::*;
use serde::{Deserialize, Serialize};

pub mod input_monitor;
pub mod app_controller;
pub mod safety_engine;
pub mod types;

use crate::types::*;

/// Main automation engine that coordinates all automation subsystems
pub struct AutomationEngine {
    input_monitor: Arc<RwLock<input_monitor::InputMonitor>>,
    app_controller: Arc<RwLock<app_controller::AppController>>,
    safety_engine: Arc<RwLock<safety_engine::SafetyEngine>>,
    is_running: Arc<RwLock<bool>>,
}

impl AutomationEngine {
    /// Create a new automation engine instance
    pub async fn new() -> anyhow::Result<Self> {
        let input_monitor = Arc::new(RwLock::new(input_monitor::InputMonitor::new().await?));
        let app_controller = Arc::new(RwLock::new(app_controller::AppController::new().await?));
        let safety_engine = Arc::new(RwLock::new(safety_engine::SafetyEngine::new().await?));
        
        Ok(Self {
            input_monitor,
            app_controller,
            safety_engine,
            is_running: Arc::new(RwLock::new(false)),
        })
    }

    /// Start the automation engine
    pub async fn start(&self) -> anyhow::Result<()> {
        let mut is_running = self.is_running.write().await;
        if *is_running {
            return Ok(());
        }

        // Start all subsystems
        self.input_monitor.write().await.start().await?;
        self.app_controller.write().await.start().await?;
        self.safety_engine.write().await.start().await?;

        *is_running = true;
        log::info!("Lumora Automation Engine started successfully");
        Ok(())
    }

    /// Stop the automation engine
    pub async fn stop(&self) -> anyhow::Result<()> {
        let mut is_running = self.is_running.write().await;
        if !*is_running {
            return Ok(());
        }

        // Stop all subsystems gracefully
        self.input_monitor.write().await.stop().await?;
        self.app_controller.write().await.stop().await?;
        self.safety_engine.write().await.stop().await?;

        *is_running = false;
        log::info!("Lumora Automation Engine stopped successfully");
        Ok(())
    }

    /// Execute an automation action with safety checks
    pub async fn execute_action(&self, action: AutomationAction) -> anyhow::Result<ActionResult> {
        // First, run safety checks
        let safety_result = self.safety_engine.read().await.validate_action(&action).await?;
        if !safety_result.is_safe {
            return Ok(ActionResult {
                success: false,
                error: Some(format!("Safety check failed: {}", safety_result.reason)),
                execution_time_ms: 0,
                rollback_data: None,
            });
        }

        // Execute the action through the app controller
        let start_time = std::time::Instant::now();
        let result = self.app_controller.write().await.execute_action(action).await?;
        let execution_time = start_time.elapsed().as_millis() as u64;

        Ok(ActionResult {
            success: result.success,
            error: result.error,
            execution_time_ms: execution_time,
            rollback_data: result.rollback_data,
        })
    }

    /// Get current system state for monitoring
    pub async fn get_system_state(&self) -> anyhow::Result<SystemState> {
        let input_state = self.input_monitor.read().await.get_current_state().await?;
        let app_state = self.app_controller.read().await.get_current_state().await?;
        let safety_state = self.safety_engine.read().await.get_current_state().await?;

        Ok(SystemState {
            input_state,
            app_state,
            safety_state,
            timestamp: chrono::Utc::now(),
        })
    }

    /// Register for input events
    pub async fn register_input_callback<F>(&self, callback: F) -> anyhow::Result<()>
    where
        F: Fn(InputEvent) + Send + Sync + 'static,
    {
        self.input_monitor.write().await.register_callback(Box::new(callback)).await
    }

    /// Check if engine is running
    pub async fn is_running(&self) -> bool {
        *self.is_running.read().await
    }
}

/// C-compatible FFI functions for Python integration
#[no_mangle]
pub extern "C" fn lumora_automation_create() -> *mut AutomationEngine {
    match tokio::runtime::Runtime::new() {
        Ok(rt) => {
            match rt.block_on(AutomationEngine::new()) {
                Ok(engine) => Box::into_raw(Box::new(engine)),
                Err(e) => {
                    log::error!("Failed to create automation engine: {}", e);
                    std::ptr::null_mut()
                }
            }
        }
        Err(e) => {
            log::error!("Failed to create tokio runtime: {}", e);
            std::ptr::null_mut()
        }
    }
}

#[no_mangle]
pub extern "C" fn lumora_automation_destroy(engine: *mut AutomationEngine) {
    if !engine.is_null() {
        unsafe {
            let _ = Box::from_raw(engine);
        }
    }
}

#[no_mangle]
pub extern "C" fn lumora_automation_start(engine: *mut AutomationEngine) -> bool {
    if engine.is_null() {
        return false;
    }

    let engine = unsafe { &*engine };
    match tokio::runtime::Runtime::new() {
        Ok(rt) => {
            match rt.block_on(engine.start()) {
                Ok(_) => true,
                Err(e) => {
                    log::error!("Failed to start automation engine: {}", e);
                    false
                }
            }
        }
        Err(e) => {
            log::error!("Failed to create tokio runtime: {}", e);
            false
        }
    }
}

/// Initialize logging for the automation engine
pub fn init_logging() {
    env_logger::Builder::from_default_env()
        .filter_level(log::LevelFilter::Info)
        .init();
}