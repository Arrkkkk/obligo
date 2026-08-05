package dev.obligo.core.platform.document;

/** Storage unreachable at upload-intent (§11.7) -- the caller maps this to a 503; the client retries. */
public class BlobStoreUnavailableException extends RuntimeException {

    public BlobStoreUnavailableException(String message) {
        super(message);
    }

    public BlobStoreUnavailableException(String message, Throwable cause) {
        super(message, cause);
    }
}
