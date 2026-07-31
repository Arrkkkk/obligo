# Development

This doc is built up incrementally, one setup step at a time, as each part of Phase 1 lands. It is not a complete guide yet.

**On timing:** the "clean clone to all three services running" target assumes Java 21, Gradle, uv, and Node/npm are already installed. First-time `brew install` of those, plus cold downloads of the Gradle distribution, Maven dependencies, and npm packages, add real time on top of the steps below — budget more than the steps alone suggest if this is a genuinely new machine.

## Prerequisites

### Java 21 (apps/core)

`apps/core` requires Java 21 and is built with Gradle via the `./gradlew` wrapper.

If you're on macOS with Homebrew and don't already have a JDK 21:

```bash
brew install openjdk@21
```

Homebrew installs it keg-only (it won't override your default `java` on `PATH` if you have a different version linked). Point Gradle at it directly so `./gradlew` works without exporting `JAVA_HOME` every session, by adding this to your **user-level** `~/.gradle/gradle.properties`, not the project's (a hardcoded per-machine path doesn't belong in a file that's committed and shared with CI):

```properties
org.gradle.java.home=/opt/homebrew/opt/openjdk@21
```

```bash
mkdir -p ~/.gradle
echo 'org.gradle.java.home=/opt/homebrew/opt/openjdk@21' >> ~/.gradle/gradle.properties
```

**If that path doesn't exist on your machine** (different OS, different chip architecture, or a different install method — e.g. sdkman, jenv, Intel Mac using `/usr/local` instead of `/opt/homebrew`), find your actual JDK 21 path and use that instead. CI doesn't need any of this — `.github/workflows/ci-core.yml` installs its own JDK 21 via `actions/setup-java` and picks it up from the environment, since there's no project-level override to conflict with it.

Verify it's working:

```bash
./gradlew :apps:core:compileJava
```

This should succeed without you setting `JAVA_HOME` in your shell.

### Running apps/core locally

`apps/core` connects to Neon Postgres using `DATABASE_URL` from `.env`. Copy `.env.example` to `.env` and fill in the real values (Neon connection string, Upstash REST URL/token — `.env.example` has comments on where to get each). Source `.env` into your shell before running:

```bash
cp .env.example .env  # first time only — then fill in real values
set -a; source .env; set +a
./gradlew :apps:core:bootRun
```

Then check:

```bash
curl http://localhost:8080/healthz
```

**At this point, with only `core` running, expect this — and it's correct:**

```json
{"status":"down","database":"reachable","brain":"unreachable","brainError":null}
```

HTTP 503. `core`'s `/healthz` also checks `brain` (see below), so it can't return a clean `"ok"` until `brain` is up too — `database: reachable` is the part this step is actually verifying. The full green response comes once all three services are running together; see "Running all three together" below.

### Python 3.12 + uv (apps/brain)

`apps/brain` uses [uv](https://docs.astral.sh/uv/) for dependency management (a uv workspace rooted at the repo root — see the root `pyproject.toml`).

```bash
brew install uv
uv python install 3.12
```

Run it:

```bash
uv run --project apps/brain uvicorn obligo_brain.main:app --app-dir apps/brain/src --port 8000
curl http://localhost:8000/healthz
# {"status":"ok"}
```

### Node 22 + npm (apps/web)

`apps/web` is a standard Next.js 15 app — if `node`/`npm` are already on your `PATH`, no extra setup is needed.

```bash
cd apps/web
npm install
npm run dev
# http://localhost:3000
```

## Running all three together, with tracing

Each service needs to know where the next one in the chain lives. Defaults assume all three running locally on their standard ports (`web` 3000, `core` 8080, `brain` 8000), but set these explicitly to be safe:

| Service | Env var | Default |
| :--- | :--- | :--- |
| `core` | `BRAIN_URL` | `http://localhost:8000` |
| `web` | `CORE_URL` | `http://localhost:8080` |

Start all three (three terminals, in order — `brain`, then `core`, then `web`):

```bash
# terminal 1
uv run --project apps/brain uvicorn obligo_brain.main:app --app-dir apps/brain/src --port 8000

# terminal 2
set -a; source .env; set +a
export BRAIN_URL=http://localhost:8000
./gradlew :apps:core:bootRun

# terminal 3
cd apps/web
export CORE_URL=http://localhost:8080
npm run dev
```

`GET web:/api/healthz` calls `core:/healthz`, which calls `brain:/healthz` — one request, three services, one trace. Hit it and watch:

```bash
curl http://localhost:3000/api/healthz
# {"status":"ok","core":{"status":"ok","database":"reachable","brain":"reachable"}}
```

All three services currently export OpenTelemetry traces to their own console/log output (no collector or backend running locally yet — see `OBLIGO_ENGINEERING_BLUEPRINT.md` §18.1: the full LGTM backend is `[PROD]`, profile-gated so `make dev` stays light, even in later phases). To verify a request produced one connected trace, grep each service's log for the same `trace_id`/`traceId` and check the parent/child span IDs line up across the web → core → brain hops.

- `core`: the OTel Java agent (`-javaagent`, auto-instrumentation) is attached via a Gradle `otelAgent` configuration in `apps/core/build.gradle.kts` — no code changes needed for HTTP/JDBC spans.
- `brain`: `opentelemetry-instrumentation-fastapi`, wired in `apps/brain/src/obligo_brain/platform/otel.py`.
- `web`: `@vercel/otel` in `apps/web/instrumentation.ts` — not the raw `@opentelemetry/sdk-node` package, because Next's `instrumentation.ts` webpack bundling pass can't resolve the Node builtins (`stream`, `path`, `diagnostics_channel`, ...) that the raw instrumentation packages need at import time. `@vercel/otel` wraps the same underlying SDK in a form that survives that bundling pass.
