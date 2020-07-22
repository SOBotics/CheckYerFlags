package ch.philnet.checkyerflags.commands;

import org.slf4j.Logger;
import org.sobotics.chatexchange.chat.Room;
import org.sobotics.chatexchange.chat.event.PingMessageEvent;

public class DeleteCommand extends Command {
    public DeleteCommand(Room chatRoom, Logger commandLogger) {
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
    public void run(long messageId, PingMessageEvent event) {
        if (super.hasPrivileges(messageId)) {
            room.delete(event.getParentMessageId());
        }
    }
}
