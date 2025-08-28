#!/usr/bin/env python
import sys
import warnings
import ssl
import os

from datetime import datetime

from webrag.crew import Webrag
from webrag.flow import WebragFlow, kickoff as flow_kickoff, plot as flow_plot

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

def run():
    """
    Run the crew directly.
    """
    inputs = {
        'topic': input('Enter topic: '),
        'current_year': str(datetime.now().year)
    }
    
    try:
        result = Webrag().crew().kickoff(inputs=inputs)
        print("✅ Crew execution completed!")
        return result
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")

def run_flow():
    """
    Run the WebRAG flow (recommended).
    """
    try:
        result = flow_kickoff()
        return result
    except Exception as e:
        raise Exception(f"An error occurred while running the flow: {e}")

def plot_flow():
    """
    Generate flow visualization.
    """
    try:
        flow_plot()
    except Exception as e:
        raise Exception(f"An error occurred while plotting the flow: {e}")


if __name__ == "__main__":
    run_flow()
    plot_flow()
