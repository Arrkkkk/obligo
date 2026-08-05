package dev.obligo.core.platform.document;

import org.apache.pdfbox.pdmodel.PDDocument;
import org.apache.pdfbox.pdmodel.PDDocumentCatalog;
import org.apache.pdfbox.pdmodel.PDPage;
import org.apache.pdfbox.pdmodel.PDPageContentStream;
import org.apache.pdfbox.pdmodel.interactive.action.PDActionJavaScript;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.UncheckedIOException;

/**
 * PDFBox-generated fixtures -- guarantees the bytes are genuinely
 * PDFBox-parseable (unlike a hand-written "%PDF-1.4\n..." string, which
 * passes magic-byte sniffing but isn't a structurally valid PDF PDFBox's
 * own loader can round-trip, as the first run of these tests discovered
 * the hard way).
 */
final class PdfTestFixtures {

    private PdfTestFixtures() {}

    static byte[] validPdf() {
        try (PDDocument document = new PDDocument()) {
            PDPage page = new PDPage();
            document.addPage(page);
            // No text: showText() requires setFont() first, and font setup
            // adds nothing this fixture needs -- a filled rectangle proves
            // the document has a real, parseable content stream just as well.
            try (PDPageContentStream contentStream = new PDPageContentStream(document, page)) {
                contentStream.addRect(72, 700, 100, 20);
                contentStream.fill();
            }
            return toBytes(document);
        } catch (IOException e) {
            throw new UncheckedIOException(e);
        }
    }

    static byte[] pdfWithEmbeddedJavaScript() {
        try (PDDocument document = new PDDocument()) {
            document.addPage(new PDPage());
            PDDocumentCatalog catalog = document.getDocumentCatalog();
            catalog.setOpenAction(new PDActionJavaScript("app.alert('obligo-test');"));
            return toBytes(document);
        } catch (IOException e) {
            throw new UncheckedIOException(e);
        }
    }

    /**
     * A content stream of ~300,000 repeated, identical operator pairs --
     * highly compressible (Flate) so the on-disk size stays small while the
     * decoded size is large, tripping PdfStructuralValidator's 200:1
     * expansion-ratio cap. compress=true is NOT the default for
     * PDPageContentStream (confirmed against source before writing this) --
     * without it, on-disk size would roughly equal decoded size and this
     * fixture would never actually trip the ratio check.
     */
    static byte[] decompressionBombPdf() {
        try (PDDocument document = new PDDocument()) {
            PDPage page = new PDPage();
            document.addPage(page);
            try (PDPageContentStream contentStream =
                    new PDPageContentStream(document, page, PDPageContentStream.AppendMode.OVERWRITE, true)) {
                for (int i = 0; i < 300_000; i++) {
                    contentStream.moveTo(1, 1);
                    contentStream.lineTo(2, 2);
                }
                contentStream.stroke();
            }
            return toBytes(document);
        } catch (IOException e) {
            throw new UncheckedIOException(e);
        }
    }

    private static byte[] toBytes(PDDocument document) throws IOException {
        ByteArrayOutputStream out = new ByteArrayOutputStream();
        document.save(out);
        return out.toByteArray();
    }
}
