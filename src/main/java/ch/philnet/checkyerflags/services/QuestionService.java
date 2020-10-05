package ch.philnet.checkyerflags.services;

import ch.philnet.checkyerflags.TagListReader;
import ch.philnet.checkyerflags.utils.MessageHandler;
import ch.philnet.checkyerflags.utils.Utils;
import com.neovisionaries.ws.client.*;
import com.rollbar.notifier.Rollbar;
import com.rollbar.notifier.config.Config;

import org.json.JSONArray;
import org.json.JSONObject;
import org.slf4j.LoggerFactory;
import org.sobotics.chatexchange.chat.Room;

import java.io.IOException;
import java.util.*;

/**
 * Monitor the site for new questions and analyze tags
 */
public class QuestionService {
    private String missingParentTag = "";
    private ArrayList<Long> checkedPosts = new ArrayList<>();
    private MessageHandler messageHandler;
    private HashMap<String, String[]> watchedTags;

    public void run(Room chatRoom, Config config) {
        this.messageHandler = new MessageHandler(LoggerFactory.getLogger(QuestionService.class), new Rollbar(config));
        this.watchedTags = new TagListReader(this.messageHandler).readTagList();

        try {
            this.messageHandler.info("(QuestionService): Connecting to Websocket...");
            new WebSocketFactory()
                    .createSocket("wss://qa.sockets.stackexchange.com/")
                    .addListener(new WebSocketAdapter() {
                        @Override
                        public void onConnected(WebSocket websocket, Map<String, List<String>> headers) throws Exception {
                            messageHandler.info("(QuestionService): Successfully connected to Websocket, listening for new posts.");
                        }
                    })
                    .addListener(new WebSocketAdapter() {
                        @Override
                        public void onDisconnected(WebSocket websocket, WebSocketFrame serverCloseFrame, WebSocketFrame clientCloseFrame, boolean closedByServer) throws Exception {
                            messageHandler.warning(new Exception("(QuestionService): Disconnected from the socket."));
                        }
                    })
                    .addListener(new WebSocketAdapter() {
                        @Override
                        public void onTextMessage(WebSocket websocket, String text) throws Exception {
                            //Respond to heartbeat
                            if (new JSONObject(text).get("action").toString().equals("hb")){
                                websocket.sendText("pong");
                                return;
                            }

                            //Parse JSON string to object
                            JSONObject question = new JSONObject(new JSONObject(text).get("data").toString());

                            //Check if it's a question from Stack Overflow and not some other site
                            //We need to do this since the single-site websocket doesn't work for SO
                            if (question.getString("siteBaseHostAddress").equals("stackoverflow.com")) {
                                JSONArray tags = question.getJSONArray("tags");
                                //Skip already checked posts
                                if (checkedPosts.contains(question.getLong("id")))
                                    return;
                                if (hasMissingTags(Utils.jsonArrayToStringList(tags), question.getLong("id"))) {
                                    //Decode question title
                                    String questionTitle = org.jsoup.parser.Parser.unescapeEntities(question.getString("titleEncodedFancy"), true);
                                    messageHandler.info("(QuestionService): Detected missing tags in question " + question.getString("url"));
                                    String tagList = "[tag:" + String.join("] [tag:", Utils.jsonArrayToStringList(tags)) + "]";
                                    String parentTag = "[tag:" + missingParentTag + "]";
                                    chatRoom.send(String.format("[ [CheckYerFlags](https://stackapps.com/q/7792) ] %s Missing parent tag %s: [%s](%s)", tagList, parentTag, questionTitle, question.getString("url")));
                                }
                            }
                        }
                    })
                    .connect()
                    .sendText("155-questions-active");
        } catch (IOException | WebSocketException e) {
            e.printStackTrace();
        }
    }

    private boolean hasMissingTags(List<String> questionTags, long questionId) {
        for (HashMap.Entry<String, String[]> watchedTag : this.watchedTags.entrySet()) {
            String parentTag = watchedTag.getKey();
            for (String watchedChildTag : watchedTag.getValue()) {
                //Check if child tag found and parent tag not found
                if (questionTags.contains(watchedChildTag) && !questionTags.contains(parentTag)) {
                    missingParentTag = parentTag;
                    if (checkedPosts.size() >= 100)
                        checkedPosts.clear();
                    checkedPosts.add(questionId);
                    return true;
                }
            }
        }
        //No missing child tag found
        return false;
    }

}
