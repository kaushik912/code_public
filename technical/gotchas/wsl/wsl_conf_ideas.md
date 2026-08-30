**1. Default (No Isolation)**

* **`/etc/wsl.conf` Configuration:** Default / no changes
* **Permissions:** Full read/write access to `C:\` and full ability to execute Windows `.exe` files.
* **Best For:** Maximum convenience when developing across Windows and Linux environments.

**2. Read-Only Automount (Balanced)**

* **`/etc/wsl.conf` Configuration:**
```ini
[automount]
enabled = true
options = "ro"

```


* **Permissions:** Read-only access to `C:\` (cannot modify Windows files); Windows executables can still run unless interop is disabled.
* **Best For:** Safe workspace for untrusted scripts/AI agents while preserving read access to Windows files.

**3. Full Lockdown (Complete Sandbox)**

* **`/etc/wsl.conf` Configuration:**
```ini
[interop]
enabled = false

[automount]
enabled = false

```


* **Permissions:** Disables `C:\` drive mounting and blocks execution of Windows binaries.
* **Best For:** High-security sandboxing when complete separation from the Windows host is required.

*(Note: Run `wsl --shutdown` in PowerShell after editing `/etc/wsl.conf` to apply changes.)*