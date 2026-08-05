package dev.obligo.core.platform.document;

import org.junit.jupiter.api.Test;

import java.nio.charset.StandardCharsets;

import static org.assertj.core.api.Assertions.assertThat;

class PdfMagicBytesTest {

    @Test
    void acceptsRealPdfSignature() {
        assertThat(PdfMagicBytes.isPdf("%PDF-1.4\n...".getBytes(StandardCharsets.US_ASCII)))
                .isTrue();
    }

    @Test
    void rejectsDeclaredMimeTypeMismatch() {
        // The whole point of magic-byte sniffing: content that merely claims
        // to be a PDF (via extension or Content-Type) but isn't one.
        assertThat(PdfMagicBytes.isPdf("plain text pretending\n".getBytes(StandardCharsets.US_ASCII)))
                .isFalse();
    }

    @Test
    void rejectsTruncatedInput() {
        assertThat(PdfMagicBytes.isPdf("%PD".getBytes(StandardCharsets.US_ASCII))).isFalse();
    }

    @Test
    void rejectsEmptyAndNullInput() {
        assertThat(PdfMagicBytes.isPdf(new byte[0])).isFalse();
        assertThat(PdfMagicBytes.isPdf(null)).isFalse();
    }
}
