# Development

This doc is built up incrementally, one setup step at a time, as each part of Phase 1 lands. It is not a complete guide yet.

## Prerequisites

### Java 21 (apps/core)

`apps/core` requires Java 21 and is built with Gradle via the `./gradlew` wrapper.

If you're on macOS with Homebrew and don't already have a JDK 21:

```bash
brew install openjdk@21
```

Homebrew installs it keg-only (it won't override your default `java` on `PATH` if you have a different version linked). The project's `gradle.properties` points Gradle directly at the Homebrew keg path so `./gradlew` works without you having to export `JAVA_HOME` yourself:

```properties
org.gradle.java.home=/opt/homebrew/opt/openjdk@21
```

**If that path doesn't exist on your machine** (different OS, different chip architecture, or a different install method — e.g. sdkman, jenv, Intel Mac using `/usr/local` instead of `/opt/homebrew`), find your actual JDK 21 path and either:
- update `org.gradle.java.home` in `gradle.properties` to match, or
- delete that line and export `JAVA_HOME` yourself before running `./gradlew`.

Verify it's working:

```bash
./gradlew :apps:core:compileJava
```

This should succeed without you setting `JAVA_HOME` in your shell.

### Running apps/core locally

`apps/core` connects to Neon Postgres using `DATABASE_URL` from `.env` (see `.env.example` — get the real values from whoever set up the Neon project). Source `.env` into your shell before running:

```bash
set -a; source .env; set +a
./gradlew :apps:core:bootRun
```

Then check:

```bash
curl http://localhost:8080/healthz
# {"status":"ok","database":"reachable"}
```
