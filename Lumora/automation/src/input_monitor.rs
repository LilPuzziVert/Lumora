use std::sync::Arc;
use std::collections::{HashMap, VecDeque};
use tokio::sync::{RwLock, mpsc};
use windows::Win32::Foundation::*;
use windows::Win32::UI::WindowsAndMessaging::*;
use windows::Win32::UI::Input::KeyboardAndMouse::*;
use chrono::{DateTime, Utc};
use parking_lot::Mutex;

use crate::types::*;

/// High-performance input monitoring system
pub struct InputMonitor {
    config: InputMonitorConfig,
    is_running: Arc<RwLock<bool>>,
    input_buffer: Arc<Mutex<VecDeque<InputEvent>>>,
    callbacks: Arc<RwLock<Vec<Box<dyn Fn(InputEvent) + Send + Sync>>>>,
    keyboard_hook: Option<HHOOK>,
    mouse_hook: Option<HHOOK>,
    stats: Arc<RwLock<InputStats>>,
    current_state: Arc<RwLock<InputState>>,
}

#[derive(Debug, Clone)]
struct InputStats {
    total_keystrokes: u64,
    total_mouse_moves: u64,
    total_clicks: u64,
    session_start: DateTime<Utc>,
    last_activity: DateTime<Utc>,
    typing_speeds: VecDeque<f32>,
}

impl InputMonitor {
    /// Create a new input monitor
    pub async fn new() -> anyhow::Result<Self> {
        let config = InputMonitorConfig {
            enabled: true,
            hook_keyboard: true,
            hook_mouse: true,
            idle_threshold_ms: 30000, // 30 seconds
            sample_rate_hz: 60,
            buffer_size: 10000,
        };

        let stats = InputStats {
            total_keystrokes: 0,
            total_mouse_moves: 0,
            total_clicks: 0,
            session_start: Utc::now(),
            last_activity: Utc::now(),
            typing_speeds: VecDeque::with_capacity(100),
        };

        let current_state = InputState {
            active_keys: Vec::new(),
            mouse_position: (0, 0),
            idle_time_ms: 0,
            last_input: Utc::now(),
            typing_speed_wpm: 0.0,
            mouse_movement_pattern: MovementPattern::Idle,
        };

        Ok(Self {
            config,
            is_running: Arc::new(RwLock::new(false)),
            input_buffer: Arc::new(Mutex::new(VecDeque::with_capacity(config.buffer_size))),
            callbacks: Arc::new(RwLock::new(Vec::new())),
            keyboard_hook: None,
            mouse_hook: None,
            stats: Arc::new(RwLock::new(stats)),
            current_state: Arc::new(RwLock::new(current_state)),
        })
    }

    /// Start input monitoring
    pub async fn start(&mut self) -> anyhow::Result<()> {
        let mut is_running = self.is_running.write().await;
        if *is_running {
            return Ok(());
        }

        if self.config.hook_keyboard {
            self.install_keyboard_hook().await?;
        }

        if self.config.hook_mouse {
            self.install_mouse_hook().await?;
        }

        // Start background processing tasks
        self.start_background_tasks().await;

        *is_running = true;
        log::info!("Input monitor started successfully");
        Ok(())
    }

    /// Stop input monitoring
    pub async fn stop(&mut self) -> anyhow::Result<()> {
        let mut is_running = self.is_running.write().await;
        if !*is_running {
            return Ok(());
        }

        // Unhook keyboard and mouse
        unsafe {
            if let Some(hook) = self.keyboard_hook.take() {
                UnhookWindowsHookExW(hook)?;
            }
            if let Some(hook) = self.mouse_hook.take() {
                UnhookWindowsHookExW(hook)?;
            }
        }

        *is_running = false;
        log::info!("Input monitor stopped successfully");
        Ok(())
    }

