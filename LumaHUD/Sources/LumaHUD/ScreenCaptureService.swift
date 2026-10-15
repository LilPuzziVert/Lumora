import AppKit
import CoreGraphics
import ImageIO
import ScreenCaptureKit
import UniformTypeIdentifiers
import os

struct CapturedCrop {
    let jpegData: Data
    let pixelWidth: Int
    let pixelHeight: Int
}

enum ScreenCaptureFailure: LocalizedError, Equatable {
    case emptySelection
    case screenRecordingPermissionRequired
    case noMatchingDisplay
    case noCapturedImage
    case imageEncodingFailed
    case unsupportedOperatingSystem

    var errorDescription: String? {
        switch self {
        case .emptySelection:
            return "The selected area is too small to capture."
        case .screenRecordingPermissionRequired:
            return "Enable LumaHUD in System Settings → Privacy & Security → Screen & System Audio Recording. If it is already on, remove the old LumaHUD entry, add this build again, then reopen LumaHUD."
        case .noMatchingDisplay:
            return "The selected area no longer matches an available display."
        case .noCapturedImage:
            return "ScreenCaptureKit returned no image for the selected area."
        case .imageEncodingFailed:
            return "The selected area could not be encoded as JPEG."
        case .unsupportedOperatingSystem:
            return "Screen capture requires macOS 14 or newer."
        }
    }
}

@MainActor
final class ScreenCaptureService {
    private static let logger = Logger(subsystem: "com.heyclicity.lumahud.prototype", category: "ScreenCapture")

    static func logFailure(_ error: Error) {
        logger.error("Screen capture failed: \(error.localizedDescription, privacy: .public)")
    }

    func captureJPEG(in selection: CGRect) async throws -> CapturedCrop {
        guard !selection.isNull, selection.width > 1, selection.height > 1 else {
            throw ScreenCaptureFailure.emptySelection
        }


        guard CGPreflightScreenCaptureAccess() else {
            _ = CGRequestScreenCaptureAccess()
            throw ScreenCaptureFailure.screenCordingPermissionRequired
        }


        let shareableContent = try await SCShareableContent.current
        let matchingDisplay = shareableContent.displays
            .compactMap { display -> (display: SCDisplay, rect: CGRect, area: CGFloat)? in
                let clipped = selection.intersection(display.frame)
                guard !clipped.isNull, clipped.width > 1, clipped.height > 1 else { return nil }
                return (display, clipped, clipped.width * clipped.height)
            }
            .max { $0.area < $1.area }


        guard let matchingDisplay else {
            throw ScreenCaptureFailure.noMatchingDisplay

        let capturedImage: CGImage
        if #available(macOS 26.0, *) {
            capturedImage = try await captureScreenshotRect(matchingDisplay.rect)

        else if #a