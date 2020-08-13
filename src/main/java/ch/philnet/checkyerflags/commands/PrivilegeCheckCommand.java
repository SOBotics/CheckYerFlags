package ch.philnet.checkyerflags.commands;

import org.sobotics.chatexchange.chat.Room;
import org.sobotics.chatexchange.chat.event.PingMessageEvent;

import ch.philnet.checkyerflags.utils.MessageHandler;

public class PrivilegeCheckCommand extends Command {
    public PrivilegeCheckCommand(Room chatRoom, MessageHandler msgHandler) {
        //Allowed Patters:
        // amiprivileged
        commandPattern = "(?i)(amiprivileged)";
        room = chatRoom;
        messageHandler = msgHandler;
    }

    @Override
    public boolean testCommandPattern(String command) {
        return super.testCommandPattern(command);
    }

    @Override
    public void run(long messageId, PingMessageEvent event) {
        if (super.hasPrivileges(messageId, false)) {
            room.replyTo(messageId, "You are allowed to run privileged commands.");
        } else {
            room.replyTo(messageId, "You are **NOT** allowed to run privileged commands. You need to be a room owner of the current chat room or a site moderator to run privileged commands.");
        }
    }
}
