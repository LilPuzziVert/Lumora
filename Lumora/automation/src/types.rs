use serde::{Deserialize, Serialize};
use chrono::{DateTime, Utc};
use uuid::Uuid;
use std::collections::HashMap;

/// Core automation action types
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum ActionType {
    Click { x: i32, y: i32, button: MouseButton },
    DoubleClick { x: i32, y: i32, button: MouseButton },
    RightClick { x: i32, y: i32 },
    Drag { from_x: i32, from_y: i32, to_x: i32, to_y: i32 },
    Scroll { x: i32, y: i32, direction: ScrollDirection, amount: i32 },
    Type { text: String },
    KeyPress { key: VirtualKey, modifiers: Vec<VirtualKey> },
    KeySequence { keys: Vec<KeyCombination> },
    Wait { duration_ms: u64 },
    WindowAction { action: WindowActionType, target: WindowTarget },
    AppSpecific { app_name: String, action: String, parameters: HashMap<String, String> },
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum MouseButton {
    Left,
    Right,
    Middle,
    X1,
    X2,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum ScrollDirection {
    Up,
    Down,
    Left,
    Right,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum VirtualKey {
    // Letters
    A, B, C, D, E, F, G, H, I, J, K, L, M, N, O, P, Q, R, S, T, U, V, W, X, Y, Z,
    // Numbers
    Num0, Num1, Num2, Num3, Num4, Num5, Num6, Num7, Num8, Num9,
    // Function keys
    F1, F2, F3, F4, F5, F6, F7, F8, F9, F10, F11, F12,
    // Modifiers
    Ctrl, Alt, Shift, Win,
    // Special keys
    Enter, Escape, Space, Tab, Backspace, Delete,
    Home, End, PageUp, PageDown,
    Left, Right, Up, Down,
    // Custom key code
    Custom(u32),
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct KeyCombination {
    pub key: VirtualKey,
    pub modifiers: Vec<VirtualKey>,
    pub hold_duration_ms: Option<u64>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum WindowActionType {
    Minimize,
    Maximize,
    Restore,
    Close,
    Focus,
    Move { x: i32, y: i32 },
    Resize { width: i32, height: i32 },
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum WindowTarget {
    Active,
    ByTitle(String),
    ByClass(String),
    ByProcess(String),
    ByHandle(u64),
}

/// Complete automation action with metadata
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AutomationAction {
    pub id: Uuid,
    pub action_type: ActionType,
    pub timestamp: DateTime<Utc>,
    pub priority: ActionPriority,
    pub retry_count: u32,
    pub timeout_ms: u64,
    pub description: Option<String>,
    pub pre_conditions: Vec<Condition>,
    pub post_conditions: Vec<Condition>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum ActionPriority {
    Low,
    Normal,
    High,
    Critical,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Condition {
    pub condition_type: ConditionType,
    pub expected_value: String,
    pub timeout_ms: u64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum ConditionType {
    WindowExists(String),
    WindowActive(String),
    TextExists(String),
    ElementExists(String),
    ProcessRunning(String),
    Custom(String),
}

/// Action execution result
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ActionResult {
    pub success: bool,
    pub error: Option<String>,
    pub execution_time_ms: u64,
    pub rollback_data: Option<RollbackData>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RollbackData {
    pub action_type: String,
    pub data: HashMap<String, String>,
    pub timestamp: DateTime<Utc>,
}

/// Input monitoring types
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum InputEvent {
    KeyPress { key: VirtualKey, timestamp: DateTime<Utc> },
    KeyRelease { key: VirtualKey, timestamp: DateTime<Utc> },
    MouseMove { x: i32, y: i32, timestamp: DateTime<Utc> },
    MouseClick { x: i32, y: i32, button: MouseButton, timestamp: DateTime<Utc> },
    MouseWheel { x: i32, y: i32, delta: i32, timestamp: DateTime<Utc> },
    WindowChange { from_window: String, to_window: String, timestamp: DateTime<Utc> },
    IdleStart { timestamp: DateTime<Utc> },
    IdleEnd { duration_ms: u64, timestamp: DateTime<Utc> },
}

/// System state structures
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SystemState {
    pub input_state: InputState,
    pub app_state: AppState,
    pub safety_state: SafetyState,
    pub timestamp: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct InputState {
    pub active_keys: Vec<VirtualKey>,
    pub mouse_position: (i32, i32),
    pub idle_time_ms: u64,
    pub last_input: DateTime<Utc>,
    pub typing_speed_wpm: f32,
    pub mouse_movement_pattern: MovementPattern,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum MovementPattern {
    Steady,
    Erratic,
    Precise,
    Gaming,
    Idle,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AppState {
    pub active_window: WindowInfo,
    pub running_processes: Vec<ProcessInfo>,
    pub recent_windows: Vec<WindowInfo>,
    pub system_load: SystemLoad,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct WindowInfo {
    pub title: String,
    pub class_name: String,
    pub process_name: String,
    pub handle: u64,
    pub rectangle: Rectangle,
    pub is_visible: bool,
    pub is_foreground: bool,
    pub z_order: i32,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Rectangle {
    pub x: i32,
    pub y: i32,
    pub width: i32,
    pub height: i32,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ProcessInfo {
    pub name: String,
    pub pid: u32,
    pub cpu_usage: f32,
    pub memory_usage: u64,
    pub start_time: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SystemLoad {
    pub cpu_percent: f32,
    pub memory_percent: f32,
    pub disk_io_read: u64,
    pub disk_io_write: u64,
    pub network_io_read: u64,
    pub network_io_write: u64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SafetyState {
    pub is_safe_mode: bool,
    pub blocked_applications: Vec<String>,
    pub rate_limit_status: HashMap<String, RateLimitInfo>,
    pub last_safety_check: DateTime<Utc>,
    pub total_actions_today: u32,
    pub failed_actions_today: u32,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RateLimitInfo {
    pub current_count: u32,
    pub limit: u32,
    pub reset_time: DateTime<Utc>,
}

/// Safety validation results
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SafetyResult {
    pub is_safe: bool,
    pub reason: String,
    pub risk_level: RiskLevel,
    pub mitigation_suggestions: Vec<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum RiskLevel {
    None,
    Low,
    Medium,
    High,
    Critical,
}

/// Configuration structures
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AutomationConfig {
    pub input_monitoring: InputMonitorConfig,
    pub app_control: AppControlConfig,
    pub safety: SafetyConfig,
    pub performance: PerformanceConfig,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct InputMonitorConfig {
    pub enabled: bool,
    pub hook_keyboard: bool,
    pub hook_mouse: bool,
    pub idle_threshold_ms: u64,
    pub sample_rate_hz: u32,
    pub buffer_size: usize,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AppControlConfig {
    pub enabled: bool,
    pub max_retry_count: u32,
    pub default_timeout_ms: u64,
    pub action_delay_ms: u64,
    pub blocked_apps: Vec<String>,
    pub allowed_apps: Vec<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SafetyConfig {
    pub enabled: bool,
    pub max_actions_per_minute: u32,
    pub max_actions_per_hour: u32,
    pub max_actions_per_day: u32,
    pub require_confirmation: bool,
    pub blocked_actions: Vec<ActionType>,
    pub safe_mode_triggers: Vec<SafeModeTrigger>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum SafeModeTrigger {
    HighCpuUsage(f32),
    HighMemoryUsage(f32),
    TooManyFailures(u32),
    UnknownApplication,
    SystemLocked,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PerformanceConfig {
    pub max_cpu_usage: f32,
    pub max_memory_usage: u64,
    pub thread_pool_size: usize,
    pub batch_size: usize,
    pub optimization_level: OptimizationLevel,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum OptimizationLevel {
    Minimal,
    Balanced,
    Performance,
    MaxPerformance,
}

impl Default for AutomationAction {
    fn default() -> Self {
        Self {
            id: Uuid::new_v4(),
            action_type: ActionType::Wait { duration_ms: 100 },
            timestamp: Utc::now(),
            priority: ActionPriority::Normal,
            retry_count: 0,
            timeout_ms: 5000,
            description: None,
            pre_conditions: Vec::new(),
            post_conditions: Vec::new(),
        }
    }
}