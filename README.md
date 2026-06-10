\# Physical AI Capstone Project



A distributed Physical AI system where a laptop runs computer vision and LLM reasoning,

while a Raspberry Pi handles GPIO hardware control.



\## Architecture



Laptop (compute layer):

\- Webcam captures live video frames

\- YOLOv8 (nano) runs real-time object detection

\- Anthropic Claude reasons about detected objects

\- Decisions sent over HTTP to Pi



Raspberry Pi 3 (actuation layer):

\- Flask API receives JSON commands

\- PhysicalController drives servo motor via lgpio

\- alert() — servo sweeps, person detected close

\- track() — servo holds center, person at medium distance  

\- idle() — servo signal off, nothing detected



\## Files



\- main.py — laptop: main loop, vision, LLM integration

\- vision.py — laptop: YOLOv8 wrapper, get\_scene\_data()

\- app.py — Pi: Flask HTTP API

\- controller.py — Pi: PhysicalController class, lgpio servo control



\## Setup



Laptop:

pip install ultralytics opencv-python anthropic requests

export ANTHROPIC\_API\_KEY=your-key

python main.py



Raspberry Pi:

pip install flask lgpio gpiozero

python app.py



\## Key Decisions



\- Split architecture: Pi 3 retained by offloading ML to laptop

\- Direct lgpio over gpiozero: hardware PWM precision, prevents servo damage

\- Threading: LLM calls run in background, main loop never blocks

\- Explicit thresholds in system prompt: reliable LLM decisions for physical actuation

