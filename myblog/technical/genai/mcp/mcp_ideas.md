# MCP using Python

## Steps to build 
- First build the python webservice project
- Clone the repo using `git clone https://github.com/modelcontextprotocol/quickstart-resources.git`
- Create a virtual env and activate using `source .venv/bin/activate`
- Install dependencies using
```bash
cd weather-server-python
pip install -e .
```
- SIDE NOTE:Since the project already has `pyproject.toml`, it helps in identifying package dependencies.
    - It can be generated using `hatch` or `poet`.
    - When you installed your package in development mode with`pip install -e .`, pip used this file to understand how to install your project and its dependencies.

## Steps to Add
- Enable Agent mode in VSCode
- create a file `.vscode/mcp.json`
- Click 'Add Server'
- Specify command and args as shown below, the final `mcp.json` should look like below:
```json
{
    "servers": {
        "my-mcp-server-fbd26a9b": {
            "type": "stdio",
            "command": "/Users/kkailasnath/projects/genai/mcp/quickstart-resources/.venv/bin/python3",
            "args": [
                "/Users/kkailasnath/projects/genai/mcp/quickstart-resources/weather-server-python/weather.py"
            ]
        }
    }
}
```
- Once this is enabled, you can see a button to 'Start' the MCP server.
- Click 'Start' and it should say 'MCP' Server started.
- Also, in the `Agent mode` Chat window, you should be able to see the two tools. 

### Testing
Now you can test your weather server by asking questions like:

- What's the weather forecast for latitude 37.7749 and longitude -122.4194?
- Are there any weather alerts in CA?
- What tools are available in this weather server?