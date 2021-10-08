OK, so I'm trying to figure out why TestingSlashCommands.py doesn't work as I expect here.

Steps to reproduce: 

1. Make a new Discord bot application and invite it to your server. Give it suitable permissions (slash commands, reading messages and viewing channels). Put the relevant environmental variables in the .env file.
2. Run TestingSlashCommands.py.
3. Type the command "y!newest" into Discord. After some time, you should see the message "Ping!" followed by an embed titled "TEST EMBED: YACPDB Problem >>[number greater than 500000]" and with text "test embed". This is as intended.
4. Type the command "/newest" into Discord. After some time, you should see the interaction fail. This is NOT as intended. The intended behaviour is as in Step 3.
