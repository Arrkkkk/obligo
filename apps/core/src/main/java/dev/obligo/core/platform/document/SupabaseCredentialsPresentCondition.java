package dev.obligo.core.platform.document;

import org.springframework.context.annotation.Condition;
import org.springframework.context.annotation.ConditionContext;
import org.springframework.core.type.AnnotatedTypeMetadata;
import org.springframework.util.StringUtils;

/** Same pattern as security's GoogleCredentialsPresentCondition -- gates a @Bean, not a hand-rolled null check. */
class SupabaseCredentialsPresentCondition implements Condition {

    @Override
    public boolean matches(ConditionContext context, AnnotatedTypeMetadata metadata) {
        return StringUtils.hasText(System.getenv("SUPABASE_URL"))
                && StringUtils.hasText(System.getenv("SUPABASE_SERVICE_ROLE_KEY"))
                && StringUtils.hasText(System.getenv("SUPABASE_STORAGE_BUCKET"));
    }
}
