package ch.philnet.checkyerflags.commands;

import org.slf4j.Logger;
import org.sobotics.chatexchange.chat.Room;

import ch.philnet.checkyerflags.services.ApiService;

public class QuotaCommand extends Command {
    private ApiService apiService;

    public QuotaCommand(Room chatRoom, Logger commandLogger, ApiService api) {
        //Allowed Patters:
        // quota
        commandPattern = "(?i)(quota)";
        room = chatRoom;
        logger = commandLogger;
        this.apiService = api;
    }

    @Override
    public boolean testCommandPattern(String command) {
        return super.testCommandPattern(command);
    }

    @Override
    public void run(long messageId) {
        logger.info("Replying to quota command");
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
