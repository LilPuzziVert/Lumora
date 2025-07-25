"""
LUMORA Modern GUI - Huly.io Inspired Interface

Stunning, animated interface with dark theme, bright accent colors,
smooth animations, and impressive visual effects.
"""

import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
import asyncio
import threading
import time
import math
from typing import Dict, Any, Optional, Callable
from pathlib import Path
import json

# Set appearance mode and color theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class LumoraModernGUI:
    """
    God-tier modern GUI for Lumora with stunning visuals and animations.
    Inspired by Huly.io's beautiful design language.
    """
    
    def __init__(self, engine, config, privacy):
        self.engine = engine
        self.config = config
        self.privacy = privacy
        
        # Color palette inspired by Huly.io
        self.colors = {
            'bg_primary': '#0A0A0B',        # Deep black
            'bg_secondary': '#141416',       # Charcoal
            'bg_tertiary': '#1C1C1F',       # Dark grey
            'bg_card': '#252529',           # Card background
            'accent_blue': '#3B82F6',       # Bright blue
            'accent_purple': '#8B5CF6',     # Purple
            'accent_green': '#10B981',      # Emerald
            'accent_pink': '#EC4899',       # Pink
            'accent_orange': '#F59E0B',     # Amber
            'accent_red': '#EF4444',        # Red
            'text_primary': '#FFFFFF',      # White
            'text_secondary': '#A1A1AA',    # Grey
            'text_muted': '#71717A',        # Muted grey
            'border': '#27272A',            # Border
            'glow_blue': '#3B82F6',         # Glow effects
            'glow_purple': '#8B5CF6',
            'success': '#10B981',
            'warning': '#F59E0B',
            'error': '#EF4444'
        }
        
        # Animation properties
        self.animation_speed = 16  # 60 FPS
        self.animations = {}
        self.is_animating = False
        
        # Window properties
        self.root = None
        self.canvas = None
        self.popup_windows = []
        
        # UI State
        self.current_page = "dashboard"
        self.sidebar_expanded = True
        self.ai_thinking = False
        
        # Real-time data
        self.live_stats = {
            'cpu_usage': 0,
            'memory_usage': 0,
            'network_activity': 0,
            'ai_confidence': 0,
            'active_processes': 0
        }
        
    async def initialize(self):
        """Initialize the modern GUI with stunning visuals."""
        try:
            # Create main window
            self._create_main_window()
            
            # Setup canvas for custom drawing
            self._setup_canvas()
            
            # Create animated components
            self._create_animated_ui()
            
            # Start animation loops
            self._start_animations()
            
            # Start real-time updates
            asyncio.create_task(self._real_time_updates())
            
            return True
            
        except Exception as e:
            print(f"Failed to initialize modern GUI: {e}")
            return False
    
    def _create_main_window(self):
        """Create the main application window with modern styling."""
        self.root = ctk.CTk()
        self.root.title("LUMORA - God-Tier AI Assistant")
        self.root.geometry("1400x900")
        self.root.minsize(1200, 800)
        
        # Set window properties
        self.root.configure(fg_color=self.colors['bg_primary'])
        
        # Make window slightly transparent for modern look
        self.root.attributes('-alpha', 0.98)
        
        # Custom window decorations
        self._setup_custom_titlebar()
        
        # Enable window effects
        self._enable_window_effects()
    
    def _setup_canvas(self):
        """Setup canvas for custom graphics and animations."""
        self.canvas = tk.Canvas(
            self.root,
            bg=self.colors['bg_primary'],
            highlightthickness=0,
            bd=0
        )
        self.canvas.place(x=0, y=0, relwidth=1, relheight=1)
        
        # Bind canvas events
        self.canvas.bind('<Configure>', self._on_canvas_resize)
        self.canvas.bind('<Button-1>', self._on_canvas_click)
        self.canvas.bind('<Motion>', self._on_canvas_motion)
    
    def _create_animated_ui(self):
        """Create the main UI with animated components."""
        # Create sidebar
        self._create_animated_sidebar()
        
        # Create main content area
        self._create_main_content()
        
        # Create floating elements
        self._create_floating_elements()
        
        # Create AI assistant popup
        self._create_ai_popup()
        
        # Create notification system
        self._create_notification_system()
    
    def _create_animated_sidebar(self):
        """Create animated sidebar with glowing effects."""
        sidebar_width = 280 if self.sidebar_expanded else 80
        
        # Sidebar background with gradient
        self.sidebar_frame = ctk.CTkFrame(
            self.root,
            width=sidebar_width,
            height=900,
            corner_radius=0,
            fg_color=self.colors['bg_secondary'],
            border_width=1,
            border_color=self.colors['border']
        )
        self.sidebar_frame.place(x=0, y=0)
        
        # Lumora logo with glow effect
        self._create_logo_with_glow()
        
        # Navigation items with hover animations
        nav_items = [
            ("🏠", "Dashboard", "dashboard", self.colors['accent_blue']),
            ("🧠", "AI Brain", "ai_brain", self.colors['accent_purple']),
            ("🔒", "Privacy", "privacy", self.colors['accent_green']),
            ("⚙️", "Settings", "settings", self.colors['accent_orange']),
            ("📊", "Analytics", "analytics", self.colors['accent_pink']),
            ("🚀", "Automation", "automation", self.colors['accent_red'])
        ]
        
        self.nav_buttons = []
        for i, (icon, text, page, color) in enumerate(nav_items):
            btn = self._create_nav_button(icon, text, page, color, i)
            self.nav_buttons.append(btn)
        
        # Status indicator with pulse animation
        self._create_status_indicator()
    
    def _create_logo_with_glow(self):
        """Create Lumora logo with animated glow effect."""
        logo_frame = ctk.CTkFrame(
            self.sidebar_frame,
            width=240,
            height=80,
            fg_color='transparent'
        )
        logo_frame.place(x=20, y=20)
        
        # Main logo text
        logo_label = ctk.CTkLabel(
            logo_frame,
            text="LUMORA",
            font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold"),
            text_color=self.colors['text_primary']
        )
        logo_label.place(x=10, y=15)
        
        # Subtitle
        subtitle_label = ctk.CTkLabel(
            logo_frame,
            text="God-Tier AI Assistant",
            font=ctk.CTkFont(family="Segoe UI", size=10),
            text_color=self.colors['accent_blue']
        )
        subtitle_label.place(x=10, y=45)
        
        # Add glow animation to logo
        self._animate_logo_glow(logo_label)
    
    def _create_nav_button(self, icon, text, page, color, index):
        """Create animated navigation button."""
        y_pos = 120 + (index * 70)
        
        # Button frame
        btn_frame = ctk.CTkFrame(
            self.sidebar_frame,
            width=240,
            height=60,
            fg_color='transparent',
            corner_radius=12
        )
        btn_frame.place(x=20, y=y_pos)
        
        # Create button with hover effects
        btn = ctk.CTkButton(
            btn_frame,
            width=220,
            height=50,
            text=f"{icon}  {text}" if self.sidebar_expanded else icon,
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            fg_color='transparent',
            text_color=self.colors['text_secondary'],
            hover_color=color + "20",  # Semi-transparent color
            corner_radius=12,
            border_width=2,
            border_color='transparent',
            command=lambda p=page: self._navigate_to_page(p)
        )
        btn.place(x=0, y=0)
        
        # Add hover animations
        self._add_button_hover_effects(btn, color)
        
        return btn
    
    def _create_main_content(self):
        """Create main content area with dynamic layouts."""
        content_x = 280 if self.sidebar_expanded else 80
        content_width = 1400 - content_x
        
        self.main_frame = ctk.CTkFrame(
            self.root,
            width=content_width,
            height=900,
            corner_radius=0,
            fg_color=self.colors['bg_primary']
        )
        self.main_frame.place(x=content_x, y=0)
        
        # Create different page contents
        self._create_dashboard_content()
        self._create_ai_brain_content()
        self._create_privacy_content()
        
    def _create_dashboard_content(self):
        """Create animated dashboard with real-time stats."""
        # Header with animated gradient
        header_frame = ctk.CTkFrame(
            self.main_frame,
            width=1100,
            height=100,
            fg_color=self.colors['bg_secondary'],
            corner_radius=20
        )
        header_frame.place(x=20, y=20)
        
        # Welcome message with typewriter effect
        welcome_label = ctk.CTkLabel(
            header_frame,
            text="Welcome to LUMORA",
            font=ctk.CTkFont(family="Segoe UI", size=32, weight="bold"),
            text_color=self.colors['text_primary']
        )
        welcome_label.place(x=30, y=20)
        
        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="Your God-Tier AI is monitoring and optimizing your system",
            font=ctk.CTkFont(family="Segoe UI", size=14),
            text_color=self.colors['accent_blue']
        )
        subtitle_label.place(x=30, y=55)
        
        # Animated stats cards
        self._create_stats_cards()
        
        # Real-time activity feed
        self._create_activity_feed()
        
        # AI insights panel
        self._create_ai_insights_panel()
    
    def _create_stats_cards(self):
        """Create animated statistics cards."""
        stats = [
            ("CPU Usage", "cpu_usage", "%", self.colors['accent_blue']),
            ("Memory", "memory_usage", "%", self.colors['accent_green']),
            ("AI Confidence", "ai_confidence", "%", self.colors['accent_purple']),
            ("Network", "network_activity", "KB/s", self.colors['accent_orange'])
        ]
        
        self.stat_cards = []
        for i, (title, key, unit, color) in enumerate(stats):
            x_pos = 20 + (i * 280)
            card = self._create_animated_stat_card(title, key, unit, color, x_pos, 140)
            self.stat_cards.append(card)
    
    def _create_animated_stat_card(self, title, key, unit, color, x, y):
        """Create individual animated stat card."""
        # Card frame with glow effect
        card_frame = ctk.CTkFrame(
            self.main_frame,
            width=260,
            height=120,
            fg_color=self.colors['bg_card'],
            corner_radius=16,
            border_width=1,
            border_color=color + "40"
        )
        card_frame.place(x=x, y=y)
        
        # Title
        title_label = ctk.CTkLabel(
            card_frame,
            text=title,
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=self.colors['text_secondary']
        )
        title_label.place(x=20, y=15)
        
        # Value with animated counter
        value_label = ctk.CTkLabel(
            card_frame,
            text="0" + unit,
            font=ctk.CTkFont(family="Segoe UI", size=28, weight="bold"),
            text_color=color
        )
        value_label.place(x=20, y=40)
        
        # Progress bar with glow
        progress_bar = ctk.CTkProgressBar(
            card_frame,
            width=220,
            height=8,
            progress_color=color,
            fg_color=self.colors['bg_tertiary']
        )
        progress_bar.place(x=20, y=85)
        
        # Add pulsing animation
        self._animate_card_pulse(card_frame, color)
        
        return {
            'frame': card_frame,
            'value_label': value_label,
            'progress_bar': progress_bar,
            'key': key,
            'unit': unit,
            'color': color
        }
    
    def _create_floating_elements(self):
        """Create floating UI elements with animations."""
        # Floating action button
        self.fab = ctk.CTkButton(
            self.root,
            width=60,
            height=60,
            text="🤖",
            font=ctk.CTkFont(size=24),
            fg_color=self.colors['accent_purple'],
            hover_color=self.colors['accent_blue'],
            corner_radius=30,
            command=self._toggle_ai_popup
        )
        self.fab.place(x=1320, y=820)
        
        # Add floating animation
        self._animate_floating_button(self.fab)
        
        # Quick actions panel
        self._create_quick_actions_panel()
    
    def _create_ai_popup(self):
        """Create impressive AI assistant popup."""
        self.ai_popup = None  # Will be created when needed
    
    def _show_ai_popup(self):
        """Show AI popup with stunning animations."""
        if self.ai_popup:
            return
        
        # Create popup window
        self.ai_popup = ctk.CTkToplevel(self.root)
        self.ai_popup.title("LUMORA AI Assistant")
        self.ai_popup.geometry("800x600")
        self.ai_popup.configure(fg_color=self.colors['bg_primary'])
        
        # Make popup appear with animation
        self.ai_popup.attributes('-alpha', 0)
        self._animate_popup_appear(self.ai_popup)
        
        # AI chat interface with animations
        self._create_ai_chat_interface()
        
        # AI thinking indicator
        self._create_ai_thinking_indicator()
        
        # Voice visualization
        self._create_voice_visualization()
    
    def _create_ai_chat_interface(self):
        """Create animated AI chat interface."""
        # Chat container
        chat_frame = ctk.CTkFrame(
            self.ai_popup,
            width=760,
            height=450,
            fg_color=self.colors['bg_secondary'],
            corner_radius=20
        )
        chat_frame.place(x=20, y=20)
        
        # AI avatar with glow
        self._create_ai_avatar()
        
        # Chat messages area
        self.chat_text = ctk.CTkTextbox(
            chat_frame,
            width=600,
            height=350,
            fg_color=self.colors['bg_tertiary'],
            text_color=self.colors['text_primary'],
            font=ctk.CTkFont(family="Segoe UI", size=12)
        )
        self.chat_text.place(x=80, y=20)
        
        # Input area
        input_frame = ctk.CTkFrame(
            self.ai_popup,
            width=760,
            height=100,
            fg_color=self.colors['bg_card'],
            corner_radius=16
        )
        input_frame.place(x=20, y=480)
        
        # Chat input with glow effect
        self.chat_input = ctk.CTkEntry(
            input_frame,
            width=600,
            height=40,
            placeholder_text="Ask Lumora anything...",
            font=ctk.CTkFont(family="Segoe UI", size=14),
            fg_color=self.colors['bg_tertiary'],
            text_color=self.colors['text_primary'],
            border_color=self.colors['accent_blue']
        )
        self.chat_input.place(x=20, y=20)
        self.chat_input.bind('<Return>', self._send_ai_message)
        
        # Send button with hover animation
        send_btn = ctk.CTkButton(
            input_frame,
            width=100,
            height=40,
            text="Send",
            fg_color=self.colors['accent_blue'],
            hover_color=self.colors['accent_purple'],
            command=self._send_ai_message
        )
        send_btn.place(x=640, y=20)
        
        # Add initial greeting with typewriter effect
        self._add_ai_message("Hello! I'm LUMORA, your god-tier AI assistant. How can I help you today?", animate=True)
    
    def _create_notification_system(self):
        """Create animated notification system."""
        self.notifications = []
        self.notification_queue = []
    
    def show_notification(self, title, message, type="info", duration=5000):
        """Show animated notification popup."""
        colors = {
            'info': self.colors['accent_blue'],
            'success': self.colors['success'],
            'warning': self.colors['warning'],
            'error': self.colors['error']
        }
        
        color = colors.get(type, self.colors['accent_blue'])
        
        # Create notification frame
        notif_frame = ctk.CTkFrame(
            self.root,
            width=350,
            height=100,
            fg_color=self.colors['bg_card'],
            corner_radius=12,
            border_width=2,
            border_color=color
        )
        
        # Position notification
        y_pos = 20 + (len(self.notifications) * 110)
        notif_frame.place(x=1030, y=y_pos)
        
        # Title
        title_label = ctk.CTkLabel(
            notif_frame,
            text=title,
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=color
        )
        title_label.place(x=15, y=15)
        
        # Message
        msg_label = ctk.CTkLabel(
            notif_frame,
            text=message,
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=self.colors['text_secondary'],
            wraplength=300
        )
        msg_label.place(x=15, y=40)
        
        # Close button
        close_btn = ctk.CTkButton(
            notif_frame,
            width=20,
            height=20,
            text="✕",
            fg_color='transparent',
            text_color=self.colors['text_muted'],
            hover_color=self.colors['error'],
            command=lambda: self._close_notification(notif_frame)
        )
        close_btn.place(x=320, y=10)
        
        # Animate notification appearance
        self._animate_notification_appear(notif_frame)
        
        # Auto-remove after duration
        self.root.after(duration, lambda: self._close_notification(notif_frame))
        
        self.notifications.append(notif_frame)
    
    def _start_animations(self):
        """Start all animation loops."""
        self.is_animating = True
        self._animation_loop()
    
    def _animation_loop(self):
        """Main animation loop running at 60 FPS."""
        if not self.is_animating:
            return
        
        try:
            # Update all animations
            self._update_glow_effects()
            self._update_particle_effects()
            self._update_breathing_animations()
            self._update_floating_animations()
            
            # Schedule next frame
            self.root.after(self.animation_speed, self._animation_loop)
            
        except Exception as e:
            print(f"Animation error: {e}")
    
    async def _real_time_updates(self):
        """Real-time data updates for live stats."""
        while True:
            try:
                # Get real system stats
                if self.engine:
                    stats = self.engine.get_live_stats()
                    self.live_stats.update(stats)
                
                # Update stat cards
                self._update_stat_cards()
                
                # Update AI thinking indicator
                self._update_ai_thinking()
                
                await asyncio.sleep(0.5)  # Update every 500ms
                
            except Exception as e:
                print(f"Real-time update error: {e}")
                await asyncio.sleep(1)
    
    def _update_stat_cards(self):
        """Update animated stat cards with current data."""
        for card in self.stat_cards:
            key = card['key']
            value = self.live_stats.get(key, 0)
            unit = card['unit']
            
            # Animate value change
            current_text = card['value_label'].cget('text')
            current_value = float(current_text.replace(unit, '')) if current_text != '0' + unit else 0
            
            # Smooth interpolation
            diff = value - current_value
            new_value = current_value + (diff * 0.1)
            
            card['value_label'].configure(text=f"{new_value:.1f}{unit}")
            card['progress_bar'].set(new_value / 100)
    
    # Animation helper methods
    def _animate_logo_glow(self, widget):
        """Animate logo glow effect."""
        def pulse():
            if hasattr(widget, 'master'):
                # Create pulsing glow effect
                current_time = time.time()
                alpha = (math.sin(current_time * 2) + 1) / 2 * 0.3 + 0.7
                
                # Apply glow (simplified for CustomTkinter)
                widget.configure(text_color=f"#{int(255*alpha):02x}{int(255*alpha):02x}FF")
                
                widget.after(50, pulse)
        
        pulse()
    
    def _animate_floating_button(self, button):
        """Animate floating action button."""
        def float_animation():
            current_time = time.time()
            offset = math.sin(current_time * 2) * 5
            
            # Get current position
            current_y = button.winfo_y()
            base_y = 820
            new_y = base_y + offset
            
            button.place(x=1320, y=new_y)
            button.after(50, float_animation)
        
        float_animation()
    
    def _animate_popup_appear(self, popup):
        """Animate popup appearance."""
        def fade_in(alpha=0):
            popup.attributes('-alpha', alpha)
            if alpha < 1:
                popup.after(20, lambda: fade_in(alpha + 0.1))
        
        fade_in()
    
    # Event handlers
    def _toggle_ai_popup(self):
        """Toggle AI popup visibility."""
        if self.ai_popup and self.ai_popup.winfo_exists():
            self.ai_popup.destroy()
            self.ai_popup = None
        else:
            self._show_ai_popup()
    
    def _send_ai_message(self, event=None):
        """Send message to AI with animations."""
        if not hasattr(self, 'chat_input'):
            return
            
        message = self.chat_input.get().strip()
        if not message:
            return
        
        # Clear input
        self.chat_input.delete(0, tk.END)
        
        # Add user message with animation
        self._add_chat_message(f"You: {message}", self.colors['accent_blue'], animate=True)
        
        # Show AI thinking
        self.ai_thinking = True
        self._show_ai_thinking()
        
        # Process with AI (async)
        asyncio.create_task(self._process_ai_response(message))
    
    async def _process_ai_response(self, message):
        """Process AI response with realistic delay and animations."""
        try:
            # Simulate thinking time
            await asyncio.sleep(1)
            
            # Get AI response
            if self.engine and self.engine.ai_brain:
                response = await self.engine.ai_brain.process_natural_language(message)
                ai_text = response.text if response else "I'm having trouble processing that right now."
            else:
                ai_text = "AI system is initializing. Please try again in a moment."
            
            # Hide thinking indicator
            self.ai_thinking = False
            
            # Add AI response with typewriter effect
            self._add_ai_message(ai_text, animate=True)
            
        except Exception as e:
            self.ai_thinking = False
            self._add_ai_message(f"Error: {e}", animate=True)
    
    def _add_ai_message(self, message, animate=False):
        """Add AI message with optional typewriter animation."""
        if not hasattr(self, 'chat_text'):
            return
        
        if animate:
            self._typewriter_effect(f"LUMORA: {message}\n\n")
        else:
            self.chat_text.insert(tk.END, f"LUMORA: {message}\n\n")
            self.chat_text.see(tk.END)
    
    def _add_chat_message(self, message, color, animate=False):
        """Add chat message with color and animation."""
        if not hasattr(self, 'chat_text'):
            return
        
        if animate:
            self._typewriter_effect(f"{message}\n\n")
        else:
            self.chat_text.insert(tk.END, f"{message}\n\n")
            self.chat_text.see(tk.END)
    
    def _typewriter_effect(self, text, index=0):
        """Create typewriter effect for text."""
        if index < len(text):
            self.chat_text.insert(tk.END, text[index])
            self.chat_text.see(tk.END)
            self.root.after(30, lambda: self._typewriter_effect(text, index + 1))
    
    # Advanced features
    def create_context_popup(self, x, y, context_info):
        """Create context-aware popup at cursor position."""
        popup = ctk.CTkToplevel(self.root)
        popup.geometry(f"400x300+{x}+{y}")
        popup.configure(fg_color=self.colors['bg_card'])
        popup.attributes('-topmost', True)
        
        # Animate appearance
        popup.attributes('-alpha', 0)
        self._animate_popup_appear(popup)
        
        # Add context content
        self._populate_context_popup(popup, context_info)
        
        # Auto-hide after delay
        popup.after(5000, popup.destroy)
    
    def show_ai_insight(self, insight_text, confidence=0.9):
        """Show AI insight with confidence visualization."""
        insight_popup = ctk.CTkToplevel(self.root)
        insight_popup.geometry("500x200+500+300")
        insight_popup.configure(fg_color=self.colors['bg_secondary'])
        
        # Confidence indicator
        confidence_frame = ctk.CTkFrame(insight_popup, fg_color='transparent')
        confidence_frame.pack(pady=10)
        
        ctk.CTkLabel(
            confidence_frame,
            text=f"AI Confidence: {confidence*100:.1f}%",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=self.colors['accent_green'] if confidence > 0.8 else self.colors['warning']
        ).pack()
        
        # Progress bar for confidence
        conf_bar = ctk.CTkProgressBar(
            confidence_frame,
            width=300,
            progress_color=self.colors['accent_green'] if confidence > 0.8 else self.colors['warning']
        )
        conf_bar.pack(pady=5)
        conf_bar.set(confidence)
        
        # Insight text
        insight_label = ctk.CTkLabel(
            insight_popup,
            text=insight_text,
            font=ctk.CTkFont(size=14),
            text_color=self.colors['text_primary'],
            wraplength=450
        )
        insight_label.pack(pady=20)
        
        # Animate appearance
        insight_popup.attributes('-alpha', 0)
        self._animate_popup_appear(insight_popup)
    
    # Additional animation methods (placeholder implementations)
    def _update_glow_effects(self): pass
    def _update_particle_effects(self): pass
    def _update_breathing_animations(self): pass
    def _update_floating_animations(self): pass
    def _create_ai_avatar(self): pass
    def _create_voice_visualization(self): pass
    def _create_ai_thinking_indicator(self): pass
    def _show_ai_thinking(self): pass
    def _update_ai_thinking(self): pass
    def _close_notification(self, frame): 
        if frame in self.notifications:
            self.notifications.remove(frame)
        frame.destroy()
    def _animate_notification_appear(self, frame): pass
    def _animate_card_pulse(self, frame, color): pass
    def _add_button_hover_effects(self, btn, color): pass
    def _create_status_indicator(self): pass
    def _create_activity_feed(self): pass
    def _create_ai_insights_panel(self): pass
    def _create_quick_actions_panel(self): pass
    def _create_ai_brain_content(self): pass
    def _create_privacy_content(self): pass
    def _navigate_to_page(self, page): 
        self.current_page = page
        print(f"Navigating to {page}")
    def _on_canvas_resize(self, event): pass
    def _on_canvas_click(self, event): pass
    def _on_canvas_motion(self, event): pass
    def _setup_custom_titlebar(self): pass
    def _enable_window_effects(self): pass
    def _populate_context_popup(self, popup, context_info): pass
    
    async def run(self):
        """Run the modern GUI."""
        self.root.mainloop()
    
    async def shutdown(self):
        """Shutdown the modern GUI."""
        self.is_animating = False
        if self.root:
            self.root.destroy()