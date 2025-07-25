# 🚀 LUMORA INSTALLATION & USAGE GUIDE
*Complete setup instructions for the God-Tier AI OS Companion*

## 📋 QUICK START

### Option 1: Automated Installation (Recommended)
```bash
# Download or clone Lumora
git clone <your-repo-url> C:\Lumora
cd C:\Lumora

# Run the smart installer as Administrator
python lumora_launcher.py --install
```

### Option 2: Launch Existing Installation
```bash
# Navigate to Lumora directory
cd C:\Lumora

# Interactive mode (recommended for first use)
python lumora_launcher.py --mode interactive

# Service mode (background operation)
python lumora_launcher.py --mode service
```

## 💾 SYSTEM REQUIREMENTS

### Minimum Requirements
- **OS**: Windows 11 (Build 22000+)
- **RAM**: 8GB (16GB recommended)
- **Storage**: 5GB free space
- **CPU**: Intel i5 / AMD Ryzen 5 or equivalent
- **GPU**: DirectX 12 compatible
- **Network**: Not required (fully offline capable)

### Recommended Specifications
- **OS**: Windows 11 Pro (Latest)
- **RAM**: 32GB
- **Storage**: 20GB SSD space
- **CPU**: Intel i7/AMD Ryzen 7 or better
- **GPU**: Dedicated graphics card (NVIDIA RTX/AMD RX series)

### Required Software
- **Python 3.9+** (installed automatically)
- **Rust 1.70+** (installed automatically)
- **Visual Studio Build Tools 2022** (installed automatically)
- **TouchDesigner 2023.11120+** (optional, for visual interface)
- **Administrator privileges** (required for installation)

## 🛠️ DETAILED INSTALLATION

### Step 1: Prerequisites Check
The installer will automatically check and install:
- Python 3.11
- Rust toolchain
- C++ build tools
- Git
- Chocolatey package manager

### Step 2: Architecture Components

#### Python Core (Automatic)
- AI brain and conversation management
- Context awareness and monitoring
- Memory and learning systems
- Configuration and privacy controls

#### Rust Automation (Automatic)
- High-performance input monitoring
- System automation and control
- Safety engine and validation
- Windows API integration

#### C++ System Integration (Automatic)
- Deep OS-level access
- Screen capture and analysis
- Service management
- Hardware interaction

#### TouchDesigner Interface (Manual Setup)
1. Download TouchDesigner from https://derivative.ca/
2. Install with default settings
3. Open `C:\Lumora\ui\lumora_main.toe`
4. Install custom operators from palette

### Step 3: Service Installation
The installer automatically:
- Creates Windows service "LumoraAI"
- Sets up auto-start configuration
- Configures system permissions
- Creates desktop shortcuts

## 🎮 HOW TO USE LUMORA

### First Launch
1. **Complete installation** using the guide above
2. **Restart your computer** (required for service registration)
3. **Open terminal as Administrator**
4. **Run**: `python C:\Lumora\lumora_launcher.py --mode interactive`

### Daily Usage Options

#### 1. Interactive Console Mode
```bash
python lumora_launcher.py --mode interactive
```
- Full-featured command interface
- Real-time status monitoring
- Direct AI conversation
- Manual automation control
- System diagnostics

#### 2. Background Service Mode
```bash
python lumora_launcher.py --mode service
```
- Silent background operation
- Hotkey activation (Ctrl+Alt+L)
- Voice activation ("Hey Lumora")
- System tray integration
- Automatic startup

#### 3. TouchDesigner Visual Mode
```bash
# Open TouchDesigner
# Load: C:\Lumora\ui\lumora_main.toe
# Experience stunning visual interface
```

### Hotkey Commands
- **Ctrl + Alt + L** - Open main interface
- **Ctrl + Alt + Shift + L** - Quick AI prompt
- **Win + L (hold 2 sec)** - Voice activation
- **Ctrl + Alt + Shift + L (hold 5 sec)** - Safe mode

### Voice Commands
- "Hey Lumora" - Activate voice interface
- "What can you see?" - Analyze current screen
- "Help me with this" - Context-aware assistance
- "Open calculator" - Launch applications
- "Type hello world" - Text automation
- "Click the save button" - UI automation
- "Show me system status" - Performance monitoring

### Console Commands

#### General Commands
```bash
help                    # Show all available commands
status                  # Display system status
restart                 # Restart Lumora engine
diagnostics            # Run system diagnostics
exit                   # Shutdown Lumora
```

#### AI Interaction
```bash
ai Hello, how are you?                    # Direct AI conversation
"What apps are running?"                  # Natural language queries
"Summarize my current screen"             # Context analysis
"Help me organize my desktop"             # Task assistance
```

#### Automation Commands
```bash
automation click 100 200                 # Click at coordinates
automation type "Hello World"            # Type text
automation key ctrl+c                    # Key combinations
automation scroll 500 300 up 3          # Scroll actions
automation drag 100 100 200 200         # Drag operations
```

## 🎨 TOUCHDESIGNER VISUAL INTERFACE

### Setup TouchDesigner Integration
1. **Install TouchDesigner** (free version works)
2. **Copy operators** to TouchDesigner palette
3. **Open main project**: `C:\Lumora\ui\lumora_main.toe`
4. **Configure Python path** in TouchDesigner preferences

### Visual Features
- **Particle-based AI responses** with emotion mapping
- **Real-time system metrics** visualization
- **Interactive 3D command interface** with gestures
- **Ambient lighting** based on system performance
- **Voice waveform** visualization during input
- **Automation flow** representation
- **Context awareness** radar display

### Custom Operators
- **LumoraAI TOP** - AI response visualization
- **SystemMonitor CHOP** - Live performance metrics
- **ContextFlow SOP** - 3D data flow representation
- **AnimatedUI COMP** - Huly.io-inspired components

