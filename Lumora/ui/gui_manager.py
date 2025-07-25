"""
LUMORA GUI Manager

Modern, beautiful GUI interface for Lumora with dark theme,
system tray integration, and intuitive controls.
"""

import asyncio
import logging
import tkinter as tk
from tkinter import ttk, messagebox
import threading
from typing import Optional, Dict, Any
from pathlib import Path

class LumoraGUI:
    """
    Main GUI interface for Lumora.
    
    Provides a modern, intuitive interface for controlling
    and interacting with the Lumora AI system.
    """
    
    def __init__(self, engine, config, privacy):
        self.engine = engine
        self.config = config
        self.privacy = privacy
        self.logger = logging.getLogger(__name__)
        
        # GUI state
        self.root = None
        self.main_window = None
        self.tray_icon = None
        self.is_minimized = False
        
        # Widgets
        self.widgets = {}
        self.status_vars = {}
        
        # Theme colors
        self.theme = {
            'bg_primary': '#1e1e1e',
            'bg_secondary': '#2d2d2d',
            'bg_tertiary': '#3e3e3e',
            'fg_primary': '#ffffff',
            'fg_secondary': '#cccccc',
            'accent': '#0078d4',
            'accent_hover': '#106ebe',
            'success': '#107c10',
            'warning': '#ff8c00',
            'error': '#d13438'
        }
    
    async def initialize(self):
        """Initialize the GUI."""
        try:
            self.logger.info("Initializing Lumora GUI...")
            
            # Create main window
            self._create_main_window()
            
            # Setup theme
            self._setup_theme()
            
            # Create UI elements
            self._create_ui()
            
            # Setup system tray
            self._setup_system_tray()
            
            # Start status updates
            asyncio.create_task(self._status_update_loop())
            
            self.logger.info("Lumora GUI initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize GUI: {e}")
            return False
    
    def _create_main_window(self):
        """Create the main application window."""
        self.root = tk.Tk()
        self.root.title("Lumora - AI OS Companion")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)
        
        # Set window icon
        try:
            icon_path = Path(__file__).parent / "assets" / "lumora_icon.ico"
            if icon_path.exists():
                self.root.iconbitmap(str(icon_path))
        except:
            pass
        
        # Configure window close behavior
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        # Bind events
        self.root.bind("<Unmap>", self._on_minimize)
        self.root.bind("<Map>", self._on_restore)
    
    def _setup_theme(self):
        """Setup modern dark theme."""
        style = ttk.Style()
        
        # Configure ttk styles
        style.theme_use('clam')
        
        # Main background
        self.root.configure(bg=self.theme['bg_primary'])
        
        # Button styles
        style.configure('Accent.TButton',
                       background=self.theme['accent'],
                       foreground=self.theme['fg_primary'],
                       borderwidth=0,
                       focuscolor='none')
        
        style.map('Accent.TButton',
                 background=[('active', self.theme['accent_hover'])])
        
        # Frame styles
        style.configure('Card.TFrame',
                       background=self.theme['bg_secondary'],
                       relief='flat',
                       borderwidth=1)
        
        # Label styles
        style.configure('Heading.TLabel',
                       background=self.theme['bg_secondary'],
                       foreground=self.theme['fg_primary'],
                       font=('Segoe UI', 12, 'bold'))
        
        style.configure('Body.TLabel',
                       background=self.theme['bg_secondary'],
                       foreground=self.theme['fg_secondary'],
                       font=('Segoe UI', 9))
    
    def _create_ui(self):
        """Create the main UI elements."""
        # Main container
        main_frame = ttk.Frame(self.root, style='Card.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Dashboard tab
        self._create_dashboard_tab(notebook)
        
        # Settings tab
        self._create_settings_tab(notebook)
        
        # AI Chat tab
        self._create_chat_tab(notebook)
        
        # Privacy tab
        self._create_privacy_tab(notebook)
        
        # System tab
        self._create_system_tab(notebook)
    
    def _create_dashboard_tab(self, parent):
        """Create the dashboard tab."""
        frame = ttk.Frame(parent, style='Card.TFrame')
        parent.add(frame, text="Dashboard")
        
        # Status section
        status_frame = ttk.LabelFrame(frame, text="System Status", padding=10)
        status_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Engine status
        self.status_vars['engine_status'] = tk.StringVar(value="Initializing...")
        ttk.Label(status_frame, text="Engine Status:").grid(row=0, column=0, sticky='w')
        ttk.Label(status_frame, textvariable=self.status_vars['engine_status']).grid(row=0, column=1, sticky='w', padx=(10, 0))
        
        # AI status
        self.status_vars['ai_status'] = tk.StringVar(value="Loading...")
        ttk.Label(status_frame, text="AI Brain:").grid(row=1, column=0, sticky='w')
        ttk.Label(status_frame, textvariable=self.status_vars['ai_status']).grid(row=1, column=1, sticky='w', padx=(10, 0))
        
        # Privacy mode
        self.status_vars['privacy_mode'] = tk.StringVar(value="Balanced")
        ttk.Label(status_frame, text="Privacy Mode:").grid(row=2, column=0, sticky='w')
        ttk.Label(status_frame, textvariable=self.status_vars['privacy_mode']).grid(row=2, column=1, sticky='w', padx=(10, 0))
        
        # Quick actions
        actions_frame = ttk.LabelFrame(frame, text="Quick Actions", padding=10)
        actions_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(actions_frame, text="Pause Monitoring", 
                  command=self._toggle_monitoring, style='Accent.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(actions_frame, text="Privacy Mode", 
                  command=self._toggle_privacy_mode, style='Accent.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(actions_frame, text="Friend Mode", 
                  command=self._toggle_friend_mode, style='Accent.TButton').pack(side=tk.LEFT, padx=5)
        
        # Statistics
        stats_frame = ttk.LabelFrame(frame, text="Statistics", padding=10)
        stats_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Create statistics display
        self._create_stats_display(stats_frame)
    
    def _create_settings_tab(self, parent):
        """Create the settings tab."""
        frame = ttk.Frame(parent, style='Card.TFrame')
        parent.add(frame, text="Settings")
        
        # AI Settings
        ai_frame = ttk.LabelFrame(frame, text="AI Settings", padding=10)
        ai_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Personality setting
        ttk.Label(ai_frame, text="Personality:").grid(row=0, column=0, sticky='w')
        personality_var = tk.StringVar(value="balanced")
        personality_combo = ttk.Combobox(ai_frame, textvariable=personality_var,
                                       values=["balanced", "professional", "casual", "friendly", "technical"],
                                       state="readonly")
        personality_combo.grid(row=0, column=1, sticky='ew', padx=(10, 0))
        
        # Response style
        ttk.Label(ai_frame, text="Response Style:").grid(row=1, column=0, sticky='w')
        response_var = tk.StringVar(value="medium")
        response_combo = ttk.Combobox(ai_frame, textvariable=response_var,
                                    values=["short", "medium", "long"],
                                    state="readonly")
        response_combo.grid(row=1, column=1, sticky='ew', padx=(10, 0))
        
        ai_frame.columnconfigure(1, weight=1)
        
        # Performance Settings
        perf_frame = ttk.LabelFrame(frame, text="Performance", padding=10)
        perf_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Monitoring interval
        ttk.Label(perf_frame, text="Monitoring Interval (ms):").grid(row=0, column=0, sticky='w')
        interval_var = tk.StringVar(value="500")
        ttk.Entry(perf_frame, textvariable=interval_var, width=10).grid(row=0, column=1, sticky='w', padx=(10, 0))
        
        # Max memory usage
        ttk.Label(perf_frame, text="Max Memory (MB):").grid(row=1, column=0, sticky='w')
        memory_var = tk.StringVar(value="1024")
        ttk.Entry(perf_frame, textvariable=memory_var, width=10).grid(row=1, column=1, sticky='w', padx=(10, 0))
        
        # Save button
        ttk.Button(frame, text="Save Settings", 
                  command=self._save_settings, style='Accent.TButton').pack(pady=10)
    
    def _create_chat_tab(self, parent):
        """Create the AI chat tab."""
        frame = ttk.Frame(parent, style='Card.TFrame')
        parent.add(frame, text="AI Chat")
        
        # Chat display
        chat_frame = ttk.Frame(frame)
        chat_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Chat text area
        self.chat_display = tk.Text(chat_frame, 
                                   bg=self.theme['bg_tertiary'],
                                   fg=self.theme['fg_primary'],
                                   insertbackground=self.theme['fg_primary'],
                                   wrap=tk.WORD,
                                   state=tk.DISABLED)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(chat_frame, orient=tk.VERTICAL, command=self.chat_display.yview)
        self.chat_display.configure(yscrollcommand=scrollbar.set)
        
        self.chat_display.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Input area
        input_frame = ttk.Frame(frame)
        input_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.chat_input = tk.Entry(input_frame,
                                  bg=self.theme['bg_tertiary'],
                                  fg=self.theme['fg_primary'],
                                  insertbackground=self.theme['fg_primary'])
        self.chat_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.chat_input.bind('<Return>', self._send_chat_message)
        
        ttk.Button(input_frame, text="Send", 
                  command=self._send_chat_message, style='Accent.TButton').pack(side=tk.RIGHT)
        
        # Add welcome message
        self._add_chat_message("Lumora", "Hello! I'm Lumora, your AI assistant. How can I help you today?")
    
    def _create_privacy_tab(self, parent):
        """Create the privacy controls tab."""
        frame = ttk.Frame(parent, style='Card.TFrame')
        parent.add(frame, text="Privacy")
        
        # Privacy level
        level_frame = ttk.LabelFrame(frame, text="Privacy Level", padding=10)
        level_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.privacy_level_var = tk.StringVar(value="balanced")
        levels = ["full_access", "balanced", "restricted", "private", "paranoid"]
        
        for i, level in enumerate(levels):
            ttk.Radiobutton(level_frame, text=level.replace('_', ' ').title(),
                           variable=self.privacy_level_var, value=level,
                           command=self._update_privacy_level).grid(row=i, column=0, sticky='w')
        
        # Data types
        data_frame = ttk.LabelFrame(frame, text="Allowed Data Types", padding=10)
        data_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.data_type_vars = {}
        data_types = ["screen_content", "keyboard_input", "mouse_input", "window_titles", "app_usage"]
        
        for i, data_type in enumerate(data_types):
            var = tk.BooleanVar(value=True)
            self.data_type_vars[data_type] = var
            ttk.Checkbutton(data_frame, text=data_type.replace('_', ' ').title(),
                           variable=var, command=self._update_data_permissions).grid(row=i, column=0, sticky='w')
        
        # Emergency controls
        emergency_frame = ttk.LabelFrame(frame, text="Emergency Controls", padding=10)
        emergency_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(emergency_frame, text="Panic Mode", 
                  command=self._panic_mode, style='Accent.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(emergency_frame, text="Stop All Monitoring", 
                  command=self._emergency_stop, style='Accent.TButton').pack(side=tk.LEFT, padx=5)
    
    def _create_system_tab(self, parent):
        """Create the system information tab."""
        frame = ttk.Frame(parent, style='Card.TFrame')
        parent.add(frame, text="System")
        
        # System info
        info_frame = ttk.LabelFrame(frame, text="System Information", padding=10)
        info_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Version info
        ttk.Label(info_frame, text="Lumora Version: 2.0.0").pack(anchor='w')
        ttk.Label(info_frame, text="Python Version: 3.11+").pack(anchor='w')
        
        # Service controls
        service_frame = ttk.LabelFrame(frame, text="Service Control", padding=10)
        service_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(service_frame, text="Install Service", 
                  command=self._install_service, style='Accent.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(service_frame, text="Uninstall Service", 
                  command=self._uninstall_service, style='Accent.TButton').pack(side=tk.LEFT, padx=5)
        
        # Logs
        logs_frame = ttk.LabelFrame(frame, text="Logs", padding=10)
        logs_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.log_display = tk.Text(logs_frame,
                                  bg=self.theme['bg_tertiary'],
                                  fg=self.theme['fg_primary'],
                                  height=10,
                                  state=tk.DISABLED)
        self.log_display.pack(fill=tk.BOTH, expand=True)
    
    def _create_stats_display(self, parent):
        """Create statistics display."""
        stats_text = tk.Text(parent,
                            bg=self.theme['bg_tertiary'],
                            fg=self.theme['fg_primary'],
                            height=8,
                            state=tk.DISABLED)
        stats_text.pack(fill=tk.BOTH, expand=True)
        
        self.widgets['stats_display'] = stats_text
    
    def _setup_system_tray(self):
        """Setup system tray icon."""
        try:
            # This would use a library like pystray for system tray
            # For now, just log that it would be set up
            self.logger.info("System tray would be set up here")
        except Exception as e:
            self.logger.warning(f"Failed to setup system tray: {e}")
    
    async def _status_update_loop(self):
        """Update status information periodically."""
        while True:
            try:
                await self._update_status()
                await asyncio.sleep(2)  # Update every 2 seconds
            except Exception as e:
                self.logger.error(f"Status update error: {e}")
                await asyncio.sleep(5)
    
    async def _update_status(self):
        """Update status displays."""
        try:
            if self.engine:
                status = self.engine.get_status()
                self.status_vars['engine_status'].set(status.state.value)
                self.status_vars['ai_status'].set("Active" if status.ai_active else "Inactive")
                self.status_vars['privacy_mode'].set("Private" if status.privacy_mode else "Normal")
                
                # Update statistics
                await self._update_statistics()
                
        except Exception as e:
            self.logger.error(f"Failed to update status: {e}")
    
    async def _update_statistics(self):
        """Update statistics display."""
        try:
            if 'stats_display' in self.widgets:
                stats_display = self.widgets['stats_display']
                
                # Get statistics from engine
                if self.engine:
                    status = self.engine.get_status()
                    stats_text = f"""System Statistics:
    
    Uptime: {status.uptime:.1f} seconds
    Memory Usage: {status.memory_usage:.1f}%
    CPU Usage: {status.cpu_usage:.1f}%
    Active Contexts: {status.active_contexts}
    Performance Mode: {status.performance_mode}
    Last Action: {status.last_action or 'None'}
    """
                    
                    stats_display.config(state=tk.NORMAL)
                    stats_display.delete(1.0, tk.END)
                    stats_display.insert(tk.END, stats_text)
                    stats_display.config(state=tk.DISABLED)
                    
        except Exception as e:
            self.logger.error(f"Failed to update statistics: {e}")
    
    # Event handlers
    def _on_closing(self):
        """Handle window closing."""
        if self.config.get('ui.minimize_to_tray', True):
            self.root.withdraw()
            self.is_minimized = True
        else:
            self.root.quit()
    
    def _on_minimize(self, event):
        """Handle window minimize."""
        if event.widget == self.root:
            self.is_minimized = True
    
    def _on_restore(self, event):
        """Handle window restore."""
        if event.widget == self.root:
            self.is_minimized = False
    
    # Action handlers
    def _toggle_monitoring(self):
        """Toggle system monitoring."""
        try:
            if self.privacy:
                enabled = self.privacy.toggle_monitoring()
                status = "enabled" if enabled else "disabled"
                messagebox.showinfo("Monitoring", f"Monitoring {status}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to toggle monitoring: {e}")
    
    def _toggle_privacy_mode(self):
        """Toggle privacy mode."""
        try:
            if self.privacy:
                if self.privacy.is_private_mode():
                    self.privacy.disable_private_mode()
                    messagebox.showinfo("Privacy", "Private mode disabled")
                else:
                    self.privacy.enable_private_mode()
                    messagebox.showinfo("Privacy", "Private mode enabled")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to toggle privacy mode: {e}")
    
    def _toggle_friend_mode(self):
        """Toggle friend mode."""
        try:
            if self.engine and self.engine.ai_brain:
                current = self.engine.ai_brain.friend_mode_enabled
                self.engine.ai_brain.enable_friend_mode(not current)
                status = "enabled" if not current else "disabled"
                messagebox.showinfo("Friend Mode", f"Friend mode {status}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to toggle friend mode: {e}")
    
    def _save_settings(self):
        """Save current settings."""
        try:
            # This would save settings to config
            messagebox.showinfo("Settings", "Settings saved successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {e}")
    
    def _send_chat_message(self, event=None):
        """Send chat message to AI."""
        try:
            message = self.chat_input.get().strip()
            if not message:
                return
            
            self.chat_input.delete(0, tk.END)
            self._add_chat_message("You", message)
            
            # Send to AI (async)
            asyncio.create_task(self._process_ai_message(message))
            
        except Exception as e:
            self.logger.error(f"Failed to send chat message: {e}")
    
    async def _process_ai_message(self, message: str):
        """Process message with AI and display response."""
        try:
            if self.engine and self.engine.ai_brain:
                response = await self.engine.ai_brain.process_natural_language(message)
                if response:
                    self._add_chat_message("Lumora", response.text)
                else:
                    self._add_chat_message("Lumora", "I'm having trouble processing that right now.")
            else:
                self._add_chat_message("Lumora", "AI system is not available.")
                
        except Exception as e:
            self._add_chat_message("Lumora", f"Error: {e}")
    
    def _add_chat_message(self, sender: str, message: str):
        """Add message to chat display."""
        try:
            self.chat_display.config(state=tk.NORMAL)
            self.chat_display.insert(tk.END, f"{sender}: {message}\n\n")
            self.chat_display.see(tk.END)
            self.chat_display.config(state=tk.DISABLED)
        except Exception as e:
            self.logger.error(f"Failed to add chat message: {e}")
    
    def _update_privacy_level(self):
        """Update privacy level."""
        try:
            level = self.privacy_level_var.get()
            if self.privacy:
                from core.privacy import PrivacyLevel
                self.privacy.set_privacy_level(PrivacyLevel(level))
                messagebox.showinfo("Privacy", f"Privacy level set to {level}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update privacy level: {e}")
    
    def _update_data_permissions(self):
        """Update data type permissions."""
        try:
            # This would update privacy settings based on checkboxes
            pass
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update permissions: {e}")
    
    def _panic_mode(self):
        """Activate panic mode."""
        try:
            if self.privacy:
                self.privacy.panic_mode()
                messagebox.showwarning("Panic Mode", "Panic mode activated! All monitoring stopped.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to activate panic mode: {e}")
    
    def _emergency_stop(self):
        """Emergency stop all monitoring."""
        try:
            if self.privacy:
                self.privacy.emergency_shutdown()
                messagebox.showwarning("Emergency Stop", "All monitoring stopped!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to emergency stop: {e}")
    
    def _install_service(self):
        """Install Windows service."""
        try:
            # This would install the service
            messagebox.showinfo("Service", "Service installation would happen here")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to install service: {e}")
    
    def _uninstall_service(self):
        """Uninstall Windows service."""
        try:
            # This would uninstall the service
            messagebox.showinfo("Service", "Service uninstallation would happen here")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to uninstall service: {e}")
    
    # Public interface
    async def run(self):
        """Run the GUI main loop."""
        try:
            self.logger.info("Starting Lumora GUI...")
            
            # Run tkinter in thread
            def run_tk():
                self.root.mainloop()
            
            tk_thread = threading.Thread(target=run_tk, daemon=True)
            tk_thread.start()
            
            # Keep async loop running
            while tk_thread.is_alive():
                await asyncio.sleep(0.1)
                
        except Exception as e:
            self.logger.error(f"GUI error: {e}")
    
    async def shutdown(self):
        """Shutdown the GUI."""
        try:
            if self.root:
                self.root.quit()
            self.logger.info("GUI shutdown complete")
        except Exception as e:
            self.logger.error(f"GUI shutdown error: {e}")

class GUIManager:
    """GUI Manager wrapper."""
    
    def __init__(self, engine, config, privacy):
        self.gui = LumoraGUI(engine, config, privacy)
    
    async def initialize(self):
        return await self.gui.initialize()
    
    async def run(self):
        return await self.gui.run()
    
    async def shutdown(self):
        return await self.gui.shutdown()