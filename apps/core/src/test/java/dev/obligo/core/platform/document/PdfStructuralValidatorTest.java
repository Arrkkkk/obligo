package dev.obligo.core.platform.document;

import org.junit.jupiter.api.Test;

import java.nio.charset.StandardCharsets;

import static org.assertj.core.api.Assertions.assertThat;

/**
 * Fast, pure unit coverage of PdfStructuralValidator's own logic -- no DB,
 * no Supabase, no Spring context. SourceUploadFlowTest complements this
 * with the smaller set of real-infrastructure end-to-end proofs the user
 * asked for (embedded-JS PDF, bomb PDF, tampered hash), run through the
 * actual commit() flow against real Supabase Storage.
 */
class PdfStructuralValidatorTest {

    private final PdfStructuralValidator validator = new PdfStructuralValidator();

    @Test
    void acceptsAnOrdinaryValidPdf() {
        byte[] pdf = PdfTestFixtures.validPdf();

        assertThat(validator.findViolation(pdf, pdf.length)).isEmpty();
    }

    @Test
    void rejectsEmbeddedJavaScript() {
        byte[] pdf = PdfTestFixtures.pdfWithEmbeddedJavaScript();

        assertThat(validator.findViolation(pdf, pdf.length))
                .hasValueSatisfying(reason -> assertThat(reason).contains("JavaScript"));
    }

    @Test
    void rejectsADecompressionBomb() {
        byte[] pdf = PdfTestFixtures.decompressionBombPdf();

        assertThat(validator.findViolation(pdf, pdf.length))
                .hasValueSatisfying(reason -> assertThat(reason).contains("decompression-bomb"));
    }

    @Test
    void rejectsContentThatIsNotAStructurallyValidPdf() {
        byte[] garbage = "%PDF-1.4\nthis satisfies magic bytes but is not a real PDF structure\n"
                .getBytes(StandardCharsets.US_ASCII);

        assertThat(validator.findViolation(garbage, garbage.length))
                .hasValueSatisfying(reason -> assertThat(reason).contains("could not be parsed"));
    }
}
