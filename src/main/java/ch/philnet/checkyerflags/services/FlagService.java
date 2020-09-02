package ch.philnet.checkyerflags.services;

import org.jsoup.Jsoup;
import org.jsoup.nodes.Document;
import org.jsoup.select.Elements;

import java.io.IOException;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class FlagService {

    public long getFlagCountForUser(long userId) throws Exception {
        if(userId <= -1)
            throw new Exception(String.format("Invalid user id '%d' supplied", userId));
        
        Document doc = null;
        try {
            doc = Jsoup.connect(String.format("https://stackoverflow.com/users/%d?tab=topactivity", userId)).get();
        } catch (IOException e) {
            throw new Exception(String.format("Could not obtain user page for user with id %d", userId));
        }

        //Get "x posts edited, y helpful flags..." part of document
        Elements stats = doc.select(".grid--cell.mt-auto.fc-black-350.fs-caption.lh-sm .grid.gs4.fd-column");
        //Parse out flag value
        try {
            Pattern pattern = Pattern.compile("\\d{1,3}(,\\d{3})*(\\,\\d+)?\shelpful\sflags");
            Matcher matcher = pattern.matcher(stats.get(0).text());
            String flagsText = "";

            while(matcher.find()) {
                flagsText = matcher.group(0);
            }

            String flagCount = flagsText.strip().replaceAll("(?i)(,|\shelpful\sflags)", "");
            return Integer.parseInt(flagCount);
        } catch (NumberFormatException e) {
            throw new Exception("Encountered non-numeric flag value");
        }

    }
}
