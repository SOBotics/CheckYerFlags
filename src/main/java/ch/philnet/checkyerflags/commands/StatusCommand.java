package ch.philnet.checkyerflags.commands;

import com.rollbar.notifier.config.Config;

import org.sobotics.chatexchange.chat.Room;
import org.sobotics.chatexchange.chat.event.PingMessageEvent;

import ch.philnet.checkyerflags.services.ApiService;
import ch.philnet.checkyerflags.utils.MessageHandler;

public class StatusCommand extends Command {
    private long startTime;
    private String location;
    private ApiService apiService;
    private Config config;

    public StatusCommand(Room chatRoom, MessageHandler msgHandler, long startTime, String location, ApiService api, Config config) {
        //Allowed Patters:
        // status
        commandPattern = "(?i)(status)";
        room = chatRoom;
        messageHandler = msgHandler;
        this.startTime = startTime;
        this.location = location;
        this.apiService = api;
        this.config = config;
    }

    @Override
    public boolean testCommandPattern(String command) {
        return super.testCommandPattern(command);
    }

    @Override
    public void run(long messageId, PingMessageEvent event) {
        messageHandler.info("(Command): Reporting system status");
        final String nl = System.lineSeparator();
        room.send(String.format("    uptime       %s    version      %s    location     %s    api quota    %s", this.getUptime() + nl, config.codeVersion() + nl, location + nl, getQuota()));
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
        int s, m, h, d;
        double dec;
        double time = duration * 1.0;
    
        time = (time / 1000.0);
        dec = time % 1;
        time = time - dec;
    
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