    /// Install low-level keyboard hook
    async fn install_keyboard_hook(&mut self) -> anyhow::Result<()> {
        let buffer = Arc::clone(&self.input_buffer);
        let callbacks = Arc::clone(&self.callbacks);
        let stats = Arc::clone(&self.stats);
        let state = Arc::clone(&self.current_state);

        unsafe {
            let hook = SetWindowsHookExW(
                WH_KEYBOARD_LL,
                Some(Self::keyboard_proc),
                GetModuleHandleW(PCWSTR::null())?,
                0,
            )?;

            self.keyboard_hook = Some(hook);
        }

        Ok(())
    }

    /// Install low-level mouse hook
    async fn install_mouse_hook(&mut self) -> anyhow::Result<()> {
        let buffer = Arc::clone(&self.input_buffer);
        let callbacks = Arc::clone(&self.callbacks);
        let stats = Arc::clone(&self.stats);
        let state = Arc::clone(&self.current_state);

        unsafe {
            let hook = SetWindowsHookExW(
                WH_MOUSE_LL,
                Some(Self::mouse_proc),
                GetModuleHandleW(PCWSTR::null())?,
                0,
            )?;

            self.mouse_hook = Some(hook);
        }

        Ok(())
    }

    /// Low-level keyboard hook procedure
    unsafe extern "system" fn keyboard_proc(
        n_code: i32,
        w_param: WPARAM,
        l_param: LPARAM,
    ) -> LRESULT {
        if n_code >= 0 {
            let kb_struct = *(l_param.0 as *const KBDLLHOOKSTRUCT);
            let key = Self::vk_to_virtual_key(kb_struct.vkCode);
            let timestamp = Utc::now();

            let event = match w_param.0 as u32 {
                WM_KEYDOWN | WM_SYSKEYDOWN => InputEvent::KeyPress { key, timestamp },
                WM_KEYUP | WM_SYSKEYUP => InputEvent::KeyRelease { key, timestamp },
                _ => return CallNextHookEx(HHOOK::default(), n_code, w_param, l_param),
            };

            // Process the event (this would need to be handled via a global callback system)
            // For now, we'll just log it
            log::debug!("Keyboard event: {:?}", event);
        }

        CallNextHookEx(HHOOK::default(), n_code, w_param, l_param)
    }

    /// Low-level mouse hook procedure
    unsafe extern "system" fn mouse_proc(
        n_code: i32,
        w_param: WPARAM,
        l_param: LPARAM,
    ) -> LRESULT {
        if n_code >= 0 {
            let mouse_struct = *(l_param.0 as *const MSLLHOOKSTRUCT);
            let x = mouse_struct.pt.x;
            let y = mouse_struct.pt.y;
            let timestamp = Utc::now();

            let event = match w_param.0 as u32 {
                WM_MOUSEMOVE => InputEvent::MouseMove { x, y, timestamp },
                WM_LBUTTONDOWN => InputEvent::MouseClick {
                    x,
                    y,
                    button: MouseButton::Left,
                    timestamp,
                },
                WM_RBUTTONDOWN => InputEvent::MouseClick {
                    x,
                    y,
                    button: MouseButton::Right,
                    timestamp,
                },
                WM_MBUTTONDOWN => InputEvent::MouseClick {
                    x,
                    y,
                    button: MouseButton::Middle,
                    timestamp,
                },
                WM_MOUSEWHEEL => {
                    let wheel_data = mouse_struct.mouseData;
                    let delta = ((wheel_data as i32) >> 16) / 120; // Convert to scroll units
                    InputEvent::MouseWheel { x, y, delta, timestamp }
                }
                _ => return CallNextHookEx(HHOOK::default(), n_code, w_param, l_param),
            };

            log::debug!("Mouse event: {:?}", event);
        }

        CallNextHookEx(HHOOK::default(), n_code, w_param, l_param)
    }

