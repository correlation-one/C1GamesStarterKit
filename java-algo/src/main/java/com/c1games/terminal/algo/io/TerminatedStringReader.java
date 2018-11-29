package com.c1games.terminal.algo.io;


import java.io.IOException;
import java.io.InputStream;

/**
 * A reader of framed strings from an inputstream.
 */
public class TerminatedStringReader implements AutoCloseable {
    private final int terminator;
    private final InputStream in;
    private StringBuilder buffer;

    public TerminatedStringReader(InputStream in, char terminator) {
        this.terminator = (int) terminator;
        this.in = in;
        this.buffer = new StringBuilder();
    }

    /**
     * Nullable, non-blocking.
     */
    public String receive() throws IOException {
        boolean terminated = false;
        boolean exausted = false;
        while (!terminated && !exausted) {
            if (in.available() > 0) {
                int b = in.read();
                if (b == -1)
                    throw new IOException("stream closed");
                else if (b == terminator)
                    terminated = true;
                else
                    buffer.append((char) b);
            } else {
                exausted = true;
            }
        }
        if (terminated) {
            String string = buffer.toString();
            buffer = new StringBuilder();
            return string;
        } else {
            return null;
        }
    }

    /**
     * Blocking, non-nullable.
     */
    public String await() throws IOException {
        boolean terminated = false;
        while (!terminated) {
            int b = in.read();
            if (b == -1)
                throw new IOException("stream closed");
            else if (b == terminator)
                terminated = true;
            else
                buffer.append((char) b);
        }
        String string = buffer.toString();
        buffer = new StringBuilder();
        return string;
    }

    /**
     * Nullable, blocking, timeouts.
     */
    public String awaitTimeout(long timeout) throws IOException {
        long start = System.currentTimeMillis();
        long end = start + timeout;

        boolean terminated = false;
        boolean timedout = false;
        while (!terminated && !timedout) {
            long now = System.currentTimeMillis();
            if (in.available() > 0) {
                int b = in.read();
                if (b == terminator)
                    terminated = true;
                else
                    buffer.append((char) b);
            } else if (now < end) {
                // since input stream interface does not have a read with timeout method, we will sleep and poll
                try {
                    Thread.sleep(Math.min(end - now, 5));
                } catch (InterruptedException e) {
                    throw new IOException(e);
                }
            } else {
                timedout = true;
            }
        }
        if (terminated) {
            String string = buffer.toString();
            buffer = new StringBuilder();
            return string;
        } else {
            return null;
        }
    }

    @Override
    public void close() throws Exception {
        in.close();
    }
}
