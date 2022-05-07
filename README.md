# Japanese Vocabulary Card Generator
This is an addon for the SRS software Anki that allows you to quickly add Japanese vocabulary to your deck using the [jisho.org](jisho.org) API.

## Installation
Download the latest release `.ankiaddon` file and install it with Anki's `install from file` option in the Add Ons menu.

## Usage
This plugin adds an option to Anki's `Tools` menu:\
![Image of the Tools menu containing the option "Add Words"](docs/tools.png)

This opens a new window where you can select the deck you would like to add to, and choose whether to add a card manually or add words from a file:\
![Image of a window displaying a list of decks to select from and two buttons entitled "Add Card" and "Add From File"](docs/add%20words.png)

The Add From File option allows you to select a text file containing Japanese words separated by newlines to add to your deck. After processing the file, a report is displayed:\
![Image of a window containing a table with columns "Success," "Note Exists," "Not Found," and "Connection Error" with Japanese words sorted between them](docs/report.PNG)

The Add Card option allows you to search for an individual word and decide whether to add it to your deck:\
![Image of a window with an input box reading めんどくさい followed by a list box containing various information about the word and two buttons labeled "Search Jisho" and "Add Card"](docs/add%20card.png)
