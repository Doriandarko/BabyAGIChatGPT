from typing import Dict, List
from quart import Quart, request, jsonify, send_file
import quart_cors
from collections import deque
import openai
import pinecone

app = Quart(__name__)
quart_cors.cors(app, allow_origin="https://chat.openai.com")

# The rest of your code...

# Set API Keys
OPENAI_API_KEY = ""
PINECONE_API_KEY = ""


from collections import deque
import openai
import pinecone
from typing import Dict, List

class BabyAGI:
    def __init__(self,
                 openai_api_key,
                 pinecone_api_key,
                 pinecone_environment="YOUR ENV",
                 table_name="YOUR TABLE NAME",
                 first_task="Develop a task list"):
        self.openai_api_key = openai_api_key
        self.pinecone_api_key = pinecone_api_key
        self.pinecone_environment = pinecone_environment
        self.task_list = deque([])
        self.objective = ""
        self.table_name = table_name
        self.first_task = first_task

        openai.api_key = self.openai_api_key
        pinecone.init(api_key=self.pinecone_api_key,
                      environment=self.pinecone_environment)

    def set_objective(self, objective):
        self.objective = objective

    def add_task(self, task: Dict):
        if not self.task_list:
            task_id = 1
        else:
            task_id = self.task_list[-1]["task_id"] + 1
        task.update({"task_id": task_id})
        self.task_list.append(task)

    def get_ada_embedding(self, text):
        text = text.replace("\n", " ")
        return openai.Embedding.create(
            input=[text], model="text-embedding-ada-002")["data"][0]["embedding"]

    def task_creation_agent(self, objective: str, result: str, task_description: str, task_list: List[str]):
        prompt = f"You are an task creation AI that uses the result of an execution agent to create new tasks with the following objective: {objective}, The last completed task has the result: {result}. This result was based on this task description: {task_description}. These are incomplete tasks: {', '.join(task_list)}. Based on the result, create new tasks to be completed by the AI system that do not overlap with incomplete tasks. Return the tasks as an array."

        response = openai.Completion.create(engine="text-davinci-003", prompt=prompt, temperature=0.5, max_tokens=100, top_p=1, frequency_penalty=0, presence_penalty=0)
        new_tasks = response.choices[0].text.strip().split('\n')
        return [{"task_name": task_name} for task_name in new_tasks]

    def execution_agent(self, objective: str, task: str) -> str:
        context = self.context_agent(index="test-table", query=objective, n=5)

        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=f"You are an AI who performs one task based on the following objective: {objective}. Your task: {task}\nResponse:",
            temperature=0.7,
            max_tokens=2000,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        return response.choices[0].text.strip()

    def context_agent(self, query: str, index: str, n: int):
        query_embedding = self.get_ada_embedding(query)
        index = pinecone.Index(index_name=index)
        results = index.query(query_embedding, top_k=n, include_metadata=True)
        sorted_results = sorted(results.matches, key=lambda x: x.score, reverse=True)
        return [(str(item.metadata['task'])) for item in sorted_results]

    def clear_task_list(self):
        self.task_list.clear()
        self.task_id_counter = 0

baby_agi = BabyAGI(OPENAI_API_KEY,
                   PINECONE_API_KEY,
                   table_name="test-table",
                   first_task="Develop a task list")


@app.route("/set_objective", methods=["POST"])
async def set_objective():
    global baby_agi
    data = await request.json
    objective = data["objective"]
    baby_agi.clear_task_list()  # Clear the task list and reset the task ID counter
    baby_agi.set_objective(objective)
    return jsonify({"status": "Objective set", "objective": objective})



@app.route("/add_task", methods=["POST"])
async def add_task():
  global baby_agi
  data = await request.json
  task_name = data["task_name"]
  task = {"task_name": task_name}
  baby_agi.add_task(task)
  return jsonify({"status": "Task added"})


@app.route("/execute_next_task", methods=["POST"])
async def execute_next_task():
  global baby_agi
  if not baby_agi.task_list:
    return jsonify({"status": "No tasks in the list"})

  task = baby_agi.task_list.popleft()
  result = baby_agi.execution_agent(baby_agi.objective, task["task_name"])

  new_tasks = baby_agi.task_creation_agent(
    baby_agi.objective, result, task["task_name"],
    [t["task_name"] for t in baby_agi.task_list])
  for new_task in new_tasks:
    baby_agi.add_task(new_task)

  response = {
    "task_id": task["task_id"],
    "task_name": task["task_name"],
    "result": result,
    "new_tasks": new_tasks,
  }
  return jsonify(response)


@app.route("/get_task_list", methods=["GET"])
async def get_task_list():
  global baby_agi
  task_list = [task["task_name"] for task in baby_agi.task_list]
  return jsonify({"task_list": task_list})


@app.route("/openapi.yaml", methods=["GET"])
async def get_openapi_yaml():
  return await send_file("openapi.yaml",
                         mimetype="application/vnd.oai.openapi")


@app.route("/logo.png", methods=["GET"])
async def get_logo():
  return await send_file("logo.png", mimetype="image/png")


@app.route("/.well-known/ai-plugin.json", methods=["GET"])
async def get_ai_plugin_json():
  return await send_file("ai-plugin.json", mimetype="application/json")


if __name__ == "__main__":
  app.run(debug=True, host="0.0.0.0", port=5001)
