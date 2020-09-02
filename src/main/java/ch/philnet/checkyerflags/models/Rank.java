package ch.philnet.checkyerflags.models;

public class Rank {
    private long flagCount;
    private String title;
    private String description;

    public Rank(long flagCount, String title, String description) {
        this.flagCount = flagCount;
        this.title = title;
        this.description = description;
    }

    public long getFlagCount() {
        return this.flagCount;
    }

    public String getTitle() {
        return this.title;
    }

    public String getDescription() {
        return this.description;
    }
}
