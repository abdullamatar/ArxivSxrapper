# STD LIB
<<<<<<< HEAD
import json
import logging
import multiprocessing as mp
import os
import signal
from concurrent.futures import ThreadPoolExecutor, as_completed

=======
# import asyncio
# import subprocess
# import threading
# import queue
import json
import logging
import os
import signal

>>>>>>> 927fc54192b430379b74cd3c69be12c069fbb516
from dataclasses import dataclass
from typing import List

# autogen
import autogen
from autogen import ConversableAgent, GroupChat, gather_usage_summary
# hf
from datasets import load_from_disk

# A2A
# import lib.functions as functions
from agents.agent import EmbeddingRetrieverAgent, GCManager, marl
from agents.agent_conf import gcconf

<<<<<<< HEAD
=======

# TruLens
# from trulens_eval.tru_custom_app import instrument


# from autogen.agentchat.contrib.capabilities import context_handling
>>>>>>> 927fc54192b430379b74cd3c69be12c069fbb516

# TruLens
# from trulens_eval.tru_custom_app import instrument

logger = logging.getLogger("coordinator")

<<<<<<< HEAD
logging.getLogger("requests").propagate = False
logging.getLogger("urllib3").propagate = False

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


=======
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

>>>>>>> 927fc54192b430379b74cd3c69be12c069fbb516
logging.basicConfig(
    level=logging.INFO,
    # Get the root directory of the project
    filename=os.path.join(root_dir, "logs/coord_gc.log"),
<<<<<<< HEAD
    format="%(asctime)s <>|<> %(levelname)s <>|<> from mod %(module)s:\n%(message)s",
)

=======
    format="%(asctime)s  👁‍🗨  %(levelname)s  👁‍🗨 from mod %(module)s:\n%(message)s",
)

logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

"""
?ATTENTION:
Registering reply functions, and potentially further sublclassing the CodingAgent are the way to move forward I believe.
"""


@dataclass
class Chat:
    sender: str
    receiver: str
    message: str

>>>>>>> 927fc54192b430379b74cd3c69be12c069fbb516

class Coordinator:
    """Coordinate sequential multi-agent conversations"""

    def __init__(
        self,
        team_name: str,
        agents: List[autogen.ConversableAgent],
    ):
        self.team_name = team_name
        self.agents = agents
        self.messages = []

    def _reset_agents(self, agents: List[ConversableAgent]) -> None:
        [agent.reset() for agent in agents]

    def log_gc_messages(self, msgs: List[dict]) -> None:
        for m in msgs:
            agent_name = m.get("name", "Unknown")
            print(m)
<<<<<<< HEAD
            content = (
                m
                if isinstance(m, str)
                else m.get("content", "ERROR RETRIEVING MESSAGE CONTENT")
            )
=======
            content = m["content"] or "fail"
