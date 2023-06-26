# BabyAGI ChatGPT Plugin (plus search)

This is a ChatGPT plugin based on the BabyAGI project by [@yoheinakajima]. This plugin adapts the original BabyAGI code to work as a plugin using Quart, an asynchronous web framework. I also added search via Google API. 

## Installation

To install the BabyAGI ChatGPT plugin on [Replit](https://replit.com/):

1. Make sure the following dependencies are added to the `.replit` file:

```bash
pip install openai quart quart-cors pinecone-client
```

(Alternatively, run this in shell)
```bash
poetry install
```

2. Replace the `OPENAI_API_KEY` and `PINECONE_API_KEY` and the rest of the variables.

```python
OPENAI_API_KEY = "your_openai_api_key_here"
PINECONE_API_KEY = "your_pinecone_api_key_here"
pinecone_environment="YOUR ENV",
table_name="YOUR TABLE NAME",
GOOGLE_API_KEY = ""
CUSTOM_SEARCH_ENGINE_ID = ""
```

3. Update your localhost link

4. Save and run the Repl.

## Usage

The plugin provides several API endpoints to interact with BabyAGI:

- `/set_objective`: Set the main objective for BabyAGI.
- `/add_task`: Add a task to the task list.
- `/get_task_list`: Retrieve the current task list.
- `/execute_next_task`: Execute the next task in the task list and create new tasks based on the result.


## Example

Here's an example of setting the objective, adding a task, and executing the next task using the BabyAGI ChatGPT plugin:

```python
import requests

base_url = "http://localhost:5001"  # Replace with the Repl URL if running on Replit

# Set the objective
objective = "Solve world hunger."
response = requests.post(f"{base_url}/set_objective", json={"objective": objective})
print(response.json())

# Add a task
task_name = "Develop a task list."
response = requests.post(f"{base_url}/add_task", json={"task_name": task_name})
print(response.json())

# Execute the next task
response = requests.post(f"{base_url}/execute_next_task")
print(response.json())
```

Make sure to replace `localhost:5001` with your Replit app URL when running on Replit.

## License

This plugin is based on the BabyAGI project by @yoheinakajima
([https://github.com/yoheinakajima)](https://github.com/yoheinakajima). Please refer to their repository for licensing information.

## Acknowledgments

This plugin is based on the BabyAGI project by [@yoheinakajima]([https://github.com/yoheinakajima)
A big thank you to the author for their original work.
