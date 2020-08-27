# CheckYerFlags

A bot notifying when a user reach a certain flag count and reporting posts with narrow language tags which are missing the generic tag.

[Commands list](https://github.com/SOBotics/CheckYerFlags/blob/v3/src/main/java/ch/philnet/checkyerflags/commands/CommandsCommand.java#L27)

### Example:
- Post has only tag `python3.x`: Bot reports for missing "parent" tag `python`
- Post has tags `javascript`, `jquery`: Bot doesn't report, the "parent" tag is present

The relation between the tags can be seen in the [tags.yaml file](https://github.com/SOBotics/CheckYerFlags/blob/v3/data/tags.yaml).

## Dependencies
Java 8, Maven etc.  
Also see the content of pom.xml

*This section will be refined to specify the actual dependencies*

## Non-code contributors
These people didn't contribute by submitting code, but by testing the bot's limits to find bugs and suggesting feature changes:
- @K-Davis1
- @geisterfurz007

The idea for the tag checking functions of the bot originated from https://github.com/SOBotics/Nursery/issues/10