>>>>>>> 927fc54192b430379b74cd3c69be12c069fbb516
            logger.info(f"SENDER {agent_name}:\nCONTENT: {content}")

    # !
    # @instrument
    def code_gen_group_chat(self, prompt: str, task_idx, epochs: int = 5):
        """
        Run a group chat with the agents and generate code
        """
        self._reset_agents(self.agents)
        main_uprox, retriever, code_review, coding_llm = self.agents  # type: ignore
        retriever: EmbeddingRetrieverAgent

        gc = GroupChat(
            agents=[retriever, code_review, coding_llm],
            messages=[],
<<<<<<< HEAD
            max_round=epochs,
=======
            max_round=5,
>>>>>>> 927fc54192b430379b74cd3c69be12c069fbb516
            speaker_selection_method="auto",
            # allow_repeat_speaker=[coding_llm],
        )

        @main_uprox.register_for_execution()
        @coding_llm.register_for_execution()
        @code_review.register_for_execution()
        @code_review.register_for_llm(
            description="Retrieve additional information to complete the given task. Create a detailed query so that the retrieval is impactful in terms of information gained. Return several docs and use them in the context."
        )
        @coding_llm.register_for_llm(
            description="Retrieve additional information to complete the given task. Create a detailed query so that the retrieval is impactful in terms of information gained. Return several docs and use them in the context."
        )
        def retrieve_content(
            message: str,
            # n_results: int = 10,
            # retriever: ConversableAgent = retriever,
        ) -> str:
            # retriever.n_results = 7

            assert message, "Message for database query not parsed correctly"
            # logger.info(f"Retrieving content for the given QUERY: {message}")
            (
                update_context_case1,
                update_context_case2,
            ) = retriever._check_update_context(message=message)

            if (
                update_context_case1 or update_context_case2
            ) and retriever.update_context:
                retriever.problem = (
                    message if not hasattr(retriever, "problem") else retriever.problem
                )
                _, ret_msg = retriever._generate_retrieve_user_reply(messages=message)
            else:
                _context = {"problem": message}
                ret_msg = retriever.message_generator(retriever, None, _context)
                # ret_msg = retriever.generate_init_message(message=message, n_results=7)
            return ret_msg if ret_msg else message

        # TODO: https://github.com/olimoz/AI_Teams_AutoGen/blob/main/JupyterNotebooksForAutoGen.ipynb
        gcman = GCManager(groupchat=gc, llm_config=gcconf, tid=task_idx)

        # 16k token limits for gpt-3.5 family #The below token limitation stuff can be ignrored when using gpt3.5 see the function in agents.py file
        # it is a hacky, unstable work around as the below Transform was not working right when AutoGen released it and I had to change the code internally to get it to work. :).

        # However, there is no harm in trying to execute the below if running into token limit problems when testing models with smaller context windows :/.

        # ctx = context_handling.TransformChatHistory(
        #     transforms=[
        #         context_handling.MessageTokenLimiter(max_tokens_per_message=15000)
        #     ],
        # )

        # for agent in [main_uprox, code_review, coding_llm]:
        #     ctx.add_to_agent(agent)
        # ctx.add_to_agent(gcman)

        # init chat calls the main reply function registered with the gcman, which is the run_chat function def'd in the GCman class
        retriever.initiate_chat(
            gcman,
            message=retriever.message_generator,
            problem=prompt,
            # clear_history=False,
        )

        assert (
            gc.messages
        ), "Something has gone awry..."  # This assertion will almost certainly never fail.

        self.log_gc_messages(gc.messages)

        combined_stats = {
            "task_description": prompt,
            "usage_stats": {},
            "exe_feedback": [],
        }
        # all_agents = self.agents + [gcman]
        total, _ = gather_usage_summary(self.agents + [gcman])
        combined_stats["usage_stats"] = total
        combined_stats["exe_feedback"] = gcman.execution_feedback_list
        combined_stats["exit_codes"] = [
            feedback["exit_code"] for feedback in gcman.execution_feedback_list
        ]
        combined_stats["task_idx"] = task_idx + 1

<<<<<<< HEAD
        with open("mlquart4-gc.jsonl", "a") as f:
=======
        combined_stats["exit_codes"] = exit_codes
        with open("agent_runs.jsonl", "a") as f:
>>>>>>> 927fc54192b430379b74cd3c69be12c069fbb516
            f.write(json.dumps(combined_stats) + "\n")

        return combined_stats


class TimeoutException(Exception):
    pass


def handler(signum, frame):
    raise TimeoutException("Prompt skipped due to timeout")


signal.signal(signal.SIGALRM, handler)


