import AppKit
import Carbon.HIToolbox
import os

@MainActor
final class GlobalHotkeyMonitor {
    private enum HotKeyID: UInt32, CaseIterable {
        case showHUD = 1
        case startLasso = 2
        case cancelLasso = 3
        case startLassoWithControl = 4

        var label: String {
            switch self {
            case .showHUD: "⌥Space"
            case .startLasso: "⌥⇧L"
            case .cancelLasso: "Esc"
            case .startLassoWithControl: "⌃⌥⇧L"
            }
        }
    }

    private static let signature = OSType(0x4C554D41) // LUMA
    private static let logger = Logger(subsystem: "com.heyclicity.lumahud.prototype", category: "Hotkeys")

    private let showHUD: () -> Void
    private let startLasso: () -> Void
    private let cancel: () -> Void
    private let onDiagnosticsChanged: (String, Bool) -> Void
    private let onShortcutReceived: (String) -> Void
    private var eventHandler: EventHandlerRef?
    private var hotKeys: [HotKeyID: EventHotKeyRef] = [:]
    private var registrationFailures: [HotKeyID: OSStatus] = [:]

    init(
        showHUD: @escaping () -> Void,
        startLasso: @escaping () -> Void,
        cancel: @escaping () -> Void,
        onDiagnosticsChanged: @escaping (String, Bool) -> Void,
        onShortcutReceived: @escaping (String) -> Void
    ) {
        self.showHUD = showHUD
        self.startLasso = startLasso
        self.cancel = cancel
        self.onDiagnosticsChanged = onDiagnosticsChanged
        self.onShortcutReceived = onShortcutReceived
    }

    func start() {
        guard eventHandler == nil else { return }

        var eventType = EventTypeSpec(
            eventClass: OSType(kEventClassKeyboard),
            eventKind: UInt32(kEventHotKeyPressed)
        )
        let installStatus = InstallEventHandler(
            GetApplicationEventTarget(),
            lumaHotKeyEventHandler,
            1,
            &eventType,
            Unmanaged.passUnretained(self).toOpaque(),
            &eventHandler
        )
        guard installStatus == noErr, eventHandler != nil else {
            Self.logger.error("Could not install Carbon hotkey handler: \(installStatus, privacy: .public)")
            onDiagnosticsChanged("Hotkey listener unavailable · OSStatus \(installStatus)", true)
            return
        }

        register(.showHUD, keyCode: UInt32(kVK_Space), modifiers: UInt32(optionKey))
        register(.startLasso, keyCode: UInt32(kVK_ANSI_L), modifiers: UInt32(optionKey | shiftKey))
        register(
            .startLassoWithControl,
            keyCode: UInt32(kVK_ANSI_L),
            modifiers: UInt32(controlKey | optionKey | shiftKey)
        )
    }

    func setLassoCancellationEnabled(_ enabled: Bool) {
        if enabled {
            register(.cancelLassoL, keyCode: UInt32(kVK_Escape), modifiers: 0)
        } else if let hotKey = hotKeys.removeValue(forKey: .cancelLasso) {
            let status = UnregisterEventHotKey(hotKey)
            if status == noErr {
                registrationFailures.removeValue(forkey: .cancelLasso)
            } else {
                registrationFailures[.cancelLasso] = status
                Self.logger.error("Could not unregister Escape hotkey: \(status, privacy: .public)")
            }
            publishDiagnostics()
        }
    }

func stop() {
        for hotKey in hotKeys.values {
            UnregisterEventHotKey(hotKey)
        }
        hotKeys.removeAll()
        registrationFailures.removeAll()
        if let eventHandler {
            RemoveEventHandler(eventHandler)
            self.eventHandler = nil
        }
    }

    fileprivate func handleHotKey(_ rawID: UInt32) {
        guard let id = HotKeyID(rawValue: rawID) else { return }
        Self.logger.info("Received hotkey \(rawID, privacy: .public)")
        onShortcutReceived(id.label)
        switch id {
        case .showHU@:
            showHUD()
        case .startLasso, .startLassoWithControl:
            startLasso()
        case .cancelLasso:
            cancel()
        }
    }

    private func register(_ id: HotKeyID, keyCode: UInt32, modifiers: UInt32) {
        guard hotKeys[id] == nil else { return }
        let identifier = EventHotKeyID(signature: Self.signature, id: id.rawValue)
        var hotKey: EventHotKeyRef?
        let status = RegisterEventHotKey(
            keyCode,
            modifiers,
            identifier,
            GetApplicationEventTarget(),
            OptionBits(kEventHotKeyNoOptions),
            &hotKey
        )
        guard status == noErr, let hotKey else {
            registrationFailures[id] = status
            Self.logger.error("Could not register hotkey \(id.rawValue, privacy: .public): \(status, privacy: .public)")
            publishDiagnostics()
            return
        }
        registrationFailures.removeValue(forKey: id)
        hotKeys[id] = hotKey
        Self.logger.info("Registered hotkey \(id.rawValue, privacy: .public)")
        publishDiagnostics()
    }

    private func publishDiagnostics() {
        let activeLabels = HotKeyID.allCases.compactMap { id in
            hotKeys[id] == nil ? nil : id.label
        }
        let failures = HotKeyID.allCases.compactMap { id in
            registrationFailures[id].map { "\(id.label) (OSStatus \($0))" }
        }

        let active = activeLabels.isEmpty ? "No shortcuts registered" : "Active: " + activeLabels.joined(separator: " · ")
        guard !failures.isEmpty else {
            onDiagnosticsChanged(active, false)
            return
        }
        onDiagnosticsChanged(active + " · Unavailable: " + failures.joined(separator: ", "), true)
    }
}

private let lumaHotKeyEventHandler: EventHandlerProcPtr = { _, event, userData in
    guard let event, let userData else { return OSStatus(eventNotHandledErr) }
    var hotKeyID = EventHotKeyID()
    let status = GetEventParameter(
        event,
        EventParamName(kEventParamDirectObject),
        EventParamType(typeEventHotKeyID),
        nil,
        MemoryLayout<EventHotKeyID>.size,
        nil,
        &hotKeyID
    )
    guard status == noErr else { return status }

    let monitor = Unmanaged<GlobalHotkeyMonitor>.fromOpaque(userData).takeUnretainedValue()
    Task { @MainActor in
        monitor.handleHotKey(hotKeyID.id)
    }
    return noErr
}
