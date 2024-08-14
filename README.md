# PCOM Bot

PCOM Bot is a Telegram bot designed to help users manage and report issues in Jira. 
It provides a user-friendly interface for creating, editing, and checking the status of Jira tickets. 
The bot supports multiple languages and can handle attachments such as images.

## Features

- **Create a Ticket**: Allows users to create new tickets in Jira.
- **Edit a Ticket**: Users can add attachments to existing tickets.
- **Check Ticket Status**: Provides information on the current status of a ticket.
- **Change Language**: Users can switch between English and Spanish using the `/lang` command.
- **Attach Images**: Users can send images related to the issue or choose not to send any.

## Commands

- `/help` - Provides information on how to use the bot and its commands.
- `/lang` - Changes the language of the bot. Use `English` or `Español`.

## How to Use

1. **Starting the Bot**: Send `/start` to initiate the bot and receive the welcome message.
   
2. **Creating a Ticket**:
   - Choose "Create a new Jira ticket" from the `/help` menu.
   - Send the title of the issue when prompted.
   - Describe the problem in detail.
   - Optionally, attach an image related to the issue or type 'No' to skip this step.
   
3. **Editing a Ticket**:
   - Choose "Add an attachment to a ticket" from the `/help` menu.
   - Provide the ticket key and the file you want to attach.

4. **Checking Ticket Status**:
   - Choose "Check the status of a ticket" from the `/help` menu.
   - Provide the ticket key to get its current status.

5. **Changing Language**:
   - Use `/lang` followed by the language you want to switch to (e.g., `/lang English` or `/lang Español`).


## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
![MIT License](https://img.shields.io/badge/License-MIT-yellow.svg)
