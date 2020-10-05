package ch.philnet.checkyerflags.commands;

import ch.philnet.checkyerflags.utils.MessageHandler;
import org.sobotics.chatexchange.chat.Room;
import org.sobotics.chatexchange.chat.event.PingMessageEvent;

import java.util.Arrays;

public class WelcomeCommand extends Command {
    public WelcomeCommand(Room chatRoom, MessageHandler msgHandler) {
        //Allowed Patters:
        // stop
        // bye
        commandPattern = "(?i)(welcome\\s\\w+)";
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
            if (event.getRoomId() != 111347)
                room.replyTo(messageId, "This command is not supported in this room.");

            String newUser = event.getMessage().getContent().split(" ")[2];
            room.send(String.format("@%s Welcome to SOBotics! You can learn more about SOBotics and what we and all the bots are doing here at our website, https://sobotics.org/. If you'd like to help out with flagging, reporting, or anything else, let us know! We have tons of userscripts to make things easier, and you'll always find someone around who will help you to install them and explain how they work. Also make sure to check out our GitHub organization.\nAll bots: https://sobotics.org/all-bots/ UserScripts: https://sobotics.org/userscripts/ GitHub: https://github.com/sobotics", newUser));
            messageHandler.info(String.format("(Command): Welcoming new User '%s', called by '%s'.", newUser, event.getMessage().getUser().getName()));
        }
    }
}
