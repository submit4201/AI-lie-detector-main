
####################################

# Example: Structured Streaming Output
# This example demonstrates how to stream audio data to the Gemini Live API
# for transcription while requesting structured output in JSON format.
# The model will return transcriptions along with a simple sentiment analysis
# for each audio chunk in a structured JSON format.

#####################################


import asyncio
from google import genai
from google.genai import types
import json # Import json for parsing structured output

# Ensure the client is initialized with the correct API key and alpha version
# (already done in earlier setup cells, but re-emphasizing its importance)

# For streaming audio transcription, we'll use a multimodal model like 'gemini-2.5-pro'
# for better instruction following and structured output capabilities.
TRANSCRIPTION_MODEL_ID = 'models/gemini-2.5-pro'

async def stream_audio_for_transcription(audio_data: bytes):
    print("Connecting to Gemini Live API for transcription with structured analysis...")
    async with client.aio.live.chat.connect(model=TRANSCRIPTION_MODEL_ID) as session:
        print("Connection established. Sending initial instruction and audio chunk...")

        # Prepare the audio blob to send
        # In a real-time scenario, 'audio_data' would be a continuous stream of chunks
        audio_blob = types.Blob(mime_type='audio/wav', data=audio_data)

        # Initial message with instructions for structured output and analysis
        # Prompt the model to return JSON with transcription and a simple sentiment analysis
        initial_instruction = """
        You are an audio transcription and analysis assistant.
        For every audio chunk, provide the transcription and a simple sentiment analysis (positive, neutral, negative).
        Respond ONLY in JSON format with the following structure:
        {
          "transcription": "...",
          "sentiment": "..."
        }
        """

        # Send the instruction as a text part, followed by the audio data
        await session.send_message(
            contents=[
                types.Content(parts=[types.Part(text=initial_instruction)]),
                types.Content(parts=[audio_blob])
            ]
        )

        print("Instruction and audio chunk sent. Waiting for structured transcription and analysis...")
        # Receive responses from the model
        async for message in session.receive():
            if message.candidates:
                for candidate in message.candidates:
                    if candidate.content and candidate.content.parts:
                        for part in candidate.content.parts:
                            if part.text:
                                try:
                                    # Attempt to parse the text as JSON
                                    response_json = json.loads(part.text)
                                    transcription = response_json.get("transcription", "N/A")
                                    sentiment = response_json.get("sentiment", "N/A")
                                    print(f"Structured Response:\n  Transcription: {transcription}\n  Sentiment: {sentiment}")
                                except json.JSONDecodeError:
                                    print(f"Received non-JSON text (or malformed JSON): {part.text}")
            else:
                print("No structured transcription/analysis received for this chunk.")

        print("Transcription session ended.")

# Simulate a very small, silent audio chunk for demonstration purposes
# In a real application, this would come from a microphone or an audio file
simulated_audio_chunk = b'RIFF\x26\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x40\x1F\x00\x00\x80\x3E\x00\x00\x02\x00\x10\x00data\x00\x00\x00\x00'

# To run the async function
# asyncio.run(stream_audio_for_transcription(simulated_audio_chunk))
# Note: If running this in a Jupyter/Colab environment, you might need to use await directly
# or a different approach to manage the event loop if one is already running.
print("To execute the transcription example, please uncomment and run the line below:")
print("await stream_audio_for_transcription(simulated_audio_chunk)")



#####################################
# # Example of streaming live microphone audio (requires sounddevice and numpy)
# # Uncomment and run in a suitable local environment with microphone access
#####################################

# import sounddevice as sd
# import numpy as np

# async def stream_live_microphone_for_transcription():
#     sample_rate = 16000  # Hz
#     channels = 1
#     block_size = 1024 * 2 # Process in small blocks

#     async with client.aio.live.chat.connect(model=TRANSCRIPTION_MODEL_ID) as session:
#         print("Listening for audio...")
#         with sd.RawInputStream(samplerate=sample_rate, channels=channels, dtype='int16', blocksize=block_size) as stream:
#             while True:
#                 audio_chunk, overflowed = stream.read(block_size)
#                 if overflowed:
#                     print("Warning: Audio input buffer overflowed!")

#                 audio_blob = types.Blob(mime_type='audio/wav', data=audio_chunk)
#                 await session.send_message(contents=[types.Content(parts=[audio_blob])])

