package ch.philnet.checkyerflags.commands;

import org.sobotics.chatexchange.chat.Room;
import org.sobotics.chatexchange.chat.event.PingMessageEvent;

import ch.philnet.checkyerflags.services.ApiService;
import ch.philnet.checkyerflags.utils.MessageHandler;

public class QuotaCommand extends Command {
    private ApiService apiService;

    public QuotaCommand(Room chatRoom, MessageHandler msgHandler, ApiService api) {
        //Allowed Patters:
        // quota
        commandPattern = "(?i)(quota)";
        room = chatRoom;
        messageHandler = msgHandler;
        this.apiService = api;
    }

    @Override
    public boolean testCommandPattern(String command) {
        return super.testCommandPattern(command);
    }

    @Override
    public void run(long messageId, PingMessageEvent event) {
        messageHandler.info("Replying to quota command");
        room.replyTo(messageId, "Remaining API quota: " + this.getQuota());
    }

    private int getQuota() {
        int quota = apiService.getQuota();
        if (quota == 0) {
            apiService.getUser(1);
            quota = apiService.getQuota();
        }
        return quota;
    }
}
