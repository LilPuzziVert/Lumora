# LUMORA - Full-Access AI OS Companion (v2)

> "Think PowerToys on steroids + Jarvis in RAM." 🧠

## 🌟 Overview

Lumora is a locally-run, OS-integrated, AI-powered super assistant for power users. It lives silently inside your system as an intelligent second brain — no cloud, no hand-holding, no limits. It feels like your OS evolved.

### ✨ Key Features
- 🔍 **System-Wide Monitoring** - Tracks all apps, processes, and user behavior
- 🖥️ **Screen + App Awareness** - Full OCR and accessibility API integration
- 🧠 **Hidden Context Detection** - Understands minimized apps and background processes
- ⌨️ **Input Monitoring** - Learns typing patterns and suggests automations
- 🤖 **Autonomous Interaction** - Can control apps like a human user
- 🧬 **Local AI Intelligence** - Fully offline AI with natural conversation
- 🛡️ **Privacy Controls** - Complete control over monitoring and data
- 🔧 **Self-Diagnostics** - Auto-repair and maintenance capabilities

## 🚀 Quick Start

### Prerequisites
- Windows 11
- Python 3.11+
- Rust (for performance-critical components)
- Administrator privileges

### Installation
```bash
cd Lumora
python scripts/install.py
```

### Usage
1. **Service Mode**: Automatically starts as Windows service
2. **Interactive Mode**: Launch GUI with `python src/main.py`
3. **Voice Mode**: Activate with configured hotkey
4. **Friend Mode**: Casual companion interaction

## 📁 Project Structure
```
Lumora/
├── src/                    # Core application code
├── core/                   # Core engine components
├── ai/                     # AI and ML modules
├── plugins/                # Extensible plugin system
├── services/               # Windows service implementation
├── ui/                     # User interface components
├── data/                   # Data storage and models
├── config/                 # Configuration files
├── scripts/                # Installation and utility scripts
├── tests/                  # Test suite
├── docs/                   # Documentation
└── build/                  # Build artifacts and installers
```

## 🛠️ Architecture

### Core Components
- **Lumora Engine**: Main orchestration and service management
- **Context Manager**: Screen awareness and app monitoring
- **AI Brain**: Local intelligence and decision making
- **Privacy Guardian**: Security and privacy controls
- **Plugin System**: Extensible functionality
- **Memory Bank**: Persistent learning and storage

### Technology Stack
- **Python**: Core application logic (stdlib only)
- **Rust**: Performance-critical system hooks
- **Win32 API**: Deep Windows integration
- **Local AI**: Custom trained models
- **SQLite**: Local data storage

## 🔧 Configuration

Edit `config/settings.yaml` to customize:
- Monitoring preferences
- Privacy settings
- AI behavior
- Plugin configuration
- Service options

## 🧠 AI Capabilities

### Local Intelligence
- Context-aware responses
- Pattern recognition
- Predictive suggestions
- Natural conversation
- Learning from user behavior

### Privacy-First Design
- All processing happens locally
- No data leaves your machine
- Granular privacy controls
- Transparent operation modes

## 🔌 Plugin System

Create custom plugins for:
- New app integrations
- Custom automations
- AI model extensions
- UI enhancements

## 📚 Documentation

- [Installation Guide](docs/installation.md)
- [User Manual](docs/user_guide.md)
- [Developer Guide](docs/developer_guide.md)
- [API Reference](docs/api_reference.md)
- [Plugin Development](docs/plugin_development.md)

## 🤝 Contributing

This is a personal project designed for full self-ownership. See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

MIT License - See [LICENSE](LICENSE) for details.

## 🎯 Roadmap

- [x] Core engine and service implementation
- [x] Screen awareness and OCR
- [x] Basic AI integration
- [x] Privacy controls
- [ ] Advanced automation
- [ ] Voice interface
- [ ] Plugin marketplace
- [ ] Mobile companion app

---

**Lumora**: Your personal AI evolution. Built by you, for you.