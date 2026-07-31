SHELL := /bin/bash
DEV_LOG_DIR := tmp/dev-logs

.PHONY: dev dev-stop test seed demo

# Starts brain, core, web natively (no Docker — see CLAUDE.md), each
# backgrounded with its own log file. Mirrors docs/DEVELOPMENT.md's
# "Running all three together" section exactly.
dev:
	@mkdir -p $(DEV_LOG_DIR)
	@if [ ! -f .env ]; then \
		echo "No .env found. Copy .env.example to .env and fill in real values first."; \
		exit 1; \
	fi
	@echo "Starting brain, core, web in the background — logs in $(DEV_LOG_DIR)/"
	@nohup bash -c 'set -a; . ./.env; set +a; \
		exec uv run --project apps/brain uvicorn obligo_brain.main:app --app-dir apps/brain/src --port 8000' \
		> $(DEV_LOG_DIR)/brain.log 2>&1 & echo $$! > $(DEV_LOG_DIR)/brain.pid
	@nohup bash -c 'set -a; . ./.env; set +a; \
		export BRAIN_URL=http://localhost:8000; \
		exec ./gradlew :apps:core:bootRun' \
		> $(DEV_LOG_DIR)/core.log 2>&1 & echo $$! > $(DEV_LOG_DIR)/core.pid
	@nohup bash -c 'export CORE_URL=http://localhost:8080; \
		exec npm --prefix apps/web run dev' \
		> $(DEV_LOG_DIR)/web.log 2>&1 & echo $$! > $(DEV_LOG_DIR)/web.pid
	@echo ""
	@echo "brain:  http://localhost:8000/healthz      (log: $(DEV_LOG_DIR)/brain.log)"
	@echo "core:   http://localhost:8080/healthz      (log: $(DEV_LOG_DIR)/core.log)"
	@echo "web:    http://localhost:3000/api/healthz  (log: $(DEV_LOG_DIR)/web.log)"
	@echo ""
	@echo "Give them a few seconds to start (core in particular), then curl the URLs above."
	@echo "Run 'make dev-stop' when you're done."

# Stops whatever `make dev` started, using the PID files it wrote.
dev-stop:
	@for svc in brain core web; do \
		pidfile=$(DEV_LOG_DIR)/$$svc.pid; \
		if [ -f $$pidfile ]; then \
			pid=$$(cat $$pidfile); \
			if kill -0 $$pid 2>/dev/null; then \
				echo "Stopping $$svc (pid $$pid)"; \
				kill $$pid 2>/dev/null; \
			else \
				echo "$$svc (pid $$pid) already stopped"; \
			fi; \
			rm -f $$pidfile; \
		else \
			echo "$$svc: no pidfile, nothing to stop"; \
		fi; \
	done

# Runs each service's test suite. Mirrors the three CI workflows exactly,
# so a green `make test` locally should mean green CI.
test:
	@echo "== apps/core: ./gradlew test =="
	./gradlew test
	@echo "== apps/brain: pytest =="
	uv run --project apps/brain pytest
	@echo "== apps/web: no test suite yet (Phase 6 adds Playwright/vitest per the blueprint) — lint + build, matching ci-web.yml =="
	npm --prefix apps/web run lint
	npm --prefix apps/web run build

# No data model exists yet to seed — obligations, documents, etc. land in
# Phase 3 (ingestion) and Phase 5 (obligation domain). See
# OBLIGO_ENGINEERING_BLUEPRINT.md §21.
seed:
	@echo "make seed: not implemented yet. No data model exists until Phase 3+ (see OBLIGO_ENGINEERING_BLUEPRINT.md §21)."

# No demo script exists yet — the real demo (obligation board, source
# split view, planted conflict) lands in Phase 6 (MVP release). See
# OBLIGO_ENGINEERING_BLUEPRINT.md §21.
demo:
	@echo "make demo: not implemented yet. The demo script lands in Phase 6 / MVP release (see OBLIGO_ENGINEERING_BLUEPRINT.md §21)."
