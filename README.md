# One Telegram bot for practicing Japanese implemented using OpenAI.
This is a Telegram bot For practicing Japanese . 
Use [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)  to build the telegram bot 
Use [Open Ai audio](https://platform.openai.com/docs/api-reference/audio) to turn audio into text.
Use [Open Ai completions](https://platform.openai.com/docs/api-reference/completions) for chat 
Use [Azure text to speech](https://learn.microsoft.com/en-us/azure/cognitive-services/Speech-Service/) to turn text into audio

## Setup
1. If you don’t have Python installed, [install it from here](https://www.python.org/downloads/).

2. Clone this repository.

3. Navigate into the project directory:

4. Create a new virtual environment:

   ```bash
   $ python -m venv venv
   $ . venv/bin/activate
   ```

5. Install the requirements:

   ```bash
   $ pip install -r requirements.txt
   ```

6. Make a copy of the example environment variables file:

   ```bash
   $ cp .env.example .env
   ```

7. Add your [API key](https://beta.openai.com/account/api-keys) to the newly created `.env` file.

