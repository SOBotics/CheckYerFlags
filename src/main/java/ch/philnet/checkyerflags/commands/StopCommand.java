package ch.philnet.checkyerflags.commands;

import org.sobotics.chatexchange.chat.Room;
import org.sobotics.chatexchange.chat.event.PingMessageEvent;

import ch.philnet.checkyerflags.utils.MessageHandler;

public class StopCommand extends Command {
    public StopCommand(Room chatRoom, MessageHandler msgHandler) {
        //Allowed Patters:
        // stop
        // bye
        commandPattern = "(?i)(stop|bye)";
        room = chatRoom;
        messageHandler = msgHandler;
    }

    @Override
    public boolean testCommandPattern(String command) {
        return super.testCommandPattern(command);
    }

    @Override
    public void run(long messageId, PingMessageEvent event) {
        if (super.hasPrivileges(messageId)) {
            room.send("I'll be back!");
            messageHandler.info("Stopping the bot");
            room.leave();
            System.exit(0);
        }
    }
}
