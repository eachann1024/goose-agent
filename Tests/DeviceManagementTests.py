#!/usr/bin/env python3
"""Regression: python3 Tests/DeviceManagementTests.py (requires Swift)."""
from pathlib import Path
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
app = (root / "Sources/GooseAgent/AppModel.swift").read_text()
device = (root / "Packages/GooseKit/Sources/GooseKit/Device.swift").read_text()
discovery = (root / "Packages/GooseKit/Sources/GooseKit/GooseSessionDiscovery.swift").read_text()
sidebar = (root / "Sources/GooseAgent/SidebarView.swift").read_text()
content = (root / "Sources/GooseAgent/ContentView.swift").read_text()


def block(source, marker):
    start = source.index(marker)
    brace = source.index("{", start)
    depth = 0
    for index in range(brace, len(source)):
        if source[index] == "{":
            depth += 1
        elif source[index] == "}":
            depth -= 1
            if depth == 0:
                return source[start:index + 1]
    raise AssertionError(f"unclosed Swift block: {marker}")


add_local = block(app, "func addLocalDevice(")
update = block(app, "func updateDevice(")
remove = block(app, "func removeDevice(")
refresh_named = block(app, "func refreshNamedSessions()")
disconnect = block(app, "func disconnectDevice(")
edit_sheet = block(content, "struct EditDeviceSheet:")
device_actions = block(sidebar, "private func deviceActions(")

# Backend/API and transactional guarantees.
assert "@discardableResult" in app[app.index(add_local) - 40:app.index(add_local)]
assert "socketPath: String) -> Bool" in add_local
assert "@discardableResult" in app[app.index(update) - 40:app.index(update)]
assert "socketPath: String = \"\"" in update and "tailcatToken: String = \"\"" in update
assert "case .local:" in update and "case .ssh:" in update and "case .tailcat:" in update
assert "updated[index].kind = .ssh" not in update[update.index("case .tailcat:"):]
assert "if !token.isEmpty" in update and "TailcatCredentialStore.token(for: id)" in update
assert "catch" in update and "error.localizedDescription" in update
assert "try TailcatCredentialStore.setToken(previousTailcatToken, for: id)" in update
assert "NSString(string: path).expandingTildeInPath" in app
assert "path.hasPrefix(\"/\") || path.hasPrefix(\"~/\")" in app
assert "!target.hasPrefix(\"-\")" in app
assert "persistDevices(updated)" in add_local and add_local.index("persistDevices(updated)") < add_local.index("devices = updated")
assert "persistDevices(updated)" in update and update.index("persistDevices(updated)") < update.index("devices = updated")
assert "persistDevices(updated)" in remove and remove.index("persistDevices(updated)") < remove.index("removeSSHPassword")
assert "knownIDs.contains(device.id.uuidString)" in remove and "hiddenNamedDevicesKey" in remove
assert "let existingIDs = Set(devices.map(\\.id))" in refresh_named
assert "let persistedIDs = Set(store.load().map(\\.id))" in refresh_named
assert "!persistedIDs.contains(device.id)" in refresh_named
assert "filter { !hiddenIDs.contains($0.id.uuidString) }" in refresh_named
assert "guard !device.isLocal" not in remove and "guard !device.isLocal" not in disconnect
assert "socketPath == nil && !devices.contains(where: { $0.id == Device.local.id })" in add_local

# UI acceptance checks are intentionally read-only: main-thread UI work is out of scope.
assert ".contextMenu { deviceActions(device) }" in sidebar
assert "Menu {\n                        deviceActions(device)" in sidebar
assert 'Button("Remove", role: .destructive)' in sidebar and "model.removeDevice(device)" in sidebar
assert 'alert(\n            "Remove Connection?"' in sidebar
assert "private func deviceActions(_ device: Device)" in device_actions
assert "case .local:" in edit_sheet and "case .tailcat:" in edit_sheet
assert "socketPath: socketPath" in edit_sheet and "tailcatToken: token" in edit_sheet

existing_id_line = next(line.strip() for line in refresh_named.splitlines()
                        if "let existingIDs = Set(devices.map" in line)
