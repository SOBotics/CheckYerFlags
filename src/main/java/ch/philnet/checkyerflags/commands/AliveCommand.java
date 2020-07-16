package ch.philnet.checkyerflags.commands;

import org.slf4j.Logger;
import org.sobotics.chatexchange.chat.Room;

public class AliveCommand extends Command {
    public AliveCommand(Room chatRoom, Logger commandLogger) {
        //Allowed Patters:
        // alive
        commandPattern = "(?i)(alive)";
        room = chatRoom;
        logger = commandLogger;
    }

    @Override
    public boolean testCommandPattern(String command) {
        return super.testCommandPattern(command);
    }

    @Override
    public void run(long messageId) {
        logger.info("Replying to alive command");
        room.replyTo(messageId, "You doubt me?");
    }
}
