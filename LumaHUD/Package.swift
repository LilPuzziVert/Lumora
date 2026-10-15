// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "LumaHUD",
    platforms: [.macOS(.v13)],
    products: [
        .executable(name: "LumaHUD", targets: ["LumaHUD"])
    ],
    targets: [
        .executableTarget(
            name: "LumaHUD",
            path: "Sources/LumaHUD",
            linkerSettings: [
                .linkedFramework("AppKit"),
                .linkedFramework("Carbon"),
                .linkedFramework("ScreenCaptureKit"),
                .linkedFramework("ImageIO"),
                .linkedFramework("UniformTypeIdentifiers")
            ]
        )
    ]
)
