package ch.philnet.checkyerflags.commands;

import org.slf4j.Logger;
import org.sobotics.chatexchange.chat.Room;

public class PrivilegeCheckCommand extends Command {
    public PrivilegeCheckCommand(Room chatRoom, Logger commandLogger) {
        //Allowed Patters:
        // amiprivileged
        commandPattern = "(?i)(amiprivileged)";
        room = chatRoom;
        logger = commandLogger;
    }

    @Override
    public boolean testCommandPattern(String command) {
        return super.testCommandPattern(command);
    }

    @Override
    public void run(long messageId) {
        if (super.hasPrivileges(messageId, false)) {
            room.replyTo(messageId, "You are allowed to run privileged commands.");
        } else {
            room.replyTo(messageId, "You are **NOT** allowed to run privileged commands. You need to be a room owner of the current chat room or a site moderator to run privileged commands.");
        }
    }
}
