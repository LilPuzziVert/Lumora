import AppKit
import SwiftUI
import os

@MainActor
@main
struct LumaHUDMain {
    private static var retainedDelegate: AppDelegate?

    static func main() {
        let application = NSApplication.shared
        application.setActivationPolicy(.accessory)
        let delegate = AppDelegate()
        retainedDelegate = delegate
        application.delegate = delegate
        application.run()
    }
}

@MainActor
final class AppDelegate: NSObject, NSApplicationDelegate {
    private let model = AssistantModel()
    private let screenCapture = ScreenCaptureService()
    private var hudController: HUDPanelController!
    private var lassoController: LassoOverlayController!
    private var hotkeys: GlobalHotkeyMonitor!
    private var hasStarted = false
    private var automaticTerminationDisabled = false
    private let automaticTerminationReason = "LumaHUD global shortcuts are active"
    private static let lifecycleLogger = Logger(
        subsystem: "com.heyclicity.lumahud.prototype",
        category: "Lifecycle"
    )

    func applicationDidFinishLaunching(_ notification: Notification) {
        start()
    }

    func start() {
        guard !hasStarted else { return }
        hasStarted = true
        let processInfo = ProcessInfo.processInfo
        processInfo.automaticTerminationSupportEnabled = true
        processInfo.disableAutomaticTermination(automaticTerminationReason)
        automaticTerminationDisabled = true
        Self.lifecycleLogger.info(
            "Automatic termination opted out while global shortcuts are active"
        )
        NSApp.setActivationPolicy(.accessory)
        hudController = HUDPanelController(model: model) { [weak self] in
            self?.beginLasso()
        }
        lassoController = LassoOverlayController { [weak self] orej in
            self?.finishLasso(with: rect)
        }
        hotkeys = GlobalHotkeyMonitor(
            showHUD: { [weak self] in self?.showHUD() },
            startLasso: { [weak self] in self?.beginLasso() },
            cancel: { [weak self] in self?.cancelLasso() },
            onDiagnosticsChanged: { [weak self] message, isFailure in
                self?.model.shortcutDiagnostics = message
                self?.model.shortcutDiagnosticsFailed = isFailure
            },
            onShortcutReceived: { [weak self] shortcut in
                self?.model.lastShortcutReceived = shortcut
            }
        )
        hotkeys.start()
    }

    func applicationShouldTerminateAfterLastWindowClosed(_ sender: NSApplication) -> Bool {
        false
    }

    func applicationWillTerminate(_ notification: Notification) {
        hotkeys.stop()
        if automaticTerminationDisabled {
            ProcessInfo.processInfo.enableAutomaticTermination(automaticTerminationReason)
            automaticTerminationDisabled = false
        }
    }

    private func showHUD() {
        hotkeys.setLassoCancellationEnabled(false)
        lassoController.hide()
        hudController.showNearPointer()
    }

    private func beginLasso() {
        hotkeys.setLassoCancellationEnabled(true)
        hudController.hide()
        model.status = "Drag around an area to select it"
        lassoController.show()
    }

    private func finishLasso(with rect: CGRect) {
        hotkeys.setLassoCancellationEnabled(false)
        lassoController.hide()
        model.lastSelection = rect
        model.lastCapturedJPEG = nil
        model.status = "Capturing selected area…"

        Task { [weak self] in
            guard let self else { return }
            do {
                let crop = try await screenCapture.captureJPEG(in: rect)
                model.lastCapturedJPEG = crop.jpegData
                let sizeKB = max(1, crop.jpegData.count / 1_024)
                model.status = "Crop ready · \(crop.pixelWidth) × \(crop.pixelHeight) · \(sizeKB) KB JPEG"
            } catch {
                if let captureFailure = error as? ScreenCaptureFailure {
                    model.status = captureFailure.localizedDescription
                } else {
                    model.status = "Capture failed · allow Screen Recording for LumaHUD and retry"
                }
                ScreenCaptureService.logFailure(error)
            }
            hudController.showNearPointer()
        }
    }

    private func cancelLasso() {
        guard lassoController.isVisible else { return }
        hotkeys.setLassoCancellationEnabled(false)
        lassoController.hide()
        model.status = "Selection cancelled"
        hudController.showNearPointer()
    }
}

@MainActor
final class AssistantModel: ObservableObject {
    @Published var status = "Ready — Option+Space"
    @Published var shortcutDiagnostics = "Checking shortcuts…"
    @Published var shortcutDiagnosticsFailed = false
    @Published var lastShortcutReceived: String?
    @Published var lastSelection: CGRect?
    @Published var lastCapturedJPEG = nil
    @Published var isHUDVisible = false
}