## 🔧 CONFIGURATION

### Privacy Settings
```python
# Edit: C:\Lumora\config\privacy.yaml
monitoring_enabled: true
screen_reading_allowed: true
input_monitoring_allowed: true
automation_enabled: true
voice_recording_enabled: false
```

### AI Personality
```python
# Edit: C:\Lumora\config\ai.yaml
personality: "assistant"  # assistant, friend, professional
response_style: "helpful"  # concise, detailed, casual
learning_enabled: true
memory_retention_days: 30
```

### Performance Tuning
```python
# Edit: C:\Lumora\config\performance.yaml
cpu_limit_percent: 25
memory_limit_gb: 4
automation_frequency_hz: 10
visual_effects_quality: "high"  # low, medium, high, ultra
```

## 🚨 TROUBLESHOOTING

### Common Issues

#### Installation Problems
```bash
# Run as Administrator
Right-click Command Prompt → "Run as administrator"

# Check Windows version
winver  # Must be Windows 11 Build 22000+

# Manual dependency installation
choco install python rust cmake git visualstudio2022buildtools -y
```

#### Service Won't Start
```bash
# Check service status
sc query LumoraAI

# Reinstall service
python C:\Lumora\lumora_launcher.py --install

# Check Event Viewer
eventvwr.msc → Windows Logs → Application
```

#### TouchDesigner Issues
```bash
# Verify TouchDesigner version
# Must be 2023.11120 or later

# Check Python integration
# TouchDesigner → Edit → Preferences → Python
# Add: C:\Lumora\core

# Update GPU drivers
# NVIDIA/AMD latest drivers required
```

#### Performance Issues
```bash
# Check system requirements
# Close unnecessary applications
# Adjust performance settings in config
# Monitor CPU/RAM usage with Task Manager
```

### Error Recovery
```bash
# Safe mode (disables automation)
python lumora_launcher.py --mode interactive
> diagnostics

# Reset configuration
del C:\Lumora\config\*.yaml
python lumora_launcher.py --mode interactive

# Complete reinstallation
rmdir /s C:\Lumora
python lumora_launcher.py --install
```

### Getting Help
- **Built-in diagnostics**: `diagnostics` command
- **Log files**: `C:\Lumora\logs\`
- **Safe mode**: Hold Ctrl+Alt+Shift+L for 5 seconds
- **System recovery**: Restart Lumora service

## 🌟 ADVANCED FEATURES

### Custom Automation Scripts
```python
# Create: C:\Lumora\automation\custom\my_script.py
async def custom_automation():
    bridge = lumora.automation
    await bridge.click_at(100, 100)
    await bridge.type_text("Hello World")
    await bridge.press_key("Enter")
```

### AI Model Customization
```python
# Edit: C:\Lumora\ai\models\custom_responses.json
{
    "greetings": {
        "morning": "Good morning! Ready to tackle the day?",
        "evening": "Good evening! How can I help you wind down?"
    }
}
```

### Context Awareness Rules
```python
# Create: C:\Lumora\context\rules\productivity.py
def detect_productivity_context(apps, screen_content):
    if "code.exe" in apps and "python" in screen_content:
        return {"context": "coding", "suggestions": ["run tests", "commit changes"]}
```

### Visual Effect Customization
```python
# TouchDesigner custom shaders
# Edit: C:\Lumora\ui\shaders\custom_particle.frag
// Custom particle effects for AI responses
```

## 📊 MONITORING & ANALYTICS

### Performance Monitoring
- Real-time CPU/Memory usage
- Automation execution statistics
- AI response time tracking
- User interaction patterns
- System health indicators

### Usage Statistics
- Daily interaction count
- Most used commands
- Automation success rate
- Context switching patterns
- Performance bottlenecks

### Health Checks
- Component status monitoring
- Error rate tracking
- Memory leak detection
- Service uptime statistics
- User satisfaction metrics

## 🔒 PRIVACY & SECURITY

### Data Protection
- **100% Local Processing** - No cloud dependencies
- **Encrypted Storage** - All data encrypted at rest
- **Granular Controls** - Toggle monitoring per application
- **Audit Trail** - Complete log of all actions
- **Safe Mode** - Disable automation when needed

### Security Features
- **Sandboxed Execution** - Isolated automation environment
- **Permission System** - User confirmation for sensitive actions
- **Anti-malware Integration** - Built-in safety checks
- **Secure Communication** - Encrypted inter-component communication

## 🚀 OPTIMIZATION TIPS

### Performance Optimization
1. **Close unnecessary applications** during intensive tasks
2. **Adjust visual effects quality** based on hardware
3. **Use SSD storage** for better I/O performance
4. **Update GPU drivers** for TouchDesigner compatibility
5. **Configure antivirus exclusions** for Lumora directory

### Memory Management
1. **Set appropriate memory limits** in configuration
2. **Enable automatic cleanup** of old data
3. **Monitor memory usage** in diagnostics
4. **Restart service daily** for optimal performance

### Automation Efficiency
1. **Group related actions** into sequences
2. **Use conditional logic** to reduce unnecessary operations
3. **Implement proper delays** between actions
4. **Test automations thoroughly** before deployment

---

## 🎯 GETTING STARTED CHECKLIST

- [ ] Verify Windows 11 compatibility
- [ ] Run installer as Administrator
- [ ] Complete automatic installation
- [ ] Restart computer
- [ ] Test interactive mode
- [ ] Configure TouchDesigner (optional)
- [ ] Setup hotkeys and voice commands
- [ ] Customize privacy settings
- [ ] Run diagnostics to verify installation
- [ ] Explore example commands and automation

**Welcome to the future of AI companions! 🚀**

*Lumora - Where artificial intelligence becomes your perfect digital companion.*