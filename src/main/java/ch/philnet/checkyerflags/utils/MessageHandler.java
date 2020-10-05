package ch.philnet.checkyerflags.utils;

import com.rollbar.notifier.Rollbar;

import org.slf4j.Logger;

import ch.philnet.checkyerflags.ErrorInterface;

/**
 * Helper class to make reporting errors easier
 */
public final class MessageHandler implements ErrorInterface {
    private final Logger logger;
    private final Rollbar rollbar;

    public MessageHandler(Logger logger, Rollbar rollbar) {
        this.logger = logger;
        this.rollbar = rollbar;
    }

    @Override
    public void error(Exception exception) {
        logger.error(exception.getMessage());
        rollbar.error(exception);
    }

    @Override
    public void error(String message, Exception exception) {
        logger.error(message);
        rollbar.error(exception);
    }

    @Override
    public void warning(Exception exception) {
        logger.warn(exception.getMessage());
        rollbar.warning(exception);
    }

    public void info(String message) {
        logger.info(message);
    }

    public void debug(String message) {
        logger.debug(message);
    }
}
