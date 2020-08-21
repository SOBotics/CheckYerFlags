package ch.philnet.checkyerflags.commands;

import org.sobotics.chatexchange.chat.Message;
import org.sobotics.chatexchange.chat.Room;
import org.sobotics.chatexchange.chat.event.PingMessageEvent;

import ch.philnet.checkyerflags.utils.MessageHandler;

public class SayCommand extends Command {

    public SayCommand(Room chatRoom, MessageHandler msgHandler) {
        //Allowed Patters:
        // quota
        commandPattern = "(?i)(say)\s.+";
        room = chatRoom;
        messageHandler = msgHandler;
    }

    @Override
    public boolean testCommandPattern(String command) {
        return super.testCommandPattern(command);
    }

    @Override
    public void run(long messageId, PingMessageEvent event) {
        messageHandler.info("Writing say message");
        Message message = room.getMessage(messageId);
        room.send(message.getContent().replaceAll(".+\s(?i)(say)\s", ""));
    }
}
