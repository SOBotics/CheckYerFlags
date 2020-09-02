package ch.philnet.checkyerflags.services;

import ch.philnet.checkyerflags.models.Rank;
import java.util.TreeMap;

public class RankService {

    public TreeMap<Long, Rank> getRanks() {
        TreeMap<Long, Rank> ranks = new TreeMap<>();
        ranks.put(365L, new Rank(365, "A flag a day keeps bad posts away", "One year has 365 days"));
        ranks.put(811L, new Rank(811, "How thare thy?", "I think you know whose user id that is"));
        ranks.put(1111L, new Rank(1111, "No badge needed", "A number is prettier than a badge anyway!"));
        ranks.put(1337L, new Rank(1337, "l337 fl4663r", "[l337 5p34k 15 4w350m3!](https://en.wikipedia.org/wiki/Leet)"));
        ranks.put(1969L, new Rank(1969, "Moon landing", "I flagged the moon!"));
        ranks.put(2008L, new Rank(2008, "Flag Overflow", "Stack Overflow was created in 2008"));
        ranks.put(2395L, new Rank(2395, "Flag me up, Scotty", "[We don't beam, we flag](https://en.wikipedia.org/wiki/Beam_me_up,_Scotty)"));
        ranks.put(3456L, new Rank(3456, "<3456", "You <3 flagging too much"));
        ranks.put(5566L, new Rank(5566, "[Long Time No Flag](https://en.wikipedia.org/wiki/Long_Time_No_See_(5566_album))", "[Taiwanese boy band, formed under Taiwanese music company, J-Star](https://en.wikipedia.org/wiki/5566)"));
        ranks.put(10000L, new Rank(10000, "Elite Squad", "At one point of time, there were only 16 of us"));
        ranks.put(11111L, new Rank(11111, "Game of Flags", "All elevens because the TV show Game of Thrones started in 2011"));
        ranks.put(19679L, new Rank(19679, "Professional Larnsonist", "19679 is Brad Larnson's user id"));
        ranks.put(22656L, new Rank(22656, "Almost Jon Skeet", "22656 is his (John's) user ID"));
        ranks.put(33333L, new Rank(33333, "The Mad Flagger", "Got nothing better to do with your time? ;D"));
        ranks.put(42195L, new Rank(42195, "The Marathon", "Marathon's length in meters"));
        ranks.put(65536L, new Rank(65536, "The two to the sixteen", ""));
        ranks.put(101010L, new Rank(101010, "Definitely a robot", "42 in binary code. [Also 42 is the Answer to the Ultimate Question of Life, the Universe, and Everything](https://en.wikipedia.org/wiki/Phrases_from_The_Hitchhiker%27s_Guide_to_the_Galaxy#Answer_to_the_Ultimate_Question_of_Life,_the_Universe,_and_Everything_(42))"));
        ranks.put(314159L, new Rank(314159, "\u03C0", "Who ate all the Pi?"));
        ranks.put(874188L, new Rank(874188, "tripleee", "Wheeereee has theee eee goneee?"));
        ranks.put(1849664L, new Rank(1849664, "Woof woof", "1849664 is Undo's user id"));
        ranks.put(3735529L, new Rank(3735529, "He just does the pointing job", "3735529 is Smokey's user id"));
        ranks.put(4733879L, new Rank(4733879, "Call me flaggy", "4733879 is Filnor's user id"));
        ranks.put(2147483647L, new Rank(2147483647, "The Overflow", "[Maximum size of a 32-bit integer](https://stackoverflow.com/a/94608)"));
        ranks.put(4294967296L, new Rank(4294967296L, "A `long` journey", ""));

        return ranks;
    }

    public Rank getCurrentRank(long flags)  {
        try {
            return this.getRanks().floorEntry(flags).getValue();
        } catch (NullPointerException e) {
            return null;
        }
    }

    public Rank getNextRank(long flags) {
        try {
            return this.getRanks().ceilingEntry(flags+1).getValue();
        } catch (NullPointerException e) {
            return null;
        }
    }
}
