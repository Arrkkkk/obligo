plugins {
    java
    id("org.springframework.boot") version "3.3.4"
    id("io.spring.dependency-management") version "1.1.6"
}

group = "dev.obligo"
version = "0.1.0"

java {
    toolchain {
        languageVersion = JavaLanguageVersion.of(21)
    }
}

repositories {
    mavenCentral()
}

val otelAgent by configurations.creating

dependencies {
    implementation("org.springframework.boot:spring-boot-starter-web")
    implementation("org.springframework.boot:spring-boot-starter-jdbc")
    implementation("org.springframework.boot:spring-boot-starter-aop")
    implementation("org.flywaydb:flyway-core")
    implementation("org.flywaydb:flyway-database-postgresql")
    runtimeOnly("org.postgresql:postgresql")
    testImplementation("org.springframework.boot:spring-boot-starter-test")

    otelAgent("io.opentelemetry.javaagent:opentelemetry-javaagent:2.30.0")
}

tasks.withType<Test> {
    useJUnitPlatform()
    // Pins the pool to a single physical connection so the tenant-isolation
    // test can prove isolation holds even when HikariCP hands the same
    // connection to two different tenant contexts (the §10.9 pooling trap).
    environment("DATABASE_MAX_POOL_SIZE", "1")
}

tasks.named<org.springframework.boot.gradle.tasks.run.BootRun>("bootRun") {
    jvmArgs = listOf("-javaagent:${otelAgent.singleFile}")
    environment("OTEL_SERVICE_NAME", "core")
    environment("OTEL_TRACES_EXPORTER", "logging")
    environment("OTEL_METRICS_EXPORTER", "none")
    environment("OTEL_LOGS_EXPORTER", "none")
}
