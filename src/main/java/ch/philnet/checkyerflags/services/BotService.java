package ch.philnet.checkyerflags.services;

import ch.philnet.checkyerflags.commands.AliveCommand;
import ch.philnet.checkyerflags.commands.Command;
import ch.philnet.checkyerflags.commands.CommandsCommand;
import ch.philnet.checkyerflags.commands.DeleteCommand;
import ch.philnet.checkyerflags.commands.PrivilegeCheckCommand;
import ch.philnet.checkyerflags.commands.QuotaCommand;
import ch.philnet.checkyerflags.commands.StopCommand;
import ch.philnet.checkyerflags.commands.StatusCommand;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.sobotics.chatexchange.chat.Room;
import org.sobotics.chatexchange.chat.event.EventType;
import org.sobotics.chatexchange.chat.event.MessagePostedEvent;
import org.sobotics.chatexchange.chat.event.PingMessageEvent;

import java.util.ArrayList;
import java.util.Arrays;

/**
 * Handles interactions in chat like mentions and replies
 */
public class BotService {
    private static final Logger LOGGER = LoggerFactory.getLogger(BotService.class);
    private String location;
    private String apiKey;
    private long startTime;

    /**
     * Run the bot service
     * @param room Current room
     * @param location Bot location
     */
    public void run(final Room room, String location, String apiKey) {
        //Save startTime in ms
        this.startTime = System.currentTimeMillis();

        //Notify chat users that the bot has started
        LOGGER.info("Send start message to chat...");
        String version = "3.0.0-dev";
        room.send(String.format("[ [CheckYerFlags](https://stackapps.com/q/7792) ] v%s started on %s.", version, location));

        //Assign passed variables
        this.location = location;
        this.apiKey = apiKey;

        //Listen for reply, mention and message posted events
        room.addEventListener(EventType.MESSAGE_POSTED, event -> handleAliveMessage(room, event));
        room.addEventListener(EventType.USER_MENTIONED, event -> handleMessage(room, event)); //This event only fires if the logged-in chat user is pinged
        //room.addEventListener(EventType.MESSAGE_REPLY, event -> handleMessage(room, event, true)); //Currently not needed
    }

    /**
     * Handle commands
     * @param room The current room
     * @param event The occured event
     * @param isReply If the current message is a reply
     */
    private void handleMessage(Room room, PingMessageEvent event) {
        String message = event.getMessage().getPlainContent();
        long messageId = event.getMessage().getId();
        LOGGER.info("New mention: " + message);
        LOGGER.info("Content: [" + event.getMessage().getContent() + "]");
        String[] allParts = message.toLowerCase().split(" ");
        String[] parts = Arrays.copyOfRange(allParts, 1, allParts.length); //Parts without ping, (everything except @user)

        for (Command command : availableCommands(room)) {
            if (command.testCommandPattern(String.join(" ", parts))) {
                command.run(messageId, event);
            }
        }
    }

    /**
     * Handle mass-bot alive check messages
     * @param room The current room
     * @param event The occured event
     */
    private void handleAliveMessage(Room room, MessagePostedEvent event) {
        String msg = event.getMessage().getContent();

        //Respond to "@bots alive" command
        if (msg != null && msg.toLowerCase().startsWith("@bots alive"))
            room.send("You doubt me?");

        //Respond to alive train
        if (msg != null && msg.length() > 0) {
            int codePoint = Character.codePointAt(msg, 0);
            if (codePoint == 128642 || (codePoint >= 128644 && codePoint <= 128650))
                room.send("[\uD83D\uDE83](https://www.youtube.com/watch?v=CSvFpBOe8eY)");
        }
    }

    /**
     * Get a list of all commands available to the bot
     */
    private ArrayList<Command> availableCommands(Room room) {
        ApiService api = new ApiService(this.apiKey, LOGGER);

        ArrayList<Command> commandList = new ArrayList<Command>();
        commandList.add(new AliveCommand(room, LOGGER));
        commandList.add(new StopCommand(room, LOGGER));
        commandList.add(new PrivilegeCheckCommand(room, LOGGER));
        commandList.add(new StatusCommand(room, LOGGER, this.startTime, this.location, api));
        commandList.add(new QuotaCommand(room, LOGGER, api));
        commandList.add(new DeleteCommand(room, LOGGER));
        commandList.add(new CommandsCommand(room, LOGGER));
        return commandList;
    }
}
