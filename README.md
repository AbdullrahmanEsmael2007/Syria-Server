# Syria Server

Syria Server is a Python script that uses the OpenAI API to generate code based on human instructions. The script is designed to be run on a server, and it accepts HTTP requests with a JSON object containing the following parameters:

* `code`: The code that the AI should generate code based on.
* `lang`: The language of the code.
* `instructions`: The instructions for the AI to follow when generating code.

The script will then generate code based on the instructions, and return it in the response.

## Example Usage

To use the script, you can send a POST request to the server with the above parameters. For example, to generate code based on the instruction "Write unit test for bazClass", you could send the following request:
