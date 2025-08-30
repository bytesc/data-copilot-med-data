import logging

from .tools.tools_def import engine, llm, query_database

from .tools.copilot.sql_code import get_db_info_prompt

from .tools.get_function_info import get_function_info

from .tools.copilot.utils.call_llm_test import call_llm


def get_cot_chat_prompt(question):
    # rag_ans = rag_from_policy_func(question,llm,engine)
    rag_ans = ""
    # print(rag_ans)

    knowledge = "\nBase knowledge: \n" + rag_ans + "\n"
    database = ""

    function_set, function_info, function_import = get_function_info(question, llm)
    # print(function_info)
    if function_info == "solved":
        return "solved", rag_ans, []
    print(function_info)

    if query_database in function_set:
        data_prompt = get_db_info_prompt(engine, simple=True)
        database = "\nThe database content: \n" + data_prompt + "\n"

    pre_prompt = """ 
If you think you can try to answer with your own knowledge and function call is not necessary, answer directly.
Else if you need to call multiple functions, please tell me how to solve the problem step by step with Natural language.
Else if there are some similar functions and you think it is hard to decide, please ask the user to choose.
Else if you need to call just one function, return a single word "one" without anything else.

Remind:
1. Do not mention code details.
2. If needed, the chain of thought should be simple, short and clear.
3. If used database, you should clarify the tables should be used!!!
4. Do not go through steps in detail!!!
5. Do not mention code detail, users are not specialists!!!
6. Please ask the user to choose if there are some similar functions !!!

You can use the following functions to solve the problem:
"""
    function_prompt = """ 
Here is the functions you can import and use:
"""
    example_ans = """
Example 1:
1. Retrieve Age Data from database.
2. Filter the Age Data.
3. Draw the Graph.

Example 2:
one

Example 3:
I need you to clarify .....

Example 4:
We have some different functions to solve the problem: 
- PlanA: first use `function_name1` to ... , then use `function_name2` to ...
- PlanB: use `function_name3` to ...
...
you can choose one of the approaches and provide more information needed.

"""

    cot_prompt = "question:" + question + knowledge + database + pre_prompt + \
                 function_prompt + str(function_info) + \
                 example_ans
    return cot_prompt, rag_ans, function_import


def get_cot_chat(question: str):
    cot_prompt, rag_ans, function_import = get_cot_chat_prompt(question)
    ans = call_llm(cot_prompt, llm)
    return ans.content