    /// Convert Windows virtual key code to our VirtualKey enum
    fn vk_to_virtual_key(vk_code: u32) -> VirtualKey {
        match vk_code {
            0x41..=0x5A => {
                // A-Z keys
                let offset = vk_code - 0x41;
                match offset {
                    0 => VirtualKey::A, 1 => VirtualKey::B, 2 => VirtualKey::C, 3 => VirtualKey::D,
                    4 => VirtualKey::E, 5 => VirtualKey::F, 6 => VirtualKey::G, 7 => VirtualKey::H,
                    8 => VirtualKey::I, 9 => VirtualKey::J, 10 => VirtualKey::K, 11 => VirtualKey::L,
                    12 => VirtualKey::M, 13 => VirtualKey::N, 14 => VirtualKey::O, 15 => VirtualKey::P,
                    16 => VirtualKey::Q, 17 => VirtualKey::R, 18 => VirtualKey::S, 19 => VirtualKey::T,
                    20 => VirtualKey::U, 21 => VirtualKey::V, 22 => VirtualKey::W, 23 => VirtualKey::X,
                    24 => VirtualKey::Y, 25 => VirtualKey::Z,
                    _ => VirtualKey::Custom(vk_code),
                }
            }
            0x30..=0x39 => {
                // 0-9 keys
                let offset = vk_code - 0x30;
                match offset {
                    0 => VirtualKey::Num0, 1 => VirtualKey::Num1, 2 => VirtualKey::Num2,
                    3 => VirtualKey::Num3, 4 => VirtualKey::Num4, 5 => VirtualKey::Num5,
                    6 => VirtualKey::Num6, 7 => VirtualKey::Num7, 8 => VirtualKey::Num8,
                    9 => VirtualKey::Num9,
                    _ => VirtualKey::Custom(vk_code),
                }
            }
            0x70..=0x7B => {
                // F1-F12 keys
                let offset = vk_code - 0x70;
                match offset {
                    0 => VirtualKey::F1, 1 => VirtualKey::F2, 2 => VirtualKey::F3, 3 => VirtualKey::F4,
                    4 => VirtualKey::F5, 5 => VirtualKey::F6, 6 => VirtualKey::F7, 7 => VirtualKey::F8,
                    8 => VirtualKey::F9, 9 => VirtualKey::F10, 10 => VirtualKey::F11, 11 => VirtualKey::F12,
                    _ => VirtualKey::Custom(vk_code),
                }
            }
            0x11 => VirtualKey::Ctrl,
            0x12 => VirtualKey::Alt,
            0x10 => VirtualKey::Shift,
            0x5B | 0x5C => VirtualKey::Win,
            0x0D => VirtualKey::Enter,
            0x1B => VirtualKey::Escape,
            0x20 => VirtualKey::Space,
            0x09 => VirtualKey::Tab,
            0x08 => VirtualKey::Backspace,
            0x2E => VirtualKey::Delete,
            0x24 => VirtualKey::Home,
            0x23 => VirtualKey::End,
            0x21 => VirtualKey::PageUp,
            0x22 => VirtualKey::PageDown,
            0x25 => VirtualKey::Left,
            0x27 => VirtualKey::Right,
            0x26 => VirtualKey::Up,
            0x28 => VirtualKey::Down,
            _ => VirtualKey::Custom(vk_code),
        }
    }

    /// Start background processing tasks
    async fn start_background_tasks(&self) {
        let buffer = Arc::clone(&self.input_buffer);
        let callbacks = Arc::clone(&self.callbacks);
        let stats = Arc::clone(&self.stats);
        let state = Arc::clone(&self.current_state);
        let is_running = Arc::clone(&self.is_running);

        // Task for processing input buffer
        tokio::spawn(async move {
            let mut interval = tokio::time::interval(tokio::time::Duration::from_millis(16)); // ~60fps

            while *is_running.read().await {
                interval.tick().await;
                
                // Process buffered events
                let events: Vec<InputEvent> = {
                    let mut buffer = buffer.lock();
                    buffer.drain(..).collect()
                };

                for event in events {
                    // Update statistics
                    Self::update_stats(&stats, &event).await;
                    
                    // Update current state
                    Self::update_current_state(&state, &event).await;
                    
                    // Notify callbacks
                    let callbacks = callbacks.read().await;
                    for callback in callbacks.iter() {
                        callback(event.clone());
                    }
                }
            }
        });

        // Task for idle detection
        let state_clone = Arc::clone(&state);
        let is_running_clone = Arc::clone(&is_running);
        tokio::spawn(async move {
            let mut interval = tokio::time::interval(tokio::time::Duration::from_secs(1));

            while *is_running_clone.read().await {
                interval.tick().await;
                
                let mut state = state_clone.write().await;
                let now = Utc::now();
                let idle_duration = now.signed_duration_since(state.last_input);
                state.idle_time_ms = idle_duration.num_milliseconds() as u64;
                
                // Update movement pattern based on recent activity
                if state.idle_time_ms > 30000 {
                    state.mouse_movement_pattern = MovementPattern::Idle;
                }
            }
        });
    }

