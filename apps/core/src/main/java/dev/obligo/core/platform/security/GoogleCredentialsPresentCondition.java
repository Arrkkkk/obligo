package dev.obligo.core.platform.security;

import org.springframework.context.annotation.Condition;
import org.springframework.context.annotation.ConditionContext;
import org.springframework.core.type.AnnotatedTypeMetadata;
import org.springframework.util.StringUtils;

class GoogleCredentialsPresentCondition implements Condition {

    @Override
    public boolean matches(ConditionContext context, AnnotatedTypeMetadata metadata) {
        return StringUtils.hasText(System.getenv("GOOGLE_CLIENT_ID"))
                && StringUtils.hasText(System.getenv("GOOGLE_CLIENT_SECRET"));
    }
}