hidden_block = block(remove, "if knownIDs.contains(device.id.uuidString)")
hidden_block = hidden_block.replace("Self.hiddenNamedDevicesKey", '"device.hiddenNamedSessions"')
refresh_filter_start = refresh_named.index("        let hiddenIDs = Set(defaults.stringArray(forKey: Self.hiddenNamedDevicesKey) ?? [])")
refresh_filter_end = refresh_named.index("        let discoveredIDs =", refresh_filter_start)
refresh_filter = refresh_named[refresh_filter_start:refresh_filter_end].replace(
    "Self.hiddenNamedDevicesKey", '"device.hiddenNamedSessions"'
).strip()

harness = r'''
import Foundation
let defaults = UserDefaults(suiteName: "device-management-" + UUID().uuidString)!
let hiddenKey = "device.hiddenNamedSessions"
let knownKey = "device.knownNamedSessions"
struct Validation {
''' + block(app, "private func validatedDeviceName(").replace("private func", "func") + "\n" + block(app, "private func validatedSocketPath(").replace("private func", "func") + "\n" + block(app, "private func validatedSSHTarget(").replace("private func", "func") + r'''
}
let validation = Validation()
assert(validation.validatedSocketPath("") != nil && validation.validatedSocketPath("")! == nil)
assert(validation.validatedSocketPath("relative.sock") == nil)
assert(validation.validatedSocketPath("~/.config/gooseagent/custom.sock")!! == NSString(string: "~/.config/gooseagent/custom.sock").expandingTildeInPath)
assert(validation.validatedSocketPath("/tmp/custom.sock")!! == "/tmp/custom.sock")
assert(validation.validatedSSHTarget("-oProxyCommand=bad") == nil)
assert(validation.validatedSSHTarget("user@host\ncommand") == nil)
assert(validation.validatedSSHTarget(" user@host ") == "user@host")

let directory = FileManager.default.temporaryDirectory.appendingPathComponent(UUID().uuidString)
let store = DeviceStore(directory: directory)
assert(store.load().map(\.id) == [Device.local.id])
let custom = Device(name: "Custom local", kind: .local, socketPath: "/tmp/custom.sock")
assert(!custom.isNamedSession, "custom local socket must not be auto-discovery")
assert(store.persist([custom]))
assert(store.load() == [custom], "local customization survives reload")
assert(store.persist([]) && store.load().isEmpty, "an intentionally empty list stays empty")
let blocker = directory.appendingPathComponent("not-a-directory")
try Data("file".utf8).write(to: blocker)
assert(!DeviceStore(directory: blocker).persist([custom]), "persistence failures are reported")

let sessionPath = URL(fileURLWithPath: NSHomeDirectory()).appendingPathComponent(".config/gooseagent/sessions/work/gooseagent.sock").path
let session = GooseSessionDiscovery.NamedSession(name: "work", socketPath: sessionPath)
let discoveredDevice = GooseSessionDiscovery.device(for: session)
var devices = [discoveredDevice]
var allDiscovered = [discoveredDevice]
let known = Set(allDiscovered.map { $0.id.uuidString })
defaults.set(known.sorted(), forKey: knownKey)
let renamed = Device(id: discoveredDevice.id, name: "Renamed work", kind: .local, socketPath: "/tmp/renamed.sock")
assert(discoveredDevice.isNamedSession && !renamed.isNamedSession, "renamed or endpoint-edited discovery becomes a persistent custom device")
devices[0] = renamed
''' + existing_id_line + r'''
assert(existingIDs.contains(discoveredDevice.id), "renamed discovered device is not duplicated on refresh")
let device = renamed
let knownIDs = Set(defaults.stringArray(forKey: knownKey) ?? [])
''' + hidden_block + r'''
let defaults = UserDefaults.standard
''' + refresh_filter + r'''
assert(!discovered.contains(where: { $0.id == device.id }), "removed renamed discovery does not revive")
print("PASS: device persistence, validation, discovery identity, UI contract and removal regression")
'''
# `defaults` shadowing in the extracted fragment is not needed; keep the isolated suite.
harness = harness.replace('let defaults = UserDefaults.standard\n', '')

with tempfile.TemporaryDirectory(prefix="device-management-") as directory:
    swift = Path(directory) / "main.swift"
    binary = Path(directory) / "check"
    swift.write_text(harness)
    subprocess.run([
        "swiftc",
        str(root / "Packages/GooseKit/Sources/GooseKit/Device.swift"),
        str(root / "Packages/GooseKit/Sources/GooseKit/GooseSessionDiscovery.swift"),
        str(swift), "-o", str(binary),
    ], check=True)
    subprocess.run([str(binary)], check=True)
