import json
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from schema.complexity_schema import ComplexitySchema

def load_openai_key(key_file="keys.json"):
    """
    Reads OpenAI key from a JSON file.
    Expects a file with contents like:
    {
      "openai_api_key": "YOUR_KEY"
    }
    Returns:
        str or None: The OpenAI API key, or None if not found or failed to load.
    """
    try:
        with open(key_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("openai_api_key")
    except Exception as e:
        print(f"Failed to read OpenAI key from {key_file}: {e}")
        return None

def analyze_file_with_ai(file_path, code):
    """
    Uses LangChain's ChatOpenAI to determine the cyclomatic complexity of any code snippet, 
    for any programming language. Returns only the complexity or a JSON mapping of complexities.
    
    Args:
      file_path (str): the path to the file (used for logging/errors)
      code (str): the file contents
    
    Returns:
      str, dict, or None: The complexity result from the AI or None on error.
    """
    prompt = (
        "You are an expert code reviewer. Analyze the following code in any programming language and "
        "return ONLY the cyclomatic complexity as an integer. Read the .gitignore file if present and skip ignored files. "
        "Also skip any files in folders starting with a dot. "
        "Here is the code:\n\n"
        f"{code}\n"
    )
    try:
        openai_api_key = load_openai_key()
        if not openai_api_key:
            print("OpenAI API key not found.")
            return None
        
        chat_model = ChatOpenAI(
            temperature=0,
            model_name="gpt-4o",
            openai_api_key=openai_api_key
        )
        llm = chat_model.with_structured_output(ComplexitySchema)
        messages = [
            SystemMessage(content="You are a helpful assistant."),
            HumanMessage(content=prompt)
        ]
        result = llm.invoke(messages)

        return result.json()
    except Exception as e:
        print(f"Error calling LangChain for {file_path}: {e}")
        return None

def initialize_openai_api(key_file="keys.json"):
    """
    Loads the OpenAI API key from the given file.
    Returns True if key is found, otherwise False.
    """
    openai_api_key = load_openai_key(key_file=key_file)
    if not openai_api_key:
        print("OpenAI API key not found. Please place your key in keys.json ('openai_api_key').")
        return False
    return True
