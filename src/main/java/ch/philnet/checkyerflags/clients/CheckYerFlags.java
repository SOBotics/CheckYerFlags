package ch.philnet.checkyerflags.clients;

import org.sobotics.chatexchange.chat.ChatHost;
import org.sobotics.chatexchange.chat.Room;
import org.sobotics.chatexchange.chat.StackExchangeClient;

import ch.philnet.checkyerflags.services.BotService;
import ch.philnet.checkyerflags.services.QuestionService;

import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.util.Properties;

import com.rollbar.notifier.Rollbar;
import com.rollbar.notifier.config.Config;
import com.rollbar.notifier.config.ConfigBuilder;
import com.rollbar.notifier.sender.SyncSender;

public class CheckYerFlags {
    public static Rollbar rollbar;
    public static void main(String[] args) throws IOException {
        StackExchangeClient client;
        Properties prop = new Properties();

        try {
            prop.load(new FileInputStream( "." + File.separator + "properties" + File.separator + "auth.properties"));
        } catch (IOException e) {
            System.err.println("Can't read properties file. Have you renamed 'auth.example.properties' to 'auth.properties'?");
            e.printStackTrace();
        }

        //Initialize Rollbar
        Config config = ConfigBuilder.withAccessToken(prop.getProperty("rollbarAccessToken"))
            .environment("development")
            .codeVersion("3.0.0")
            .sender(new SyncSender.Builder().build())
            .enabled(prop.getProperty("rollbarAccessToken") == "")
        .build();

        client = new StackExchangeClient(prop.getProperty("email"), prop.getProperty("password"));
        Room room = client.joinRoom(ChatHost.STACK_OVERFLOW, Integer.parseInt(prop.getProperty("roomId")));
        new BotService().run(room, prop.getProperty("location"), prop.getProperty("apiKey"), config);
        new QuestionService().run(room);
    }
}
