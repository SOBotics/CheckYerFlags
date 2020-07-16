package ch.philnet.checkyerflags.commands;

import org.slf4j.Logger;
import org.sobotics.chatexchange.chat.Room;
import org.sobotics.chatexchange.chat.User;

import java.util.regex.Pattern;

/**
 * Parent Class for Commands
 */
public abstract class Command {
    String commandPattern;
    Room room;
    Logger logger;

    /**
     * Test if the supplied command string has a valid pattern for the command instance
     * @param command Command string to test
     */
    public boolean testCommandPattern(String command) {
        return Pattern.matches(commandPattern, command);
    }

    /**
     * Test if the user that called the command has privileges to run it
     * @param messageId Id of the message that called the command
     */
    public boolean hasPrivileges(long messageId) {
        User messageAuthor = room.getMessage(messageId).getUser();

        //Only allowed to room owners and moderators
        if (messageAuthor.isModerator() || messageAuthor.isRoomOwner()) {
            return true;
        } else {
            room.replyTo(messageId, "This command is restricted to moderators and room owners.");
            return false;
        }
    }

    /**
     * Run a specific command
     * @param messageId The message id
     */
    public abstract void run(long messageId);
}
