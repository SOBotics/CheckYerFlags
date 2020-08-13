package ch.philnet.checkyerflags.commands;

import org.sobotics.chatexchange.chat.Room;
import org.sobotics.chatexchange.chat.event.PingMessageEvent;

import ch.philnet.checkyerflags.utils.MessageHandler;

public class DeleteCommand extends Command {
    public DeleteCommand(Room chatRoom, MessageHandler msgHandler) {
        //Allowed Patters:
        // alive
        commandPattern = "(?i)(delete)";
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
            room.delete(event.getParentMessageId());
        }
    }
}
