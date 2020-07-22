package ch.philnet.checkyerflags;

import java.io.*;
import java.util.ArrayList;
import java.util.HashMap;
import org.slf4j.Logger;

public class TagListReader {
    private Logger logger;

    public TagListReader(Logger logger) {
        this.logger = logger;
    }

    public HashMap<String, String[]> readTagList() {
        String currentMainTag = "";
        ArrayList<String> childTags = new ArrayList<String>();
        HashMap<String, String[]> tags = new HashMap<String, String[]>();
        try (BufferedReader br = new BufferedReader(new FileReader("data" + File.separator + "tags.yaml"))) {
            String line;
            while ((line = br.readLine()) != null) {
               if (line.startsWith("  - ")) {
                   String childTag = line.replace("  - ", "");
                   childTags.add(childTag);
               } else {
                   if (childTags.size() > 0) {
                       tags.put(currentMainTag, childTags.toArray(new String[0]));
                       //Clear child tags array
                       childTags.removeAll(childTags);
                   }
                   currentMainTag = line.replace(":", "");
               }
            }
        } catch(FileNotFoundException fnf) {
            logger.error("Failed to read tag list, file does not exist!");

        } catch(IOException io) {
            logger.error("IOException while reading tag list!");
        }

        return tags;
    }
}
