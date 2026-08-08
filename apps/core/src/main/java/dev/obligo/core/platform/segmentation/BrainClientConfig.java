package dev.obligo.core.platform.segmentation;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Conditional;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.client.RestClient;

/**
 * Same @Conditional-not-eager-requireEnv shape as document's BlobStoreConfig
 * -- see that class's javadoc for the full history of why (a requireEnv()
 * call at bean-construction time takes down every test in the module the
 * moment the env var is unset, not just tests that touch this feature).
 * brain.url always has a default (BRAIN_URL, application.yml), so only
 * BRAIN_SERVICE_TOKEN gates this bean's existence.
 */
@Configuration
public class BrainClientConfig {

    @Bean
    @Conditional(BrainServiceTokenPresentCondition.class)
    public BrainClient brainClient(RestClient.Builder restClientBuilder, @Value("${brain.url}") String brainUrl) {
        return new BrainClient(restClientBuilder, brainUrl, System.getenv("BRAIN_SERVICE_TOKEN"));
    }
}