    /// Update input statistics
    async fn update_stats(stats: &Arc<RwLock<InputStats>>, event: &InputEvent) {
        let mut stats = stats.write().await;
        stats.last_activity = Utc::now();

        match event {
            InputEvent::KeyPress { .. } | InputEvent::KeyRelease { .. } => {
                stats.total_keystrokes += 1;
            }
            InputEvent::MouseMove { .. } => {
                stats.total_mouse_moves += 1;
            }
            InputEvent::MouseClick { .. } => {
                stats.total_clicks += 1;
            }
            _ => {}
        }
    }

    /// Update current input state
    async fn update_current_state(state: &Arc<RwLock<InputState>>, event: &InputEvent) {
        let mut state = state.write().await;

        match event {
            InputEvent::KeyPress { key, timestamp } => {
                if !state.active_keys.contains(key) {
                    state.active_keys.push(key.clone());
                }
                state.last_input = *timestamp;
            }
            InputEvent::KeyRelease { key, .. } => {
                state.active_keys.retain(|k| k != key);
            }
            InputEvent::MouseMove { x, y, timestamp } => {
                let old_pos = state.mouse_position;
                state.mouse_position = (*x, *y);
                state.last_input = *timestamp;

                // Analyze movement pattern
                let distance = ((x - old_pos.0).pow(2) + (y - old_pos.1).pow(2)) as f64;
                if distance > 100.0 {
                    state.mouse_movement_pattern = MovementPattern::Erratic;
                } else if distance > 10.0 {
                    state.mouse_movement_pattern = MovementPattern::Steady;
                } else if distance > 1.0 {
                    state.mouse_movement_pattern = MovementPattern::Precise;
                }
            }
            InputEvent::MouseClick { timestamp, .. } => {
                state.last_input = *timestamp;
            }
            _ => {}
        }
    }

    /// Register a callback for input events
    pub async fn register_callback(
        &self,
        callback: Box<dyn Fn(InputEvent) + Send + Sync>,
    ) -> anyhow::Result<()> {
        let mut callbacks = self.callbacks.write().await;
        callbacks.push(callback);
        Ok(())
    }

    /// Get current input state
    pub async fn get_current_state(&self) -> anyhow::Result<InputState> {
        let state = self.current_state.read().await;
        Ok(state.clone())
    }

    /// Get input statistics
    pub async fn get_statistics(&self) -> anyhow::Result<InputStats> {
        let stats = self.stats.read().await;
        Ok(stats.clone())
    }

    /// Add an input event to the buffer
    pub async fn add_event(&self, event: InputEvent) {
        let mut buffer = self.input_buffer.lock();
        if buffer.len() >= self.config.buffer_size {
            buffer.pop_front(); // Remove oldest event
        }
        buffer.push_back(event);
    }

    /// Check if monitoring is enabled
    pub async fn is_enabled(&self) -> bool {
        self.config.enabled
    }

    /// Update configuration
    pub async fn update_config(&mut self, config: InputMonitorConfig) -> anyhow::Result<()> {
        self.config = config;
        
        // Restart if necessary
        if *self.is_running.read().await {
            self.stop().await?;
            self.start().await?;
        }
        
        Ok(())
    }
}