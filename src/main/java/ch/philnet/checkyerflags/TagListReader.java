package ch.philnet.checkyerflags;

import java.io.*;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;
import org.slf4j.Logger;

public class TagListReader {
    private Logger logger;

    public TagListReader(Logger logger) {
        this.logger = logger;
    }

    /**
     * @deprecated Use YAML implementation instead
     */
    public HashMap<String, String> readTagListCsv() {
        HashMap<String, String> tags = new HashMap<>();
        String line = "";

        try {
            BufferedReader br = new BufferedReader(new FileReader("." + File.separator + "data" + File.separator + "tags.csv"));
            while((line = br.readLine()) != null) {
                String[] lineTags = line.split(",");
                tags.put(lineTags[0], lineTags[1]);
            }

            br.close();
        } catch (IOException e) {
            e.printStackTrace();
        }

        return tags;
    }

    /**
     * @deprecated This sucks, just don't use it
     */
    public Map<String, String> readTagListYAML() {
        /*Yaml yaml = new Yaml();
        InputStream inputStream = this.getClass()
          .getClassLoader()
          .getResourceAsStream("data" + File.separator + "tags.yaml");
        Map<String, Object> obj = yaml.load(inputStream)*/
        return null;
    }


    public HashMap<String, String[]> readTagList() {
        String currentMainTag = "";
        ArrayList<String> childTags = new ArrayList<String>();
        HashMap<String, String[]> tags = new HashMap<String, String[]>();
        try (BufferedReader br = new BufferedReader(new FileReader("data" + File.separator + "tags.yaml"))) {
            String line;
            while ((line = br.readLine()) != null) {
               if(line.startsWith("  - ")) {
                   String childTag = line.replace("  - ", "");
                   childTags.add(childTag);
               } else {
                   if(childTags.size() > 0) {
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