def mp_execute_task(task_queue, result_queue):
    while not task_queue.empty():
        try:
            task = task_queue.get_nowait()
            if task is None:
                break

            signal.alarm(300)

            result = Coordinator(
                team_name="test",
                agents=marl(collection_name="MLBench_papers"),
            ).code_gen_group_chat(
                f"Here is some information from a readme related to the task at hand, this information is more than enough to successfully implement the following task and is of utmost importance, use it as guidance and a starting point to build from:\n {task['oracle']}\nTo prepare the execution environment please run this command: {task['prefix_code']}\n"
                f"Here is the task description:\n{task['instruction']}\nAvoid any executing things that require standard inputs to given, such as an API key or token.\n"
                f"The type of output expected for this task is {task['type']}.",
                epochs=7,
                task_idx=task["id"],
            )

            signal.alarm(0)

            logger.info(f"Task {task['id']} completed successfully.")
            result_queue.put(result)

        except TimeoutException:
            logger.info(f"Skipping task {task['id']} due to timeout")
        except Exception as e:
            logger.error(f"Error in task {task['id']}: {str(e)}")

    result_queue.put("&done&")


def listener(result_queue, output_file):
    with open(output_file, "a") as f:
        while True:
            result = result_queue.get()
            if result == "&done&":
                break
            f.write(json.dumps(result) + "\n")
            f.flush()


def run_multiproc(
    mlbench, subset, num_workers=4, output_file="agent_runs_multiproc.jsonl"
):
    task_queue = mp.Queue()
    result_queue = mp.Queue()

    for task in mlbench[subset]:
        task_queue.put(task)
        # break

    listener_process = mp.Process(target=listener, args=(result_queue, output_file))
    listener_process.start()

    worker_processes = []
    for _ in range(num_workers):
        worker = mp.Process(target=mp_execute_task, args=(task_queue, result_queue))
        worker.start()
        worker_processes.append(worker)

    # wait for workers to finish
    for worker in worker_processes:
        worker.join()

    result_queue.put(None)
    listener_process.join()


def process_task(task, log_dir="../logs", epochs=7):
    try:
        signal.alarm(300)  # Set task timeout

        result = Coordinator(
            team_name="test",
            agents=marl(collection_name="MLBench_papers"),
        ).code_gen_group_chat(
            f"Here is some information from a readme related to the task at hand, this information is more than enough to successfully implement the following task and is of utmost importance, use it as guidance and a starting point to build from:\n {task['oracle']}\nTo prepare the execution environment please run this command: {task['prefix_code']}\n"
            f"Here is the task description:\n{task['instruction']}\nAvoid any executing things that require standard inputs to given, such as an API key or token.\n"
            f"The type of output expected for this task is {task['type']}.",
            epochs=epochs,
            task_idx=task["id"],
        )

        signal.alarm(0)  # Disable the alarm

        logger.info(f"Task {task['id']} completed successfully.")
        return result

    except TimeoutException:
        logger.info(f"Skipping task {task['id']} due to timeout")
        return None
    except Exception as e:
        logger.error(f"Error in task {task['id']}: {str(e)}")
        return None


def run_multiproc2(
    mlbench, subset, output_file="agent_runs_multiproc.jsonl", max_workers=4
):
    tasks = mlbench[subset]
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(process_task, task): task for task in tasks}
        with open(output_file, "a") as f:
            for future in as_completed(futures):
                result = future.result()
                if result is not None:
                    f.write(json.dumps(result) + "\n")
                    f.flush()

    logger.info(f"Finished processing {len(results)} tasks.")


def execute_task(mlbench, iteration):
    # function to skip over blocking stdin prompts for whatever reason (i,e. an api key being required via some library).
    try:
        signal.alarm(300)

        Coordinator(
            team_name="test",
            agents=marl(collection_name="MLBench_papers"),
        ).code_gen_group_chat(
            f"Here is some information from a readme related to the task at hand, this information is more than enough to successful implement the following and task and is of utmost importance, use it as guidance and a starting point to build from:\n {mlbench['quarter'][iteration]['oracle']}\n"
            f"Here is the task description:\n{mlbench['quarter'][iteration]['instruction']}\n"
            f"The type of output expected for this task is {mlbench['quarter'][iteration]['type']}",
            epochs=7,
            task_idx=mlbench["quarter"][iteration]["id"],
        )

        signal.alarm(0)
        logger.info(f"Iteration {iteration + 1} completed successfully.")
        # return results
    except TimeoutException:
        logger.info(f"Skipping prompt for iteration {iteration + 1}")


