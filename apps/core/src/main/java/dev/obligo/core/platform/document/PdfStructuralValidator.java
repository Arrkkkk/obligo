package dev.obligo.core.platform.document;

import org.apache.pdfbox.Loader;
import org.apache.pdfbox.cos.COSBase;
import org.apache.pdfbox.cos.COSDictionary;
import org.apache.pdfbox.cos.COSDocument;
import org.apache.pdfbox.cos.COSName;
import org.apache.pdfbox.cos.COSObjectKey;
import org.apache.pdfbox.cos.COSStream;
import org.apache.pdfbox.pdmodel.PDDocument;

import java.io.IOException;
import java.io.InputStream;
import java.time.Duration;
import java.util.Optional;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;
import java.util.concurrent.atomic.AtomicLong;

/**
 * §11.6 structural checks beyond magic-byte sniffing: active-content
 * rejection (embedded JavaScript, launch actions, embedded files) and the
 * decompression-bomb guard (page count, expansion ratio, hard timeout) --
 * confirmed to be one guard with three components per blueprint's own
 * wording ("page count cap (500), expansion ratio cap, and a hard timeout
 * on parsing"), not two separate checks.
 *
 * Active-content detection is a flat scan of every indirect object in the
 * file's xref table (COSDocument.getXrefTable()/getObjectFromPool()),
 * rather than walking the high-level tree (OpenAction, per-page actions,
 * per-annotation A/AA, AcroForm field triggers). Every action, wherever
 * it's referenced from in the document, ultimately exists as an indirect
 * object that shows up in this scan -- so this is both simpler and more
 * exhaustive than enumerating tree locations one by one, and isn't fooled
 * by an action dictionary that omits the (often-optional-in-practice)
 * /Type /Action key.
 *
 * The expansion-ratio check reads each stream's DECODED bytes in bounded
 * chunks, checking the running total against both caps after every chunk
 * and aborting the instant either is crossed -- so measuring the ratio
 * never itself buffers a real bomb to completion.
 *
 * Runs on a plain platform-thread executor (not virtual threads): this is
 * CPU-bound work (parsing, inflate decompression), not blocking I/O, which
 * is the case virtual threads are actually cheap for.
 *
 * Known, accepted gap (see CLAUDE.md): this runs a third-party parser
 * against untrusted, potentially-malicious bytes directly inside the main
 * Spring process. Blueprint §11.6 calls for this to happen in an isolated
 * worker with no network egress and a read-only filesystem, which doesn't
 * exist yet. The timeout below is the only mitigation this class has
 * against a parser-level DoS; there is no isolation against a parser-level
 * memory-safety issue.
 */
class PdfStructuralValidator {

    static final int MAX_PAGES = 500;
    static final long MAX_DECODED_BYTES = 500L * 1024 * 1024;
    static final int EXPANSION_RATIO_CAP = 200;
    static final Duration TIMEOUT = Duration.ofSeconds(10);

    private static final int READ_CHUNK_SIZE = 65536;
    private static final COSName LAUNCH = COSName.getPDFName("Launch");

    /** Empty if the PDF passes every check; otherwise a human-readable reason for rejection. */
    Optional<String> findViolation(byte[] pdfBytes, long declaredFileSize) {
        try (ExecutorService executor = Executors.newSingleThreadExecutor()) {
            Future<Optional<String>> future = executor.submit(() -> checkSync(pdfBytes, declaredFileSize));
            try {
                return future.get(TIMEOUT.toSeconds(), TimeUnit.SECONDS);
            } catch (TimeoutException e) {
                future.cancel(true);
                return Optional.of("PDF structural validation timed out after " + TIMEOUT.toSeconds() + "s");
            } catch (ExecutionException e) {
                return Optional.of("PDF could not be parsed: " + rootMessage(e.getCause()));
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                return Optional.of("PDF structural validation was interrupted");
            }
        }
    }

    private Optional<String> checkSync(byte[] pdfBytes, long declaredFileSize) throws IOException {
        try (PDDocument document = Loader.loadPDF(pdfBytes)) {
            if (document.getNumberOfPages() > MAX_PAGES) {
                return Optional.of(
                        "page count (%d) exceeds the %d-page cap".formatted(document.getNumberOfPages(), MAX_PAGES));
            }

            COSDocument cosDocument = document.getDocument();
            AtomicLong decodedBytesTotal = new AtomicLong();
            byte[] chunk = new byte[READ_CHUNK_SIZE];

            for (COSObjectKey key : cosDocument.getXrefTable().keySet()) {
                if (Thread.currentThread().isInterrupted()) {
                    throw new IOException("cancelled");
                }

                COSBase base = cosDocument.getObjectFromPool(key).getObject();
                if (!(base instanceof COSDictionary dict)) {
                    continue;
                }

                Optional<String> activeContent = activeContentViolation(dict);
                if (activeContent.isPresent()) {
                    return activeContent;
                }

                if (dict instanceof COSStream stream) {
                    Optional<String> bomb = checkStreamForBomb(stream, chunk, decodedBytesTotal, declaredFileSize);
                    if (bomb.isPresent()) {
                        return bomb;
                    }
                }
            }
            return Optional.empty();
        }
    }

    private Optional<String> activeContentViolation(COSDictionary dict) {
        COSName subtype = dict.getCOSName(COSName.S);
        if (COSName.JAVA_SCRIPT.equals(subtype)) {
            return Optional.of("embedded JavaScript action detected");
        }
        if (LAUNCH.equals(subtype)) {
            return Optional.of("embedded launch action detected");
        }
        if (dict.containsKey(COSName.JS)) {
            return Optional.of("embedded JavaScript detected");
        }
        if (COSName.EMBEDDED_FILE.equals(dict.getCOSName(COSName.TYPE))) {
            return Optional.of("embedded file attachment detected");
        }
        return Optional.empty();
    }

    private Optional<String> checkStreamForBomb(
            COSStream stream, byte[] chunk, AtomicLong decodedBytesTotal, long declaredFileSize) throws IOException {
        try (InputStream decoded = stream.createInputStream()) {
            int read;
            while ((read = decoded.read(chunk)) != -1) {
                if (Thread.currentThread().isInterrupted()) {
                    throw new IOException("cancelled");
                }
                long total = decodedBytesTotal.addAndGet(read);
                if (total > MAX_DECODED_BYTES || total > declaredFileSize * (long) EXPANSION_RATIO_CAP) {
                    return Optional.of(
                            "decompression-bomb guard tripped: decoded content exceeds the %dMB absolute cap or the %dx expansion-ratio cap"
                                    .formatted(MAX_DECODED_BYTES / (1024 * 1024), EXPANSION_RATIO_CAP));
                }
            }
        }
        return Optional.empty();
    }

    private String rootMessage(Throwable t) {
        Throwable cause = t;
        while (cause.getCause() != null) {
            cause = cause.getCause();
        }
        return cause.getMessage() != null ? cause.getMessage() : cause.getClass().getSimpleName();
    }
}
