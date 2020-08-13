package ch.philnet.checkyerflags.commands;

import org.sobotics.chatexchange.chat.Room;
import org.sobotics.chatexchange.chat.event.PingMessageEvent;

import ch.philnet.checkyerflags.utils.MessageHandler;

public class AliveCommand extends Command {
    public AliveCommand(Room chatRoom, MessageHandler msgHandler) {
        //Allowed Patters:
        // alive
        commandPattern = "(?i)(alive)";
        room = chatRoom;
        messageHandler = msgHandler;
    }

    @Override
    public boolean testCommandPattern(String command) {
        return super.testCommandPattern(command);
    }

    @Override
    public void run(long messageId, PingMessageEvent event) {
        messageHandler.info("Replying to alive command");
        room.replyTo(messageId, "You doubt me?");
    }
}
