import sys
import os
import subprocess
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

class App:
    def __init__(self):
        print("App initialized.")
        pass
    
    def run(self):
        print("App is running...")
        # gui_path = os.path.join(os.path.dirname(__file__), '..', 'src', 'gui', 'gui.py')
        # subprocess.Popen(["streamlit", "run", gui_path], shell=True)
    
    
if __name__ == "__main__":
    app = App()
    app.run()