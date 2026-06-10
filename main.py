import cv2
import json
import threading
import anthropic
import requests
from vision import get_scene_data

client = anthropic.Anthropic()
PI_URL = "http://10.0.0.155:5000"

latest_decision = {"action": "idle", "reason": "initializing"}
llm_running = False

SYSTEM_PROMPT = """You are the reasoning layer of a Physical AI system.
You receive data about objects detected by a camera.
Decide what action the physical system should take.

Use these rules:
- alert: a person is detected AND size_pct > 20 (they are close)
- track: a person is detected AND size_pct between 5 and 20 (they are at medium distance)
- idle: no person detected, or person is very far away (size_pct < 5)

You must always respond with valid JSON only. No explanation, no preamble.
Exactly this format: {"action": "alert", "reason": "..."}"""

def call_llm(scene_data):
    global latest_decision, llm_running
    try:
        prompt = f"Current scene: {json.dumps(scene_data)}\nWhat action should the physical system take?"
        response = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=256,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}]
        )
        raw = response.content[0].text
        try:
            latest_decision = json.loads(raw)
        except json.JSONDecodeError:
            latest_decision = {"action": "idle", "reason": "parse error"}
    except Exception as e:
        print(f"LLM error: {e}")
        latest_decision = {"action": "idle", "reason": f"api error: {str(e)}"}
    finally:
        llm_running = False

def send_to_pi(action):
    try:
        requests.post(
            f"{PI_URL}/command",
            json={"action": action},
            timeout=2
        )
    except requests.exceptions.RequestException as e:
        print(f"Pi unreachable: {e}")

def main():
    global llm_running
    cap = cv2.VideoCapture(0)
    frame_count = 0
    last_action = None

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        frame_count += 1

        if frame_count % 30 == 0 and not llm_running:
            scene = get_scene_data(frame)
            if scene['objects']:
                llm_running = True
                thread = threading.Thread(target=call_llm, args=(scene,))
                thread.daemon = True
                thread.start()

        current_action = latest_decision['action']
        if current_action != last_action:
            print(f"Decision: {latest_decision}")
            send_to_pi(current_action)
            last_action = current_action

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()