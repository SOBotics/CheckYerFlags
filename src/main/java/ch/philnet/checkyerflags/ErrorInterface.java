package ch.philnet.checkyerflags;

public interface ErrorInterface {
    public void error(Exception exception);

    public void error(String message, Exception exception);

    public void warning(Exception exception);
}