class TimeoutException(Exception):
    pass


def handler(signum, frame):
    raise TimeoutException("Prompt skipped due to timeout")


signal.signal(signal.SIGALRM, handler)


def perform_iteration(mlbench, iteration):
    # function to skip over blocking stdin prompts for whatever reason (i,e. api being required via some library).
    try:
        signal.alarm(80)

        Coordinator(
            team_name="test",
            agents=marl(collection_name="MLBench_papers"),
        ).code_gen_group_chat(
            f"Here is some information from a readme related to the task at hand:\n {mlbench['quarter'][iteration]['oracle']}\n"
            f"Here is the task description:\n{mlbench['quarter'][iteration]['instruction']}\n"
            f"The type of output expected for this task is {mlbench['quarter'][iteration]['type']}"
        )

        signal.alarm(0)
        logger.info(f"Iteration {iteration + 1} completed successfully.")
    except TimeoutException:
        logger.info(f"Skipping prompt for iteration {iteration + 1}")


if __name__ == "__main__":
    mlbench = load_from_disk(root_dir + "/lib/eval/MLBench/datasets/")

    # mlbench = load_from_disk(root_dir + "/lib/eval/MLBench/datasets/")
    # run_multiproc2(
    #     mlbench,
    #     "quarter",
    #     # max_workers=5,
    #     output_file="mlquart3.jsonl",
    # )

    # process_in_batches(mlbench)
    for i in range(len(mlbench["quarter"])):
        execute_task(mlbench, i)

    mlbench = load_from_disk(root_dir + "/lib/eval/MLBench/datasets/")

    # with open("./temp.jsonl", "r") as f:
    #     tasks = [json.loads(line) for line in f]
    # manager = mp.Manager()
    # q = manager.Queue()
    # lock = manager.Lock()

<<<<<<< HEAD
    # listener_proc = mp.Process(target=listener, args=(q, "agent_runs_multiproc.jsonl"))
    # listener_proc.start()
    # file_pool = mp.Pool(1)
    # file_pool.apply_async(listener, (q, "agent_runs_multiproc.jsonl"))
    # pool = mp.Pool(16)
    # procs = []
    # for i in range(len(mlbench["quarter"][:15])):
    # p = mp.Process(target=execute_task, args=(mlbench, i, q))
    # procs.append(p)
    # p.start()
    # for pross in procs:
    # pross.join()
    # job.get()

    # q.put("#done#")
    # pool.close()
    # pool.join()
    # file_pool.close()
    # file_pool.join()
    # listener_proc.join()
    # exe_exe_task2()

    # # with Manager() as manager:
    # #     results = manager.list()
    # #     with concurrent.futures.ProcessPoolExecutor(max_workers=7) as executor:
    # #         futures = [
    # #             executor.submit(execute_task, mlbench, i)
    # #             for i in range(len(mlbench["quarter"][:15]))
    # #         ]
    # #         for future in concurrent.futures.as_completed(futures):
    # #             try:
    # #                 result = future.result()
    # #                 if result:
    # #                     results.append(result)
    # #                     logger.info(f"Result for {result['task_idx']}: {result}")
    # #             except Exception as e:
    # #                 logger.error(f"ERROR: {e}")

    #     with open("agent_runs_multiproc.jsonl", "a") as f:
    #         for result in results:
    #             f.write(json.dumps(result) + "\n")

# def process_batch(mlbench, start_idx, end_idx):
#     """Process a specific batch of tasks."""
#     for i in range(start_idx, end_idx):
#         execute_task(mlbench, i)


