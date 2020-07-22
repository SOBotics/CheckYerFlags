package ch.philnet.checkyerflags.commands;

import org.slf4j.Logger;
import org.sobotics.chatexchange.chat.Room;

import ch.philnet.checkyerflags.services.ApiService;

public class StatusCommand extends Command {
    private long startTime;
    private String location;
    private ApiService apiService;

    public StatusCommand(Room chatRoom, Logger commandLogger, long startTime, String location, ApiService api) {
        //Allowed Patters:
        // alive
        commandPattern = "(?i)(status)";
        room = chatRoom;
        logger = commandLogger;
        this.startTime = startTime;
        this.location = location;
        this.apiService = api;
    }

    @Override
    public boolean testCommandPattern(String command) {
        return super.testCommandPattern(command);
    }

    @Override
    public void run(long messageId) {
        logger.info("Reporting system status");
        room.send(String.format("    uptime       %s\n    location     %s\n    api quota    %s\s", this.getUptime(), location, getQuota()));
    }

    private String getUptime() {
        long uptimeMillis = (System.currentTimeMillis() - this.startTime) / 1000;
        //TODO: Fix calculation of this
        return String.format("%dd %02dh %02ds", uptimeMillis / 3600, (uptimeMillis % 3600) / 60, (uptimeMillis % 60));
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
