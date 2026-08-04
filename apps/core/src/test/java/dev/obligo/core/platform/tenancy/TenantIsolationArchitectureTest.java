package dev.obligo.core.platform.tenancy;

import com.tngtech.archunit.core.domain.JavaClasses;
import com.tngtech.archunit.core.domain.JavaMethod;
import com.tngtech.archunit.core.importer.ClassFileImporter;
import com.tngtech.archunit.core.importer.ImportOption;
import com.tngtech.archunit.lang.ArchCondition;
import com.tngtech.archunit.lang.ArchRule;
import com.tngtech.archunit.lang.SimpleConditionEvent;
import org.junit.jupiter.api.Test;
import org.springframework.transaction.annotation.Transactional;

import javax.sql.DataSource;
import java.sql.Connection;

import static com.tngtech.archunit.core.domain.JavaClass.Predicates.assignableTo;
import static com.tngtech.archunit.lang.syntax.ArchRuleDefinition.methods;
import static com.tngtech.archunit.lang.syntax.ArchRuleDefinition.noFields;

/**
 * Closes the Phase 2 carried-forward gap from blueprint §21/§10.9:
 * "removing the tenant predicate from any repository method fails the
 * build." See {@link TenantScopedRepository}'s Javadoc for exactly what
 * these two rules do and do not prove — in short, they check that the
 * *precondition* for isolation holds (a transaction boundary exists for
 * TenantConnectionPreparer's AOP to intercept, and no field can be used to
 * dodge that boundary), not that isolation itself holds. The actual
 * guarantee is the RLS policy + TenantConnectionPreparer, proved against a
 * real database by TenantIsolationTest.
 *
 * A SQL-text-scanning rule ("query string must contain org_id") would be
 * the wrong mechanism for this codebase: OrganizationRepository.findAll()
 * has no org_id predicate in its SQL at all, by design — RLS filters
 * silently server-side. These rules check structure, not query text.
 */
class TenantIsolationArchitectureTest {

    // DO_NOT_INCLUDE_TESTS: these rules govern production repositories.
    // Test doubles/fixtures living under src/test are out of scope.
    private static final JavaClasses CORE_CLASSES = new ClassFileImporter()
            .withImportOption(ImportOption.Predefined.DO_NOT_INCLUDE_TESTS)
            .importPackages("dev.obligo.core");

    @Test
    void everyMethodOnATenantScopedRepositoryRunsInsideATransaction() {
        ArchRule rule = methods()
                .that()
                .areDeclaredInClassesThat(assignableTo(TenantScopedRepository.class))
                .and()
                .arePublic()
                .should(beAnnotatedWithTransactionalDirectlyOrViaItsClass())
                .because("TenantConnectionPreparer's AOP only fires around @Transactional "
                        + "(@annotation or @within) — a method that skips it never has "
                        + "app.org_id set, so the RLS policy that is this codebase's actual "
                        + "tenant predicate never sees a value to compare against");

        rule.check(CORE_CLASSES);
    }

    @Test
    void tenantScopedRepositoriesCannotHoldARawDataSourceField() {
        ArchRule rule = noFields()
                .that()
                .areDeclaredInClassesThat(assignableTo(TenantScopedRepository.class))
                .should()
                .haveRawType(DataSource.class)
                .because("a raw DataSource field lets a method call getConnection() directly, "
                        + "bypassing DataSourceUtils/the active Spring transaction — the "
                        + "connection TenantConnectionPreparer set app.org_id on. Only "
                        + "JdbcTemplate/NamedParameterJdbcTemplate (transaction-aware) are "
                        + "allowed for tenant-scoped access");

        rule.check(CORE_CLASSES);
    }

    @Test
    void tenantScopedRepositoriesCannotHoldARawConnectionField() {
        ArchRule rule = noFields()
                .that()
                .areDeclaredInClassesThat(assignableTo(TenantScopedRepository.class))
                .should()
                .haveRawType(Connection.class)
                .because("a cached java.sql.Connection field could outlive, or never belong "
                        + "to, the transaction TenantConnectionPreparer set app.org_id on for "
                        + "a given request");

        rule.check(CORE_CLASSES);
    }

    /**
     * Spring honors class-level {@code @Transactional} as applying to every
     * public method, so the ArchUnit check has to match that, not just
     * check the method itself. Every current tenant-scoped repository
     * method uses method-level annotations, but this keeps the rule correct
     * if a future one uses class-level instead.
     */
    private static ArchCondition<JavaMethod> beAnnotatedWithTransactionalDirectlyOrViaItsClass() {
        return new ArchCondition<>("be annotated with @Transactional, directly or via its class") {
            @Override
            public void check(JavaMethod method, com.tngtech.archunit.lang.ConditionEvents events) {
                boolean methodAnnotated = method.isAnnotatedWith(Transactional.class);
                boolean classAnnotated = method.getOwner().isAnnotatedWith(Transactional.class);
                boolean satisfied = methodAnnotated || classAnnotated;

                String message = satisfied
                        ? method.getFullName() + " is annotated with @Transactional"
                        : method.getFullName() + " is declared on a TenantScopedRepository but is not "
                                + "annotated @Transactional, directly or via its class — "
                                + "TenantConnectionPreparer's AOP will not fire for this call";

                events.add(new SimpleConditionEvent(method, satisfied, message));
            }
        };
    }
}
