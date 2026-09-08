### Install SDKMAN

```bash
curl -s "https://get.sdkman.io" | bash
source "$HOME/.sdkman/bin/sdkman-init.sh"

# verify
sdk version
```

Add-on: hooks itself into `~/.bashrc`/`~/.zshrc` automatically (a `sdkman-init.sh` source line) — no manual PATH edits needed.

### Quick guide: project needs Java 21, you're currently on 17

1. `cd /path/to/your-project`
2. Check what's active: `sdk current java` → shows 17.x
3. See available 21 builds: `sdk list java | grep 21`
4. Install the one you want: `sdk install java 21.0.12-tem` (skip if already installed)
5. Switch it for this shell: `sdk use java 21.0.12-tem`
6. Confirm: `java -version` → should now print 21
7. Pin it for the project: `sdk env init` → writes `.sdkmanrc` with `java=21.0.12-tem` in the current dir
8. Test auto-switch: `cd ..` then `cd -` (back into project) → with `sdkman_auto_env=true`, it auto-prints "Using java version 21.0.12-tem..." and `java -version` confirms 21 again
9. (optional) commit `.sdkmanrc` to the repo

### Enable / disable auto-switch

* **Enable:** set `sdkman_auto_env=true` in `~/.sdkman/etc/config`. Now every `cd` into a folder with a `.sdkmanrc` switches java/gradle/maven for you.
* **Disable:** set it back to `false`. `sdk` commands still work manually, just no auto-switch on `cd`.
* **No `.sdkmanrc` in a folder:** nothing happens — whatever was active before stays active (last project's version, or system default in a fresh shell).

### General useful commands

```bash
sdk current                  # everything active in this shell
sdk current java              # just one candidate
sdk list java                 # available versions/vendors for install
sdk install java 17.0.8-tem    # install a specific build
sdk use java 17.0.8-tem        # switch for current shell only, no file written
sdk default java 17.0.8-tem    # set as the global fallback (new shells with no .sdkmanrc)
sdk env install                # install + activate everything a .sdkmanrc lists
sdk env init                   # generate .sdkmanrc from what's active now
sdk uninstall java 17.0.8-tem   # remove a candidate you no longer need
sdk upgrade                     # check for newer versions of installed candidates
```

### Gotchas

* Version string has a vendor suffix (`-tem` = Temurin, `-amzn` = Corretto, etc.) — pick one, doesn't matter which for a plain app.
* `.sdkmanrc` only pins what it lists — no `gradle=`/`maven=` line means those stay whatever was last active.
* SDKMAN-installed JDKs (`~/.sdkman/candidates/`) are separate from system/apt-installed ones (`/usr/lib/jvm/`) — no conflict, but also no auto-reuse; you install a copy unless you explicitly point SDKMAN at an existing path.
