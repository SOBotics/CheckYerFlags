package ch.philnet.checkyerflags.services;

import com.google.gson.JsonObject;
import org.slf4j.Logger;
import ch.philnet.checkyerflags.utils.JsonUtils;
import java.io.IOException;

public class ApiService {

    private final String site = "stackoverflow";
    private final String baseUrl = "https://api.stackexchange.com/2.2";
    private String apiKey;
    private Logger logger;
    private static int quota = 0;

    public ApiService(String apiKey, Logger logger){
        this.apiKey = apiKey;
        this.logger = logger;
    }

    public int getQuota(){
        return quota;
    }

    public JsonObject getUser(long userId) {
        try {
            JsonObject usersData = JsonUtils.get(String.format("%s/users/%d", baseUrl, userId), "order", "desc", "sort", "reputation", "site", site, "key", apiKey);
            JsonUtils.handleBackoff(usersData);
            quota = usersData.get("quota_remaining").getAsInt();
            JsonObject user = usersData.getAsJsonArray("items").get(0).getAsJsonObject();
            return user;
        } catch (IOException e) {
            logger.error("Failed to get user information from SE API: " + e.getMessage());
            return null;
        }
    }

    public String getUserName(long userId) {
        JsonObject user = getUser(userId);
        if (user != null) {
            return user.get("display_name").getAsString();
        } else {
            return "";
        }
    }
}