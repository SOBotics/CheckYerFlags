package ch.philnet.checkyerflags.commands;

import java.util.regex.Matcher;
import java.util.regex.Pattern;

import org.sobotics.chatexchange.chat.Message;
import org.sobotics.chatexchange.chat.Room;
import org.sobotics.chatexchange.chat.event.PingMessageEvent;

import ch.philnet.checkyerflags.models.Rank;
import ch.philnet.checkyerflags.services.ApiService;
import ch.philnet.checkyerflags.services.FlagService;
import ch.philnet.checkyerflags.services.RankService;
import ch.philnet.checkyerflags.utils.MessageHandler;

public class RankCommand extends Command {
    private ApiService api;
    private final FlagService flagService = new FlagService();
    private final RankService rankService = new RankService();

    public RankCommand(Room chatRoom, MessageHandler msgHandler, ApiService api) {
        //Allowed Patters:
        // alive
        commandPattern = "(r[m|n])|(rank\s(next|me|[0-9]+))|(r\s[0-9]+)";
        room = chatRoom;
        messageHandler = msgHandler;
        this.api = api;
    }

    @Override
    public boolean testCommandPattern(String command) {
        return super.testCommandPattern(command);
    }

    @Override
    public void run(long messageId, PingMessageEvent event) {
        messageHandler.info("Replying to rank check command");

        Message message = room.getMessage(messageId);
        String messageText = message.getContent().toLowerCase();

        //Remove @-ping from message
        messageText = messageText.replaceAll("@\\w+\\s", "");

        long senderId = message.getUser().getId();

        long currentFlags = 0L;
        try {
            currentFlags = this.flagService.getFlagCountForUser(senderId);
        } catch (Exception e) {
            messageHandler.error(e);
            room.replyTo(messageId, "Error while obtaining flag count. (cc @Filnor)");
            return;
        }
        Rank currentRank = this.rankService.getCurrentRank(currentFlags);
        Rank nextRank = this.rankService.getNextRank(currentFlags);
        long flagsToNextRank = nextRank.getFlagCount()-currentFlags;


        if(messageText.matches("rm") || messageText.matches("rank me")) {
            if(currentRank == null) {
                room.replyTo(messageId, String.format("You currently have %,d helpful flags. You need %,d flags more for your first rank.", currentFlags, flagsToNextRank));
                return;
            }

            room.replyTo(messageId, String.format("You currently have %,d helpful flags. Your last achieved rank was **%s** %s for %,d helpful flags. You need %,d more flags for your next rank, *%s*.",
            currentFlags, currentRank.getTitle(), currentRank.getDescription(), currentRank.getFlagCount(), flagsToNextRank, nextRank.getTitle()));
        } else if(messageText.matches("rn") || messageText.matches("rank next")) {
            room.replyTo(messageId, String.format("You need %,d more flags to get your next flag rank, **%s** %s (%,d flags in total).",
            flagsToNextRank, nextRank.getTitle(), nextRank.getDescription(), nextRank.getFlagCount()));
        } else if(messageText.matches("(rank\s[0-9]+)|(r\s[0-9]+)")) {
            long userId = this.getUserFromMessage(messageText);

            if(userId <= 0) {
                room.replyTo(messageId, String.format("User id '%d' is not valid", userId));
                return;
            }

            long userCurrentFlags = 0L;
            try {
                userCurrentFlags = this.flagService.getFlagCountForUser(userId);
            } catch (Exception e) {
                messageHandler.error(e);
                room.replyTo(messageId, "Error while obtaining flag count. (cc @Filnor)");
                return;
            }
            Rank userCurrentRank = this.rankService.getCurrentRank(userCurrentFlags);
            Rank userNextRank = this.rankService.getNextRank(userCurrentFlags);
            long userFlagsToNextRank = userNextRank.getFlagCount()-userCurrentFlags;
            String userName = this.api.getUserName(userId);

            if(userCurrentRank == null) {
                room.replyTo(messageId, String.format("%s currently has %,d helpful flags. They need %,d flags more for their first rank.", userName, userCurrentFlags, userFlagsToNextRank));
                return;
            }

            room.replyTo(messageId, String.format("%s currently has %,d helpful flags. Their last achieved rank was **%s** %s for %,d helpful flags. They need %,d more flags for their next rank, *%s*.",
            userName, userCurrentFlags, userCurrentRank.getTitle(), userCurrentRank.getDescription(), userCurrentRank.getFlagCount(), userFlagsToNextRank, userNextRank.getTitle()));
        }
    }

    private long getUserFromMessage(String message) {
        Pattern pattern = Pattern.compile("((?<=rank\s)[0-9]+)|((?<=r\s)[0-9]+)");
        Matcher matcher = pattern.matcher(message);
        String user = "0";

        if(matcher.find()) {
            user = matcher.group(0);
        }

        return Long.parseLong(user);
    }
}
