import re
import ast
import operator
import json
from datetime import datetime

# ==========================================
# SAFE CALCULATOR TOOL IMPLEMENTATION
# ==========================================

# Map AST operators to safe Python operators
SAFE_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Mod: operator.mod,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}

def safe_ast_eval(node):
    """
    Recursively evaluate an AST node, allowing only safe arithmetic operations and constants.
    """
    # For Python < 3.8
    if hasattr(ast, 'Num') and isinstance(node, getattr(ast, 'Num')):
        return node.n
    # For Python >= 3.8
    elif isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value
        raise TypeError(f"Unsupported constant type: {type(node.value)}")
    elif isinstance(node, ast.BinOp):
        left = safe_ast_eval(node.left)
        right = safe_ast_eval(node.right)
        op_type = type(node.op)
        if op_type in SAFE_OPERATORS:
            if op_type in (ast.Div, ast.Mod) and right == 0:
                raise ZeroDivisionError("Division or modulo by zero")
            return SAFE_OPERATORS[op_type](left, right)
        raise TypeError(f"Unsupported binary operator: {op_type}")
    elif isinstance(node, ast.UnaryOp):
        operand = safe_ast_eval(node.operand)
        op_type = type(node.op)
        if op_type in SAFE_OPERATORS:
            return SAFE_OPERATORS[op_type](operand)
        raise TypeError(f"Unsupported unary operator: {op_type}")
    else:
        raise TypeError(f"Unsupported expression node: {type(node)}")

def run_calculator(question_or_ctx) -> str:
    """
    Extracts the arithmetic expression from the question and evaluates it.
    """
    question = question_or_ctx.question if hasattr(question_or_ctx, 'question') else question_or_ctx
    # Attempt to isolate the math expression
    # Remove common conversational prefixes/suffixes
    cleaned = question.strip()
    q_lower = cleaned.lower()
    for prefix in ["what is", "calculate", "compute", "evaluate", "solve"]:
        if q_lower.startswith(prefix):
            cleaned = cleaned[len(prefix):].strip()
            q_lower = cleaned.lower()
            
    cleaned = cleaned.rstrip("?=")
    
    # Remove alphabetical words/characters, keeping operators and numbers
    # We want to extract only the mathematical part
    cleaned = re.sub(r'[a-zA-Z\?\s\=]', '', cleaned)
    
    if not cleaned:
        return "Error: No arithmetic expression could be extracted."
        
    try:
        tree = ast.parse(cleaned, mode='eval')
        result = safe_ast_eval(tree.body)
        
        # Nicely format float results that represent whole numbers
        if isinstance(result, float) and result.is_integer():
            result = int(result)
            
        return str(result)
    except ZeroDivisionError:
        return "Error: Division or modulo by zero."
    except Exception as e:
        return f"Error: Invalid mathematical expression ({str(e)})."


# ==========================================
# DATE & TIME TOOL IMPLEMENTATION
# ==========================================

def run_date_time(question_or_ctx) -> str:
    """
    Returns current date, current time, and/or day of week.
    """
    question = question_or_ctx.question if hasattr(question_or_ctx, 'question') else question_or_ctx
    q = question.lower()
    now = datetime.now()
    
    results = []
    
    # Match specific requests
    if "date" in q or "today" in q:
        results.append(f"Current Date: {now.strftime('%Y-%m-%d')}")
    if "time" in q or "clock" in q or "now" in q:
        results.append(f"Current Time: {now.strftime('%H:%M:%S')}")
    if "day" in q:
        results.append(f"Day of Week: {now.strftime('%A')}")
        
    # If no specific key word triggered, return all three
    if not results:
        results = [
            f"Current Date: {now.strftime('%Y-%m-%d')}",
            f"Current Time: {now.strftime('%H:%M:%S')}",
            f"Day of Week: {now.strftime('%A')}"
        ]
        
    return "\n".join(results)


# ==========================================
# JSON FORMATTER TOOL IMPLEMENTATION
# ==========================================

def run_json_formatter(question_or_ctx) -> str:
    """
    Parses, validates, and pretty-prints the JSON content extracted from the query.
    """
    question = question_or_ctx.question if hasattr(question_or_ctx, 'question') else question_or_ctx
    # Find start and end bounds of JSON content
    start_curly = question.find('{')
    start_bracket = question.find('[')
    
    if start_curly == -1 and start_bracket == -1:
        return "Error: No JSON content found in the query. (JSON must be enclosed in '{ }' or '[ ]')"
        
    if start_curly != -1 and (start_bracket == -1 or start_curly < start_bracket):
        start = start_curly
        end = question.rfind('}')
    else:
        start = start_bracket
        end = question.rfind(']')
        
    if start == -1 or end == -1 or end <= start:
        return "Error: Incomplete JSON delimiters found in the query."
        
    json_str = question[start:end+1]
    
    try:
        parsed = json.loads(json_str)
        pretty = json.dumps(parsed, indent=4)
        return f"JSON is VALID.\nFormatted JSON:\n{pretty}"
    except json.JSONDecodeError as e:
        return f"JSON is INVALID.\nError details: {str(e)}"


