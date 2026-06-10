# OctoEverywhere Host Patch

This integration is an unsupported local patch for an existing Klipper
OctoEverywhere checkout. It is intended for hosts where:

- the main OctoEverywhere printer portal still serves Mainsail or Fluidd
- `Shared Connection` URLs are not desired for KlipperAI
- KlipperAI is already installed locally and reachable behind nginx at `/klipperai/`

What the patch does:

- extends OctoEverywhere's Moonraker-side relative-path router so requests for
  `/klipperai` and `/klipperai/...` are forwarded directly to the local KlipperAI
  backend on `127.0.0.1:8811`
- patches OctoEverywhere's injected frontend helper so the `KlipperAI` nav item
  bypasses the Mainsail SPA/router and can open KlipperAI in either the current
  tab or a new tab

What it does not do:

- it does not patch Mainsail itself
- it does not add a second officially supported frontend to OctoEverywhere
- it does not keep the OctoEverywhere checkout clean while the route is active;
  the optional update hook temporarily removes only KlipperAI's marked blocks
  when Moonraker reports a pending OE update

## Assumptions

- OctoEverywhere checkout path: `/home/<service-user>/octoeverywhere`
  or, on rooted Creality Nebula Pad-style layouts, `/usr/data/octoeverywhere`
- KlipperAI backend port: `8811`
- KlipperAI public prefix: `/klipperai`

If your host differs, pass explicit arguments to the helper script.

If `install.sh` detects an OctoEverywhere checkout, it can offer to run this
helper automatically.

## Apply

From the KlipperAI checkout on the host:

```bash
chmod +x integrations/octoeverywhere/apply-local-klipperai-route-patch.sh
./integrations/octoeverywhere/apply-local-klipperai-route-patch.sh \
  --oe-root /home/<service-user>/octoeverywhere \
  --restart-service
```

Rooted Creality Nebula Pad example:

```bash
./integrations/octoeverywhere/apply-local-klipperai-route-patch.sh \
  --oe-root /usr/data/octoeverywhere \
  --restart-service
```

Optional flags:

- `--klipperai-prefix /klipperai`
- `--klipperai-port 8811`
- `--nav-target _blank`
- `--service octoeverywhere`

The script writes timestamped backups under
`/etc/klipperai/octoeverywhere-backups` so the OctoEverywhere git checkout does
not get extra untracked backup files.

## Automatic Update Coordination

Install the systemd path/timer hook to coordinate Moonraker-managed OE updates:

```bash
sh integrations/octoeverywhere/install-auto-reapply.sh \
  --oe-root /home/biqu/octoeverywhere \
  --klipperai-prefix /klipperai \
  --klipperai-port 8811 \
  --nav-target _blank \
  --service octoeverywhere
```

The hook:

- checks Moonraker's `octoeverywhere` update-manager state
- removes only KlipperAI's marked blocks when OE has pending commits
- leaves unrelated local changes in the two OE files intact
- refreshes Moonraker so the checkout can become updateable
- watches the patched files and reapplies KlipperAI after the OE update
- runs a five-minute fallback timer in case no file event is emitted
- moves legacy `*.klippyai-backup-*` files out of the OE checkout and into
  `/etc/klipperai/octoeverywhere-backups/legacy`

Installed artifacts:

- `/usr/local/bin/klipperai-octoeverywhere-reapply`
- `/etc/systemd/system/klipperai-octoeverywhere-reapply.service`
- `/etc/systemd/system/klipperai-octoeverywhere-reapply.timer`
- `/etc/systemd/system/klipperai-octoeverywhere-reapply.path`

## Updating OctoEverywhere

With the automatic hook installed, refresh Moonraker updates and wait for the
hook to remove the patch before clicking `Update`. Manual preparation remains
available:

```bash
sh integrations/octoeverywhere/apply-local-klipperai-route-patch.sh \
  --oe-root /home/biqu/octoeverywhere \
  --restore-original \
  --restart-service \
  --service octoeverywhere
```

The restore operation removes the marked KlipperAI blocks rather than resetting
the whole files from git. After the OE update, the path/timer hook reapplies the
patch. Manual reapplication remains available:

```bash
sh integrations/octoeverywhere/apply-local-klipperai-route-patch.sh \
  --oe-root /home/biqu/octoeverywhere \
  --klipperai-prefix /klipperai \
  --klipperai-port 8811 \
  --nav-target _blank \
  --restart-service \
  --service octoeverywhere
```

Reapplying removes the auto-reapply suspend marker.

## Verify

After the script restarts OctoEverywhere:

1. hard-refresh the OctoEverywhere printer portal
2. open `https://<printer>.octoeverywhere.com/klipperai/`
3. click the `KlipperAI` navigation entry from the OE-hosted Mainsail sidebar

If the browser still serves cached Mainsail shell content on the first try,
repeat the test in an incognito window.

## Rollback

Run the patch helper with `--restore-original`, then restart the OctoEverywhere
service again. The script also writes timestamped backups under
`/etc/klipperai/octoeverywhere-backups`.

## Maintenance

This patch targets OctoEverywhere's source layout as of June 2026. The automatic
hook logs a failed reapplication instead of resetting upstream files if these
anchors change:

- `moonraker_octoeverywhere/moonrakerapirouter.py`
- `moonraker_octoeverywhere/static/oe-ui.js`