# def batch_processing_parallel(mlbench, batch_size):
#     """Process the entire dataset in batches using parallel execution."""
#     total_tasks = len(mlbench["quarter"])
#     with concurrent.futures.ThreadPoolExecutor() as executor:
#         futures = []
#         for i in range(0, total_tasks, batch_size):
#             start_idx = i
#             end_idx = min(i + batch_size, total_tasks)
#             futures.append(executor.submit(process_batch, mlbench, start_idx, end_idx))

#         for future in concurrent.futures.as_completed(futures):
#             future.result()
=======
    # for i in range(len(mlbench["quarter"][20])):
    perform_iteration(mlbench, 20)
    # Function to read output from a subprocess without blocking
    # def enqueue_output(out, q):
    #     for line in iter(out.readline, b""):
    #         q.put(line.decode("utf-8"))
    #     out.close()

    # def run_task(task_instruction):
    #     script_content = f"""
    # import subprocess

    # def main():
    # Coordinator(
    #     team_name="test",
    #     agents=marl(collection_name="MLBench_papers"),
    # ).code_gen_group_chat("retrieve some content about AC-Gans")

    # if __name__ == "__main__":
    #     main()
    # """
    #     # Write the script content to a temporary file
    #     script_file = "temp_task_script.py"
    #     with open(script_file, "w") as f:
    #         f.write(script_content)

    #     # Start the subprocess
    #     process = subprocess.Popen(
    #         ["python", script_file],
    #         stdout=subprocess.PIPE,
    #         stderr=subprocess.PIPE,
    #         stdin=subprocess.PIPE,
    #         bufsize=1,
    #         universal_newlines=True,
    #     )

    #     # Create a queue to hold the subprocess output
    #     q = queue.Queue()
    #     t = threading.Thread(target=enqueue_output, args=(process.stdout, q))
    #     t.daemon = True  # Thread dies with the program
    #     t.start()

    #     # Monitor the subprocess output
    #     while True:
    #         try:
    #             line = q.get_nowait()  # Non-blocking read
    #         except queue.Empty:
    #             if process.poll() is not None:
    #                 break  # Process finished
    #             time.sleep(0.1)
    #         else:
    #             print(line, end="")  # Print the output

    #             # Check if the line contains a text prompt
    #             if "Enter" in line or "Prompt" in line:
    #                 print("Detected prompt, terminating subprocess...")
    #                 process.terminate()
    #                 return False  # Indicate the round should be skipped

    #     # Wait for the process to finish
    #     process.wait()
    #     return True  # Indicate the round completed successfully

    # # mlbench = load_from_disk(root_dir + "/lib/eval/MLBench/datasets/")

    # results = []

    # for i in range(len(mlbench["quarter"])):
    #     task_instruction = (
    #         f"Here is some information from a readme related to the task at hand:\n {mlbench['quarter'][i]['oracle']}\n"
    #         f"Here is the task description:\n{mlbench['quarter'][i]['instruction']}\n"
    #         f"The type of output expected for this task is {mlbench['quarter'][i]['type']}"
    #     )
    #     success = run_task(task_instruction)
    #     if success:
    #         print(f"Task {i + 1} completed successfully.")
    #         results.append(True)
    #     else:
    #         print(f"Task {i + 1} skipped due to prompt.")
    #         results.append(False)
    #     logger.info(f"Results: {results}")

##################old########################
# for task in tasks:
#     Coordinator(
#         team_name="test",
#         agents=marl(collection_name="cs_demo"),
#     ).code_gen_group_chat(task)
# Coordinator(
#     team_name="test",
#     agents=marl(collection_name="eval4_db_guidingpretraining"),
# ).code_gen_group_chat(
#     "Show me how an RL agents exploration can be guiding with LLM priors according to the paper. Create a minimal example in a self-contained python file that must be executable and produce an output, do not make any assumptions or fill any functions with the pass keyword or ellipses."
# )
>>>>>>> 927fc54192b430379b74cd3c69be12c069fbb516
