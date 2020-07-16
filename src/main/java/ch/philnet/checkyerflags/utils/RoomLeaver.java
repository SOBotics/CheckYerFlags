package ch.philnet.checkyerflags.utils;

import org.sobotics.chatexchange.chat.Room;

/**
 * Leaves the room after some other action is finished
 */
public class RoomLeaver implements Runnable{
    private Room room;

    public RoomLeaver(Room chatRoom) {
        room = chatRoom;
    }

    @Override
    public void run() {
        room.leave();
    }
}