# ==========================================
# TEXT STATISTICS TOOL IMPLEMENTATION
# ==========================================

def run_text_statistics(question_or_ctx) -> str:
    """
    Calculates word, character, and line counts of the target text.
    """
    is_context = hasattr(question_or_ctx, 'question')
    if is_context:
        ctx = question_or_ctx
        # Prioritize draft_answer if knowledge agent generated text
        text = ctx.draft_answer if ctx.draft_answer else ctx.question
    else:
        text = question_or_ctx

    is_from_draft = is_context and bool(question_or_ctx.draft_answer)

    if not is_from_draft:
        q_lower = text.lower()
        extracted = ""
        # Attempt to extract text after a colon, quote, or specific indicator
        for indicator in [":", "text is", "string is", "for"]:
            idx = q_lower.find(indicator)
            if idx != -1:
                extracted = text[idx + len(indicator):].strip()
                break
                
        # Clean quotes if any
        if extracted.startswith(('"', "'")) and extracted.endswith(('"', "'")):
            extracted = extracted[1:-1].strip()
            
        if not extracted:
            # If no delimiter found, remove instruction prefix and use the rest of the question
            extracted = text
            prefixes = [
                "how many words are in this text",
                "how many characters are in this text",
                "how many lines are in this text",
                "word count of",
                "character count of",
                "line count of",
                "text statistics for",
                "text statistics of"
            ]
            for prefix in prefixes:
                if q_lower.startswith(prefix):
                    extracted = text[len(prefix):].strip()
                    break
                    
        # Clean up formatting
        text = extracted.lstrip(" :\"'").rstrip(" \"'")
    
    if not text:
        return "Error: No text provided for statistics."
        
    words = len(text.split())
    chars = len(text)
    lines = len(text.splitlines()) if text else 0
    
    return (
        f"Text Statistics:\n"
        f"- Word Count: {words}\n"
        f"- Character Count: {chars}\n"
        f"- Line Count: {lines}"
    )


# ==========================================
# TOOL REGISTRY AND DISPATCHER
# ==========================================

class Tool:
    def __init__(self, name, matcher, runner):
        self.name = name
        self.matcher = matcher
        self.runner = runner

# Define matches for registry selection
def is_math_query(q: str) -> bool:
    # Match standard calculator equations e.g. "457*328", "(1+2)*3", etc.
    cleaned = re.sub(r'[a-zA-Z\?\s\=]', '', q)
    if not cleaned:
        return False
    # Check if it looks like math (has digits/operators and no other characters)
    has_digit = any(c.isdigit() for c in cleaned)
    has_operator = any(c in '+-*/%()' for c in cleaned)
    all_valid = all(c in '0123456789+-*/%().' for c in cleaned)
    return has_digit and has_operator and all_valid

def is_date_time_query(q: str) -> bool:
    q_lower = q.lower()
    return any(kw in q_lower for kw in ["date", "time", "day", "today", "clock"])

def is_json_query(q: str) -> bool:
    q_lower = q.lower()
    if "json" in q_lower:
        return True
    if '{' in q and '}' in q:
        return True
    if '[' in q and ']' in q:
        return True
    return False

def is_text_stats_query(q: str) -> bool:
    q_lower = q.lower()
    keywords = [
        "word count", "character count", "line count", 
        "text statistics", "words are in", "characters are in", 
        "lines are in", "count the words", "count the characters",
        "count", "statistics", "stats"
    ]
    return any(kw in q_lower for kw in keywords)

# The tool registry
TOOL_REGISTRY = [
    Tool("Calculator", is_math_query, run_calculator),
    Tool("Date & Time", is_date_time_query, run_date_time),
    Tool("JSON Formatter", is_json_query, run_json_formatter),
    Tool("Text Statistics", is_text_stats_query, run_text_statistics),
]

def run_tools(context_or_question) -> str:
    """
    Dispatches a query to the first matching tool from the registry.
    Supports ExecutionContext and backward compatible string questions.
    """
    if hasattr(context_or_question, 'question'):
        ctx = context_or_question
        for tool in TOOL_REGISTRY:
            if tool.matcher(ctx.question):
                import time
                start_t = time.time()
                res = tool.runner(ctx)
                duration_ms = (time.time() - start_t) * 1000.0
                ctx.tool_outputs[tool.name] = res
                ctx.debug_metadata["tool"] = {
                    "selected_tool": tool.name,
                    "execution_time_ms": duration_ms
                }
                # Mirror or append to draft_answer so subsequent agents (like critic) can see it
                if ctx.draft_answer:
                    ctx.draft_answer = f"{ctx.draft_answer}\n\n{res}"
                else:
                    ctx.draft_answer = res
                return res
        return "Error: No matching tool found in registry."
    else:
        for tool in TOOL_REGISTRY:
            if tool.matcher(context_or_question):
                return tool.runner(context_or_question)
        return "Error: No matching tool found in registry."
