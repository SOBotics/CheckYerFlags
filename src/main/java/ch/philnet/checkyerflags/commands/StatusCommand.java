package ch.philnet.checkyerflags.commands;

import org.slf4j.Logger;
import org.sobotics.chatexchange.chat.Room;
import org.sobotics.chatexchange.chat.event.PingMessageEvent;

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
    public void run(long messageId, PingMessageEvent event) {
        logger.info("Reporting system status");
        room.send(String.format("    uptime       %s\n    location     %s\n    api quota    %s\s", this.getUptime(), location, getQuota()));
    }

    private String getUptime() {
        long uptimeMillis = System.currentTimeMillis() - this.startTime;
        return formatUptime(uptimeMillis);
    }

    private int getQuota() {
        int quota = apiService.getQuota();
        if (quota == 0) {
            apiService.getUser(1);
            quota = apiService.getQuota();
        }
        return quota;
    }

    private String formatUptime(long duration) {
        int ms, s, m, h, d;
        double dec;
        double time = duration * 1.0;
    
        time = (time / 1000.0);
        dec = time % 1;
        time = time - dec;
        ms = (int)(dec * 1000);
    
        time = (time / 60.0);
        dec = time % 1;
        time = time - dec;
        s = (int)(dec * 60);
    
        time = (time / 60.0);
        dec = time % 1;
        time = time - dec;
        m = (int)(dec * 60);
    
        time = (time / 24.0);
        dec = time % 1;
        time = time - dec;
        h = (int)(dec * 24);
        
        d = (int)time;
        
        return (String.format("%02dd %02dh %02dm %02ds", d, h, m, s));
    }
}
