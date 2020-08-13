package ch.philnet.checkyerflags.services;

import ch.philnet.checkyerflags.commands.AliveCommand;
import ch.philnet.checkyerflags.commands.Command;
import ch.philnet.checkyerflags.commands.CommandsCommand;
import ch.philnet.checkyerflags.commands.DeleteCommand;
import ch.philnet.checkyerflags.commands.PrivilegeCheckCommand;
import ch.philnet.checkyerflags.commands.QuotaCommand;
import ch.philnet.checkyerflags.commands.StopCommand;
import ch.philnet.checkyerflags.utils.MessageHandler;
import ch.philnet.checkyerflags.commands.StatusCommand;

import org.slf4j.LoggerFactory;
import org.sobotics.chatexchange.chat.Room;
import org.sobotics.chatexchange.chat.event.EventType;
import org.sobotics.chatexchange.chat.event.MessagePostedEvent;
import org.sobotics.chatexchange.chat.event.PingMessageEvent;

import java.util.ArrayList;
import java.util.Arrays;

import com.rollbar.notifier.Rollbar;
import com.rollbar.notifier.config.Config;

/**
 * Handles interactions in chat like mentions and replies
 */
public class BotService {
    public MessageHandler messageHandler;
    private String location;
    private String apiKey;
    private Config config;
    private long startTime;

    /**
     * Run the bot service
     * @param room Current room
     * @param location Bot location
     */
    public void run(final Room room, String location, String apiKey, Config config) {
        //Save startTime in ms
        this.startTime = System.currentTimeMillis();

        //Setup MessageHandler
        this.messageHandler = new MessageHandler(LoggerFactory.getLogger(BotService.class), new Rollbar(config));

        //Notify chat users that the bot has started
        messageHandler.info("Send start message to chat...");
        String modeSuffix = config.environment() == "development" ? " (dev)" : "";
        room.send(String.format("[ [CheckYerFlags](https://stackapps.com/q/7792) ] v%s%s started on %s.", config.codeVersion(), modeSuffix, location));

        //Assign passed variables
        this.location = location;
        this.apiKey = apiKey;
        this.config = config;

        //Listen for reply, mention and message posted events
        room.addEventListener(EventType.MESSAGE_POSTED, event -> handleAliveMessage(room, event));
        room.addEventListener(EventType.USER_MENTIONED, event -> handleMessage(room, event, false)); //This event only fires if the logged-in chat user is pinged
        room.addEventListener(EventType.MESSAGE_REPLY, event -> handleMessage(room, event, true));
    }

    /**
     * Handle commands
     * @param room The current room
     * @param event The occured event
     * @param isReply If the current message is a reply
     */
    private void handleMessage(Room room, PingMessageEvent event, boolean isReply) {
        String message = event.getMessage().getPlainContent();
        long messageId = event.getMessage().getId();
        this.messageHandler.info("New mention: " + message);
        this.messageHandler.info("Content: [" + event.getMessage().getContent() + "]");
        String[] allParts = message.toLowerCase().split(" ");
        String[] parts = Arrays.copyOfRange(allParts, 1, allParts.length); //Parts without ping, (everything except @user)

        //Exception for replies
        if (isReply) {
            new DeleteCommand(room, this.messageHandler).run(messageId, event);
            return;
        }

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
        ApiService api = new ApiService(this.apiKey, this.messageHandler);

        ArrayList<Command> commandList = new ArrayList<Command>();
        commandList.add(new AliveCommand(room, this.messageHandler));
        commandList.add(new StopCommand(room, this.messageHandler));
        commandList.add(new PrivilegeCheckCommand(room, this.messageHandler));
        commandList.add(new StatusCommand(room, this.messageHandler, this.startTime, this.location, api, this.config));
        commandList.add(new QuotaCommand(room, this.messageHandler, api));
        commandList.add(new CommandsCommand(room, this.messageHandler));
        return commandList;
    }
}
