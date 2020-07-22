package ch.philnet.checkyerflags.utils;

import org.json.JSONArray;

import java.util.ArrayList;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public final class Utils {

    /**
     * Test a regular expression against a string like String.contains()
     * @param expression The regular expression
     * @param testString The string which should be checked against
     */
    public static boolean testRegex(String expression, String testString) {
        Pattern p = Pattern.compile(expression);
        Matcher m = p.matcher(testString);
        return m.find();
    }

    /**
     * Converts a JSONArray of strings to a list of strings
     * @param jsonArray JSONArray to convert
     */
    public static List<String> jsonArrayToStringList(JSONArray jsonArray) {
        List<String> list = new ArrayList<String>();
        for (int i = 0; i < jsonArray.length(); i++){
            list.add(jsonArray.getString(i));
        }
        return list;
    }
}
