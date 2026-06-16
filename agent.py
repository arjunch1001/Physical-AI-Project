import anthropic
import json
from datetime import datetime

client = anthropic.Anthropic()

def read_sensor(sensor_id):
    # fake sensor data — in a real system this would 
    # read from actual hardware
    sensors = {
        1: {"temperature": 23.1, "vibration": 0.02, "status": "normal"},
        2: {"temperature": 31.4, "vibration": 0.08, "status": "elevated"},
        3: {"temperature": 87.6, "vibration": 0.91, "status": "critical"},
        4: {"temperature": 24.2, "vibration": 0.03, "status": "normal"}
    }
    return sensors.get(sensor_id, {"error": "sensor not found"})

def log_event(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}\n"
    with open("agent_log.txt", "a") as f:
        f.write(log_entry)
    return {"logged": True, "entry": log_entry}

def send_alert(level, message):
    print(f"\n🚨 ALERT [{level.upper()}]: {message}\n")
    return {"alert_sent": True, "level": level, "message": message}


tools = [
    {
        "name": "read_sensor",
        "description": "Reads current data from a factory floor sensor. Use this to check sensor status, temperature, and vibration levels.",
        "input_schema": {
            "type": "object",
            "properties": {
                "sensor_id": {
                    "type": "integer",
                    "description": "The ID of the sensor to read. Valid IDs are 1, 2, 3, and 4."
                }
            },
            "required": ["sensor_id"]
        }
    },
    {
        "name": "log_event",
        "description": "Logs an event or finding to the monitoring log file. Use this to record what you discover during investigation.",
        "input_schema": {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "The message to log."
                }
            },
            "required": ["message"]
        }
    },
    {
        "name": "send_alert",
        "description": "Sends an alert to the operations team. Use this when you identify an issue requiring attention.",
        "input_schema": {
            "type": "object",
            "properties": {
                "level": {
                    "type": "string",
                    "enum": ["low", "medium", "critical"],
                    "description": "Severity level of the alert."
                },
                "message": {
                    "type": "string",
                    "description": "Description of the issue."
                }
            },
            "required": ["level", "message"]
        }
    }
]


def execute_tool(tool_name, tool_input):
    print(f"Executing tool: {tool_name} with input: {tool_input}")
    
    if tool_name == "read_sensor":
        return read_sensor(tool_input["sensor_id"])
    elif tool_name == "log_event":
        return log_event(tool_input["message"])
    elif tool_name == "send_alert":
        return send_alert(tool_input["level"], tool_input["message"])
    else:
        return {"error": f"unknown tool: {tool_name}"}
    


def run_agent(task):
    print(f"\nTask: {task}\n")
    print("="*50)
    
    messages = [{"role": "user", "content": task}]
    
    system_prompt = """You are a factory floor monitoring agent. 
You have tools to read sensors, log events, and send alerts.

When given a task:
1. Investigate thoroughly — check multiple sensors when relevant
2. Log your key findings
3. Send an alert at the appropriate severity level
4. Give a clear final summary of what you found and what you did

Always reason through what you find before deciding next steps."""

    while True:
        response = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=1024,
            system=system_prompt,
            tools=tools,
            messages=messages
        )
        
        print(f"\nClaude stop reason: {response.stop_reason}")
        
        # if Claude is done — print final answer and exit
        if response.stop_reason == "end_turn":
            final_answer = response.content[0].text
            print(f"\nFinal Answer: {final_answer}")
            print(f"\nFull message history had {len(messages)} turns")
            break
        
        # if Claude wants to use tools
        if response.stop_reason == "tool_use":
            # add Claude's response to history
            messages.append({
                "role": "assistant",
                "content": response.content
            })
            
            # execute every tool Claude requested
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    print(f"\nClaude wants to call: {block.name}")
                    result = execute_tool(block.name, block.input)
                    print(f"Result: {result}")
                    
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": json.dumps(result)
                    })
            
            # add results to history and loop
            messages.append({
                "role": "user",
                "content": tool_results
            })


if __name__ == '__main__':
	run_agent("Something seems off on the factory floor but I'm not sure what. Check everything and report back.")