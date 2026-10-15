# LumaHUD

LumaHUD is a native macOS prototype for Lumora's screen-selection HUD. It displays a floating cyan HUD, opens a transparent lasso overlay, captures the selected screen region with ScreenCaptureKit, and keeps the resulting JPEG in memory for a later pipeline stage. It does not write the captured image to disk.

## Shortcuts

- `Option+Space`: show the HUD
- `Option+Shift+L`: start a lasso selection
- `Control+Option+Shift+L`: backup shortcut to start a lasso selection
- `Escape`: cancel an active selection

## macOS permissions

- **Screen Recording** is required to capture the selected screen region. Grant it to LumaHUD in System Settings and restart the app if macOS reports that access is missing.
- **Input Monitoring** may be needed for the global keyboard shortcuts, as noted by the current app implementation. If the shortcuts do not register, check the permission in System Settings and relaunch.
- The current source does not use Accessibility APIs.

## Build and run

Requires macOS 13 or later and Swift 5.9 or later. From this directory:

```sh
swift build
swift run LumaHUD
```

The package uses AppKit, SwiftUI, Carbon, ScreenCaptureKit, ImageIO, and UniformTypeIdentifiers from the macOS SDK. No external package dependencies or signing credentials are required to build it.

## Known unverified

- Live global shortcut behavior has not been verified on the target Mac.
- Live lasso-to-ScreenCaptureKit capture behavior has not been verified end to end.

A successful build only checks compilation; it does not grant macOS permissions or verify runtime interaction.
