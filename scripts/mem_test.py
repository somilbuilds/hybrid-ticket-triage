import os
import psutil
from app import get_agent

def print_mem(step):
    process = psutil.Process(os.getpid())
    print(f"{step}: {process.memory_info().rss / 1024 / 1024:.2f} MB")

print_mem("Startup")
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
import torch
torch.set_num_threads(1)
print_mem("After Torch Import")

agent = get_agent()
print_mem("After get_agent()")

row = {
    "Company": "HackerRank",
    "Subject": "Login username does not match",
    "Issue": "I am trying to log in but my username does not match my email address.",
}

details = agent.predict_details(row)
print_mem("After predict_details()")
