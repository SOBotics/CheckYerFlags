package ch.philnet.checkyerflags.commands;

import org.sobotics.chatexchange.chat.Room;
import org.sobotics.chatexchange.chat.event.PingMessageEvent;

import ch.philnet.checkyerflags.utils.MessageHandler;

public class CommandsCommand extends Command {
    public CommandsCommand(Room chatRoom, MessageHandler msgHandler) {
        //Allowed Patters:
        // commands
        // help
        commandPattern = "(?i)(commands|help)";
        room = chatRoom;
        messageHandler = msgHandler;
    }

    @Override
    public boolean testCommandPattern(String command) {
        return super.testCommandPattern(command);
    }

    @Override
    public void run(long messageId, PingMessageEvent event) {
        messageHandler.info("Printing command list");
        //TODO: Actually implement all those commands.
        String commands = "    ### CheckYerFlags commands ###\n" +
        "    alive                        - Responds with a message if the bot is running in the current room\n" +
        "    amiprivileged                - Checks if you're allowed to run privileged commands.\n" +
        "    commands, help               - This command. Lists all available commands.\n" +
        //"    goal <flag count> [message]  - Set your custom goal to <flag count> flags. Displays an optional message once you reach your custom rank.\n" +
        //"    goal delete                  - Deletes your custom goal.\n" +
        "    quota                        - Returns the amount of remaining Stack Exchange API quota.\n" +
        //"    rank next, rn                - Gets your next flag rank and how much flags you need to get to it. Returns your custom goal if it's closer than the next rank.\n" +
        "    say <message>                - Sends <message> as a chat message.\n" +
        //"    rank <user id>               - Gets flag rank and status to the next rank for the specified <user id>.\n" +
        //"    rank me, rm                  - Gets your own flag rank and status to the next rank.\n" +
        "    status                       - Returns uptime, location and api quota.\n" +
        "    ### Privileged commands (room owners & moderators) ###\n" +
        "    delete                       - Deletes the message replied to, if possible.\n" +
        "    stop, bye                    - Stops the bot.";




        //Only on SOBotics: Welcome command
        if (room.getRoomId() == 111347) {
            commands += "welcome <username>           - Post a room introduction message. The specified user with <username> will get pinged.";
        }

        room.send(commands);
    }
}
