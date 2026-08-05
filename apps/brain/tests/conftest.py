import os

# Mirrors apps/core/build.gradle.kts's `environment("DATABASE_MAX_POOL_SIZE",
# "1")` for the test JVM: pin apps/brain's engine to a single physical
# connection for the whole pytest session, so tests that need to prove
# "same physical connection, different tenant contexts" (see
# test_tenant_isolation.py) can assert that property is guaranteed, not
# merely likely. get_engine() is a lazy singleton, so this only has effect
# if it's set before the first call -- setdefault() at collection time,
# before any test module imports obligo_brain.platform.tenancy.db,
# satisfies that.
os.environ.setdefault("DATABASE_MAX_POOL_SIZE", "1")
