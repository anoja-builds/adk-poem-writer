# ADK Poem Writer Agent

An AI-powered poem-writing agent built using Google's Agent Development Kit (ADK).

This project was developed collaboratively during the **Build with AI Sri Lanka 2026 Buildathon** as a hands-on exploration of AI agents and generative AI.

## About the Project

The ADK Poem Writer Agent generates original poems based on user preferences such as topic, language, mood, style, format, and length.

The goal of the project was to experiment with building a simple AI agent using Google's Agent Development Kit.

## Features

- Generates original poems
- Supports multiple languages, including English, Tamil, and Sinhala
- Supports different moods such as motivational, nostalgic, romantic, peaceful, and humorous
- Supports multiple poem formats, including:
  - Free verse
  - Rhyming poems
  - Haiku
  - Sonnet
  - Acrostic poems
- Supports custom poem lengths
- Automatically generates a suitable title
- Reviews and refines each draft before returning the final poem

The text pipeline exposes only the refiner's response. Drafts and feedback
remain in session state for the following stages and can still be inspected
in ADK's developer tools. Requests for no title are preserved during refinement.

## Tech Stack

- Python
- Google Agent Development Kit (ADK)
- Gemini
- ADK Web

## Project Structure

```text
adk-poem-writer/
├── .gitignore
├── README.md
├── requirements.txt
└── poem_writer/
    ├── __init__.py
    └── agent.py
```

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/anoja-builds/adk-poem-writer.git
cd adk-poem-writer
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate the virtual environment

Windows:

```bash
.venv\Scripts\activate
```

### 4. Install the dependencies

```bash
pip install -r requirements.txt
```

The project pins Google ADK to version 1.28.0 for the sequential pipeline API.

### 5. Configure Google ADK

Configure your Gemini API credentials according to the Google ADK setup instructions.

Keep API keys and environment variables in a `.env` file and do not commit them to GitHub.

### 6. Run the agent

```bash
adk web
```

## Example Prompts

```text
Write a motivational poem about learning programming.

Write a nostalgic Tamil poem about childhood friendships.

Write a haiku about rain.

Write an acrostic poem using the word AI.
```

## Tests

With the virtual environment activated, run:

```bash
python -m unittest discover -s tests -v
```

These tests use simulated model responses with the real ADK runner to verify
state handoff and final-only output, including streaming. They require no API
key. Actual Gemini poetry quality and instruction adherence require a live run.

## Contributors

This project was developed collaboratively during the **Build with AI Sri Lanka 2026 Buildathon**.

- Anoja C — [@anoja-builds](https://github.com/anoja-builds)
- Theenasaran K — https://github.com/IT24103104

## Event

Built during the **Build with AI Sri Lanka 2026 Buildathon**.

The event provided an opportunity to explore AI development and build practical AI-powered solutions using Google technologies.

## Future Improvements

- Improve input validation
- Add structured controls for poem preferences
- Add a simple custom user interface
- Deploy the application online
