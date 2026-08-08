package dev.obligo.core.platform.segmentation;

import org.springframework.context.annotation.Condition;
import org.springframework.context.annotation.ConditionContext;
import org.springframework.core.type.AnnotatedTypeMetadata;
import org.springframework.util.StringUtils;

/** Same pattern as document's SupabaseCredentialsPresentCondition -- gates a @Bean, not a hand-rolled null check. */
class BrainServiceTokenPresentCondition implements Condition {

    @Override
    public boolean matches(ConditionContext context, AnnotatedTypeMetadata metadata) {
        return StringUtils.hasText(System.getenv("BRAIN_SERVICE_TOKEN"));
    }
}
