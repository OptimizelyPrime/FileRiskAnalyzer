from pydantic import BaseModel, Field

class ComplexitySchema(BaseModel):
    class_name: str = Field(description="The class name")
    function_name: str = Field(description="The function name")
    complexity: int = Field(description="The cyclomatic complexity of the function")