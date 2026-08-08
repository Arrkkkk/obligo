package dev.obligo.core.platform.segmentation;

/** apps/brain unreachable, or returned something outside its documented contract. The caller maps this to a 503. */
public class BrainClientUnavailableException extends RuntimeException {

    public BrainClientUnavailableException(String message) {
        super(message);
    }

    public BrainClientUnavailableException(String message, Throwable cause) {
        super(message, cause);
    }
}