#                 # Process incoming transcriptions (similar to the example above)
#                 async for message in session.receive():
#                     if message.candidates:
#                         for candidate in message.candidates:
#                             if candidate.content and candidate.content.parts:
#                                 for part in candidate.content.parts:
#                                     if part.text:
#                                         print(f"Live Transcription: {part.text}")

#                 await asyncio.sleep(0.01) # Small delay

# # To run live microphone (requires appropriate setup and permissions):
# # await stream_live_microphone_for_transcription()

#####################################

# # colab notebook example of streaming usage below
# # example from google gemini cookbook
# # for reference only and not to be run here

##############
# {
#   "cells": [
#     {
#       "cell_type": "markdown",
#       "metadata": {
#         "id": "Tce3stUlHN0L"
#       },
#       "source": [
#         "##### Copyright 2025 Google LLC."
#       ]
#     },
#     {
#       "cell_type": "code",
#       "execution_count": null,
#       "metadata": {
#         "cellView": "form",
#         "id": "tuOe1ymfHZPu"
#       },
#       "outputs": [],
#       "source": [
#         "# @title Licensed under the Apache License, Version 2.0 (the \"License\");\n",
#         "# you may not use this file except in compliance with the License.\n",
#         "# You may obtain a copy of the License at\n",
#         "#\n",
#         "# https://www.apache.org/licenses/LICENSE-2.0\n",
#         "#\n",
#         "# Unless required by applicable law or agreed to in writing, software\n",
#         "# distributed under the License is distributed on an \"AS IS\" BASIS,\n",
#         "# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.\n",
#         "# See the License for the specific language governing permissions and\n",
#         "# limitations under the License."
#       ]
#     },
#     {
#       "cell_type": "markdown",
#       "metadata": {
#         "id": "yeadDkMiISin"
#       },
#       "source": [
#         "# Gemini API: Streaming Quickstart"
#       ]
#     },
#     {
#       "cell_type": "markdown",
#       "metadata": {
#         "id": "3f5bc95b9107"
#       },
#       "source": [
#         "<a target=\"_blank\" href=\"https://colab.research.google.com/github/google-gemini/cookbook/blob/main/quickstarts/Streaming.ipynb\"><img src=\"https://colab.research.google.com/assets/colab-badge.svg\" height=30/></a>"
#       ]
#     },
#     {
#       "cell_type": "markdown",
#       "metadata": {
#         "id": "df1767a3d1cc"
#       },
#       "source": [
#         "This notebook demonstrates streaming in the Python SDK. By default, the Python SDK returns a response after the model completes the entire generation process. You can also stream the response as it is being generated, and the model will return chunks of the response as soon as they are generated."
#       ]
#     },
#     {
#       "cell_type": "code",
#       "execution_count": null,
#       "metadata": {
#         "id": "xuiLSV7amy3P"
#       },
#       "outputs": [],
#       "source": [
#         "%pip install -U -q \"google-genai\" # Install the Python SDK"
#       ]
#     },
#     {
#       "cell_type": "code",
#       "execution_count": null,
#       "metadata": {
#         "id": "79EWm0DAmy-g"
#       },
#       "outputs": [],
#       "source": [
#         "from google import genai"
#       ]
#     },
#     {
#       "cell_type": "markdown",
#       "metadata": {
#         "id": "DkeZNMrw6kPD"
#       },
#       "source": [
#         "You'll need an API key stored in an environment variable to run this notebook. See the the [Authentication quickstart](https://github.com/google-gemini/cookbook/blob/main/quickstarts/Authentication.ipynb) for an example."
#       ]
#     },
#     {
#       "cell_type": "code",
#       "execution_count": null,
#       "metadata": {
#         "id": "t9O-OzeAKC_m"
#       },
#       "outputs": [],
#       "source": [
#         "from google.colab import userdata\n",
#         "\n",
#         "GOOGLE_API_KEY = userdata.get('GOOGLE_API_KEY')\n",
#         "client = genai.Client(api_key=GOOGLE_API_KEY)"
#       ]
#     },
#     {
#       "cell_type": "markdown",
#       "metadata": {
#         "id": "BUoa5q0iUuE1"
#       },
#       "source": [
#         "## Handle streaming responses\n",
#         "\n",
#         "To stream responses, use [`Models.generate_content_stream`](https://googleapis.github.io/python-genai/genai.html#genai.models.Models.generate_content_stream)."
#       ]
#     },
#     {
#       "cell_type": "code",
#       "execution_count": null,
#       "metadata": {
#         "id": "nVWWGBsBok3m"
#       },
#       "outputs": [
#         {
#           "name": "stdout",
#           "output_type": "stream",
#           "text": [
#             "El\n",
#             "________________________________________________________________________________\n",
#             "ara adjusted her\n",
#             "________________________________________________________________________________\n",
#             " goggles, the copper rims digging slightly into her temples. The air in her workshop hummed with\n",
#             "________________________________________________________________________________\n",
#             " the chaotic symphony of whirring gears, sputtering steam, and the rhythmic clanging\n",
#             "________________________________________________________________________________\n",
#             " of her hammer. Today was the day. Today, the Sky Serpent took flight.\n",
#             "\n",
#             "For years, Elara had toiled, fueled by scraps of dreams\n",
#             "________________________________________________________________________________\n",
#             " and a stubborn refusal to accept the limitations others imposed. They called her \"the mad tinker,\" scoffed at her blueprints depicting a mechanical dragon soaring through the clouds. But El\n",
#             "________________________________________________________________________________\n",
#             "ara had seen the future, a future where the impossible was merely a challenge.\n",
#             "\n",
#             "She tightened the last bolt on the Sky Serpent's massive, ornithopter wings. Sunlight streamed through the grimy window, illuminating the intricate network of pipes and pistons\n",
#             "________________________________________________________________________________\n",
#             " that powered the magnificent beast. Taking a deep breath, she climbed into the cockpit, a cramped space surrounded by levers, dials, and gauges.\n",
#             "\n",
#             "With a flick of a switch, the furnace roared to life, sending plumes of smoke billowing from the dragon\n",
#             "________________________________________________________________________________\n",
#             "'s iron snout. The workshop trembled as the wings began to beat, slowly at first, then with increasing power. Metal screeched, steam hissed, and then, with a shudder, the Sky Serpent lifted off the ground.\n",
#             "\n",
#             "Elara gripped the controls, her heart pounding in her chest. The workshop shrunk\n",
#             "________________________________________________________________________________\n",
#             " beneath her as the dragon climbed higher and higher, leaving the familiar world behind. Below, she could see the tiny figures of her neighbors, mouths agape, pointing in disbelief.\n",
#             "\n",
#             "As the Sky Serpent broke through the clouds, Elara laughed, a sound filled with triumph and liberation. The wind whipped through her hair, and\n",
#             "________________________________________________________________________________\n",
#             " the sun warmed her face. She had done it. She had flown. The mad tinker, the dreamer, had proven them all wrong. The sky, she realized, was truly the limit.\n",
#             "\n",
#             "________________________________________________________________________________\n"
#           ]
#         }
#       ],
#       "source": [
#         "for chunk in client.models.generate_content_stream(\n",
#         "  model='gemini-2.5-flash',\n",
#         "  contents='Tell me a story in 300 words.'\n",
#         "):\n",
#         "    print(chunk.text)\n",
#         "    print(\"_\" * 80)"
#       ]
#     },
#     {
#       "cell_type": "markdown",
#       "metadata": {
#         "id": "KswwVyHCKC_n"
#       },
#       "source": [
#         "## Handle streaming responses asynchronously\n",
#         "\n",
#         "To stream responses asynchronously, use [`AsyncModels.generate_content_stream(...)`](https://googleapis.github.io/python-genai/genai.html#genai.models.AsyncModels.generate_content_stream)."
#       ]
#     },
#     {
#       "cell_type": "code",
#       "execution_count": null,
#       "metadata": {
#         "id": "DHbwhXi2nvnS"
#       },
#       "outputs": [
#         {
#           "name": "stdout",
#           "output_type": "stream",
#           "text": [
#             "C\n",
#             "________________________________________________________________________________\n",
#             "lementine was a tiny, ginger kitten with a perpetually surprised expression. Her whiskers were like\n",
#             "________________________________________________________________________________\n",
#             " exclamation points, and her tail, a fluffy question mark. She lived in a sun-d\n",
#             "________________________________________________________________________________\n",
#             "renched flower shop, nestled between bouquets of lilies and rambling rose bushes. Her job, as she saw it, was Official Greeter and Head of Pest Control (\n",
#             "________________________________________________________________________________\n",
#             "though the only pests she’d ever encountered were particularly daring butterflies).\n",
#             "\n",
#             "Her best friend was Bartholomew, a grand old tabby who ruled the back room where the flower\n",
#             "________________________________________________________________________________\n",
#             " pots were stored. Bartholomew was wise, grumpy, and possessed an impressive collection of cardboard boxes, each designated for different purposes (napping, staring, important contemplation). He tolerated Clementine’s boundless energy, mostly because she brought him the occasional\n",
#             "________________________________________________________________________________\n",
#             " rogue ladybug.\n",
#             "\n",
#             "One day, a new flower arrived at the shop - a vibrant, exotic orchid with velvety purple petals. Clementine was instantly smitten. She'd never seen anything so beautiful! She spent hours circling it, her little\n",
#             "________________________________________________________________________________\n",
#             " nose twitching, trying to decipher its secrets.\n",
#             "\n",
#             "\"What's that?\" she asked Bartholomew, her tail quivering with excitement.\n",
#             "\n",
#             "Bartholomew, disturbed from his afternoon nap in the \"Important Contemplation\" box, grumbled, \"Just a fancy weed. Don't bother it.\"\n",
#             "\n",
#             "But\n",
#             "________________________________________________________________________________\n",
#             " Clementine couldn't resist. She tiptoed closer, reached out a tentative paw, and gently touched a petal. It was softer than silk!\n",
#             "\n",
#             "Suddenly, the orchid shimmered. Not in a scary way, but in a sparkly, magical way. Clementine gasped as tiny, glittering lights danced around the petals.\n",
#             "________________________________________________________________________________\n",
#             " She blinked, sure she was imagining things.\n",
#             "\n",
#             "Then, she heard a faint, high-pitched voice. \"Hello?\"\n",
#             "\n",
#             "Clementine froze, her fur on end. She looked around wildly. \"Who's there?\"\n",
#             "\n",
#             "The voice giggled. \"Down here!\"\n",
#             "\n",
#             "She peered at the orchid and saw the tini\n",
#             "________________________________________________________________________________\n",
#             "est of figures emerge from within the petals. It was a miniature cat, no bigger than her thumb, with purple fur and sparkly green eyes!\n",
#             "\n",
#             "\"I'm Petunia,\" the tiny cat squeaked. \"And I'm lost!\"\n",
#             "\n",
#             "Clementine was speechless. A real-life, miniature, purple cat\n",
#             "________________________________________________________________________________\n",
#             "! She carefully scooped Petunia up with her paw, holding her gently.\n",
#             "\n",
#             "\"Don't worry, Petunia,\" she said, her voice full of concern. \"I'll help you!\"\n",
#             "\n",
#             "She ran to Bartholomew, her heart thumping with excitement. \"Bartholomew! Bartholomew! Look!\"\n",
#             "________________________________________________________________________________\n",
#             "\n",
#             "\n",
#             "Bartholomew, predictably, was not impressed. He opened one eye a crack and squinted at Clementine. \"What is it this time? Did you find a particularly shiny beetle?\"\n",
#             "\n",
#             "Clementine presented Petunia to him. \"It's a tiny cat! And she's lost!\"\n",
#             "\n",
#             "Bartholom\n",
#             "________________________________________________________________________________\n",
#             "ew sighed dramatically. He clearly thought Clementine had finally lost her mind. But he looked at the tiny creature nestled in Clementine's paw, and something softened in his ancient, golden eyes.\n",
#             "\n",
#             "He puffed out his chest and, in a surprisingly gentle voice, said, \"Alright, alright. We'll\n",
#             "________________________________________________________________________________\n",
#             " help her. First, we need to find her a safe place to sleep.\"\n",
#             "\n",
#             "And so, Clementine and Bartholomew embarked on a grand adventure to help Petunia find her way home. They used a thimble for a bed, a bottle cap for a food dish (filled with delicious flower pollen), and Bartholomew even\n",
#             "________________________________________________________________________________\n",
#             " shared his \"Important Contemplation\" box for the night.\n",
#             "\n",
#             "After a few days, with the help of the flower shop owner who mysteriously found a tiny, perfectly purple knitted blanket, they discovered that Petunia was a magical garden sprite, blown into the shop on a strong wind. With a final, tearful goodbye (\n",
#             "________________________________________________________________________________\n",
#             "and a promise to visit), Petunia was gently placed back onto a passing dandelion seed and floated away, back to her garden.\n",
#             "\n",
#             "Clementine watched until Petunia was a tiny speck in the sky. She felt a pang of sadness, but also a deep sense of joy. She had helped someone, and she had\n",
#             "________________________________________________________________________________\n",
#             " made a friend.\n",
#             "\n",
#             "She looked at Bartholomew, who was already back in his \"Important Contemplation\" box. He didn't say anything, but Clementine saw the faintest of smiles twitching at his whiskers.\n",
#             "\n",
#             "From that day on, Clementine continued to greet every customer with a cheerful meow, and\n",
#             "________________________________________________________________________________\n",
#             " she kept a watchful eye on the orchid, just in case Petunia ever decided to visit again. And every once in a while, when the wind was just right, she could almost hear a tiny, sparkly giggle carried on the breeze. The flower shop, already a magical place, was now a little bit more so,\n",
#             "________________________________________________________________________________\n",
#             " all thanks to a tiny, ginger kitten and her grand adventure.\n",
#             "\n",
#             "________________________________________________________________________________\n"
#           ]
#         }
#       ],
#       "source": [
#         "async for chunk in await client.aio.models.generate_content_stream(\n",
#         "    model='gemini-2.5-flash',\n",
#         "    contents=\"Write a cute story about cats.\"):\n",
#         "    if chunk.text:\n",
#         "        print(chunk.text)\n",
#         "    print(\"_\"*80)"
#       ]
#     },
#     {
#       "cell_type": "markdown",
#       "metadata": {
#         "id": "jpK3p1B4KC_o"
#       },
#       "source": [
#         "Here's a simple example of two asynchronous functions running simultaneously."
#       ]
#     },
#     {
#       "cell_type": "code",
#       "execution_count": null,
#       "metadata": {
#         "id": "1n5qFwvBpyQ1"
#       },
#       "outputs": [
#         {
#           "name": "stdout",
#           "output_type": "stream",
#           "text": [
#             "==========not blocked!==========\n",
#             "The\n",
#             "________________________________________________________________________________\n",
#             " rusty\n",
#             "________________________________________________________________________________\n",
#             " swing set groaned a mournful song as Elara pushed back and forth, her\n",
#             "________________________________________________________________________________\n",
#             " worn sneakers kicking up dust devils. It was the only sound in the forgotten corner of the park\n",
#             "________________________________________________________________________________\n",
#             ", a place even the stray dogs avoided. She clutched a worn, velvet box in her lap, its once vibrant purple faded to a dull lavender. Inside, nestled\n",
#             "________________________________________________________________________________\n",
#             " on a bed of frayed satin, was a single, tarnished silver locket.\n",
#             "\n",
#             "Today was the anniversary. Five years since Grandma Clara had vanished, leaving\n",
#             "________________________________________________________________________________\n",
#             "==========not blocked!==========\n",
#             " behind only this locket and a house full of unanswered questions. Elara visited every year, hoping for… well, she didn't know what. A sign? A memory? Anything.\n",
#             "\n",
#             "Grandma Clara had been a storyteller, weaving\n",
#             "________________________________________________________________________________\n",
#             " fantastical tales of hidden cities and talking animals. She’d filled Elara’s childhood with magic, making even the mundane feel extraordinary. The locket, she’d said, held a secret, a whisper of a forgotten world.\n",
#             "\n",
#             "Elara\n",
#             "________________________________________________________________________________\n",
#             " flipped open the locket. Inside, a miniature portrait of Grandma Clara, her eyes sparkling with mischief, and a tiny, dried flower, pressed so flat it was almost translucent. She ran a finger over the flower, a wave of sadness washing over her. The flower was a Forget-Me-Not.\n",
#             "\n",
#             "Suddenly, the\n",
#             "________________________________________________________________________________\n",
#             "==========not blocked!==========\n",
#             " air shimmered. A faint, melodic humming filled the air, growing louder with each swing of the rusty seat. Elara stopped, her heart pounding. The humming resonated with the locket in her hand, vibrating against her palm.\n",
#             "\n",
#             "As the humming reached a crescendo, the park around her seemed to fade. The rust\n",
#             "________________________________________________________________________________\n",
#             " on the swing set disappeared, replaced by gleaming, polished metal. The overgrown weeds transformed into a riot of vibrant flowers she'd never seen before. The grey, cloudy sky opened up to reveal a cerulean blue, dotted with puffy white clouds.\n",
#             "\n",
#             "Before her stood a path, paved with cobblestones and lined with\n",
#             "________________________________________________________________________________\n",
#             " trees whose leaves shimmered with an iridescent glow. The humming pulled her forward, a gentle but irresistible force.\n",
#             "\n",
#             "Hesitantly, Elara stepped onto the path. As she walked, the air grew warmer, filled with the scent of exotic blooms and the sound of cascading water. She saw creatures darting amongst the trees\n",
#             "________________________________________________________________________________\n",
#             "==========not blocked!==========\n",
#             ", creatures she only knew from Grandma Clara's stories – tiny winged sprites, furry creatures with glowing eyes, and elegant deer with antlers of pure light.\n",
#             "\n",
#             "Finally, she reached a clearing. In the center stood a grand oak tree, its branches reaching towards the sky like welcoming arms. Underneath the tree, sitting on a moss\n",
#             "________________________________________________________________________________\n",
#             "-covered stone, was Grandma Clara.\n",
#             "\n",
#             "She looked older, wiser, but her eyes held the same mischievous sparkle.\n",
#             "\n",
#             "“Elara, my darling,” she said, her voice a gentle melody. “I knew you would find your way.”\n",
#             "\n",
#             "Tears streamed down Elara’s face as she rushed forward\n",
#             "________________________________________________________________________________\n",
#             "==========not blocked!==========\n",
#             ", throwing her arms around her grandmother. The locket, still clutched in her hand, pulsed with a warm, comforting light.\n",
#             "\n",
#             "“But… where were you? What happened?” Elara managed to choke out.\n",
#             "\n",
#             "Grandma Clara smiled, a knowing glint in her eyes. “Some stories are meant\n",
#             "________________________________________________________________________________\n",
#             " to be lived, not just told,” she said, gesturing towards the fantastical world around them. “And some secrets… are meant to be discovered.”\n",
#             "\n",
#             "The adventure had just begun. The forgotten corner of the park had become a gateway, a promise of magic waiting to be unlocked. And Elara, finally reunited with her grandmother,\n",
#             "________________________________________________________________________________\n",
#             " was ready to embrace it all.\n",
#             "\n",
#             "________________________________________________________________________________\n"
#           ]
#         }
#       ],
#       "source": [
#         "import asyncio\n",
#         "\n",
#         "\n",
#         "async def get_response():\n",
#         "    async for chunk in await client.aio.models.generate_content_stream(\n",
#         "        model='gemini-2.5-flash',\n",
#         "        contents='Tell me a story in 500 words.'\n",
#         "    ):\n",
#         "        if chunk.text:\n",
#         "            print(chunk.text)\n",
#         "        print(\"_\" * 80)\n",
#         "\n",
#         "async def something_else():\n",
#         "    for i in range(5):\n",
#         "        print(\"==========not blocked!==========\")\n",
#         "        await asyncio.sleep(1)\n",
#         "\n",
#         "async def async_demo():\n",
#         "    # Create tasks for concurrent execution\n",
#         "    task1 = asyncio.create_task(get_response())\n",
#         "    task2 = asyncio.create_task(something_else())\n",
#         "    # Wait for both tasks to complete\n",
#         "    await asyncio.gather(task1, task2)\n",
#         "\n",
#         "# In IPython notebooks, you can await the coroutine directly:\n",
#         "await async_demo()"
#       ]
#     }
#   ],
#   "metadata": {
#     "colab": {
#       "name": "Streaming.ipynb",
#       "toc_visible": true
#     },
#     "google": {
#       "image_path": "/site-assets/images/share.png",
#       "keywords": [
#         "examples",
#         "googleai",
#         "samplecode",
#         "python",
#         "embed",
#         "function"
#       ]
#     },
#     "kernelspec": {
#       "display_name": "Python 3",
#       "name": "python3"
#     }
#   },
#   "nbformat": 4,
#   "nbformat_minor": 0
# }