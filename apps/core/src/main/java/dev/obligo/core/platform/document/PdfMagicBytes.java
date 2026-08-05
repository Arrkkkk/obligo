package dev.obligo.core.platform.document;

/** §11.6: MIME by magic bytes, never by the client's declared Content-Type or filename extension. */
final class PdfMagicBytes {

    private static final byte[] PDF_SIGNATURE = {'%', 'P', 'D', 'F', '-'};

    private PdfMagicBytes() {}

    static boolean isPdf(byte[] firstBytes) {
        if (firstBytes == null || firstBytes.length < PDF_SIGNATURE.length) {
            return false;
        }
        for (int i = 0; i < PDF_SIGNATURE.length; i++) {
            if (firstBytes[i] != PDF_SIGNATURE[i]) {
                return false;
            }
        }
        return true;
    }
}
