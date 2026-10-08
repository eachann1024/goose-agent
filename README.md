# Goose Agent

macOS workspace for Goose Agent, a native terminal UI for local and remote coding-agent sessions.

## Demo

https://github.com/user-attachments/assets/4138898f-bf27-426a-b87d-7f23280178ae

## Remote devices

Devices can be reached over SSH, or over a Tailcat (WireGuard/DERP) tunnel.

- **SSH** uses your OpenSSH config/agent and needs nothing extra on the remote Mac beyond a running gooseagent.
- **Tailcat** client code is in this repo: the add-device flow, Keychain token storage, and an embedded tunnel bridge (`Packages/GooseTailcat`, built on [tailscale/tailcat](https://github.com/tailscale/tailcat)). It only carries the gooseagent socket, so standalone shells and the Files workspace still need SSH. It has not been verified end to end in this repository.
- **The remote end is not part of this repo.** A Tailcat device needs the third-party gooseagent plugin [`lbr77/gooseagent-plugin-tailcat`](https://github.com/lbr77/gooseagent-plugin-tailcat) (`gooseagent plugin install lbr77/gooseagent-plugin-tailcat`) installed on the remote host to expose the `gooseagent.tailcat` socket and issue the token. That plugin is not maintained here, and its repository could not be opened anonymously when this was written, so the plugin's availability is not guaranteed.

## Local build

Requires macOS, Xcode, and XcodeGen. Generate the project and build a debug app with:

```sh
make build
```

The app uses bundle identifier `dev.eachann.gooseagent`; the Finder-visible app name is **Goose Agent**.

## Sidebar

In Priority sessions, New Space appears before New Terminal. Available agents enabled in Settings appear directly below New Terminal in the configured order; choosing one opens it in the current space or asks for a space when none is selected. The sidebar scrolls with the session list when these shortcuts exceed the window height.

## License

MIT © 2026 eachann1024, see [LICENSE](LICENSE). Third-party code under `UsageHelper/vendor/` and bundled binary artifacts under `Packages/` keep their own licenses.
