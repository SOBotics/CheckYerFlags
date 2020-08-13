package ch.philnet.checkyerflags.services;

import com.google.gson.JsonObject;

import ch.philnet.checkyerflags.utils.JsonUtils;
import ch.philnet.checkyerflags.utils.MessageHandler;

import java.io.IOException;

public class ApiService {

    private final String site = "stackoverflow";
    private final String baseUrl = "https://api.stackexchange.com/2.2";
    private String apiKey;
    private MessageHandler messageHandler;
    private static int quota = 0;

    public ApiService(String apiKey, MessageHandler messageHandler){
        this.apiKey = apiKey;
        this.messageHandler = messageHandler;
    }

    public int getQuota(){
        return quota;
    }

    public JsonObject getUser(long userId) {
        try {
            JsonObject usersData = JsonUtils.get(String.format("%s/users/%d", baseUrl, userId), "order", "desc", "sort", "reputation", "site", site, "key", apiKey);
            JsonUtils.handleBackoff(usersData);
            updateQuota(usersData.get("quota_remaining").getAsInt());
            JsonObject user = usersData.getAsJsonArray("items").get(0).getAsJsonObject();
            return user;
        } catch (IOException e) {
            this.messageHandler.error("Failed to get user information from SE API: " + e.getMessage(), e);
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

    private void updateQuota(int newQuota) {
        if (newQuota > quota) {
            this.messageHandler.info(String.format("API quota rolled over at %s", quota));
        }
        quota = newQuota;
    }
}
