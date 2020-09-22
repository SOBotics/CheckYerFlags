package ch.philnet.checkyerflags;

import java.io.*;
import java.util.ArrayList;
import java.util.HashMap;

import ch.philnet.checkyerflags.utils.MessageHandler;

public class TagListReader {
    private MessageHandler messageHandler;

    public TagListReader(MessageHandler messageHandler) {
        this.messageHandler = messageHandler;
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
            this.messageHandler.error("(TagListReader): Failed to read tag list, file does not exist!", fnf);

        } catch(IOException io) {
            this.messageHandler.error("(TagListReader): IOException while reading tag list!", io);
        } catch(Exception e) {
            this.messageHandler.error("(TagListReader): Unhandled general exception.", e);
        }
        this.messageHandler.info(String.format("(TagListReader): Loaded %d tags.", tags.size()));


        return tags;
    }
}
