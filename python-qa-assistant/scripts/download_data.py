#!/usr/bin/env python3
"""
Python script to download and prepare the Kaggle Stack Overflow Python Questions & Answers dataset.
Dataset URL: https://www.kaggle.com/datasets/stackoverflow/pythonquestions
"""

import os
import sys
import zipfile
from pathlib import Path

# Setup paths relative to script
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "raw"

def main():
    print("=" * 60)
    print("STACK OVERFLOW PYTHON QA DATASET DOWNLOADER")
    print("=" * 60)

    # Ensure output directory exists
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Check for Kaggle Credentials
    kaggle_username = os.environ.get("KAGGLE_USERNAME")
    kaggle_key = os.environ.get("KAGGLE_KEY")

    # Check if .kaggle/kaggle.json exists in user home directory
    home_kaggle = Path.home() / ".kaggle" / "kaggle.json"
    has_credentials = (kaggle_username and kaggle_key) or home_kaggle.exists()

    if not has_credentials:
        print("\n[!] WARNING: Kaggle credentials not found in environment or ~/.kaggle/kaggle.json")
        print("\nTo download the Stack Overflow Python Question & Answers dataset directly, please setup Kaggle credentials:")
        print("1. Go to https://www.kaggle.com/settings")
        print("2. Click 'Create New Token' to download kaggle.json")
        print("3. Either:")
        print("   - Set environment variables:")
        print("     export KAGGLE_USERNAME=your_username")
        print("     export KAGGLE_KEY=your_api_key")
        print("   - Place the file at ~/.kaggle/kaggle.json")
        print("\nCreating placeholder simulated small data files for development/testing instead...\n")
        
        create_simulated_dataset()
        sys.exit(0)

    try:
        import kaggle
    except ImportError:
        print("[!] kaggle package not installed. Installing standard mock data files...")
        create_simulated_dataset()
        sys.exit(0)

    dataset_slug = "stackoverflow/pythonquestions"
    print(f"\n[*] Authenticating with Kaggle API...")
    try:
        kaggle.api.authenticate()
        print(f"[*] Downloading '{dataset_slug}' to {DATA_DIR}...")
        kaggle.api.dataset_download_files(dataset_slug, path=str(DATA_DIR), unzip=False)
        
        zip_path = DATA_DIR / "pythonquestions.zip"
        if zip_path.exists():
            print(f"[*] Unzipping data package...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(DATA_DIR)
            zip_path.unlink()  # Clean up zip file
            print("[+] Unzipped dataset successfully!")
        
        verify_files()

    except Exception as e:
        print(f"\n[!] Failed to download via Kaggle API: {e}")
        print("[*] Creating simulated workspace dataset files for high fidelity development tests...")
        create_simulated_dataset()

def verify_files():
    required_files = ["Questions.csv", "Answers.csv", "Tags.csv"]
    all_exist = True
    
    print("\n--- DATASET VERIFICATION ---")
    for f_name in required_files:
        f_path = DATA_DIR / f_name
        if f_path.exists():
            size_mb = f_path.stat().st_size / (1024 * 1024)
            print(f"[✓] {f_name:15} | Size: {size_mb:.2f} MB")
        else:
            print(f"[✗] {f_name:15} | MISSING!")
            all_exist = False
            
    if all_exist:
        print("\n[+] SUCCESS: Full dataset verified and ready for ingestion!")
    else:
        print("\n[!] WARNING: Some required dataset files are missing. Swapping in simulated files.")
        create_simulated_dataset()

def create_simulated_dataset():
    """Create a high-fidelity subset of Stack Overflow Q&A for development, CI/CD, and fast startup."""
    import pandas as pd
    
    questions = [
        {
            "Id": 1,
            "OwnerUserId": 101,
            "CreationDate": "2026-01-01T12:00:00Z",
            "Score": 52,
            "Title": "How do I read a CSV file using pandas?",
            "Body": "<p>I have a CSV file and want to load it into a pandas DataFrame. What is the best and most efficient way to do this in Python?</p>"
        },
        {
            "Id": 2,
            "OwnerUserId": 102,
            "CreationDate": "2026-01-02T12:00:00Z",
            "Score": 48,
            "Title": "What is the difference between a list and a tuple in Python?",
            "Body": "<p>I am learning Python and keep seeing lists and tuples used in similar ways. What are the key differences (performance, syntax, mutability)? When should I prefer one over the other?</p>"
        },
        {
            "Id": 3,
            "OwnerUserId": 103,
            "CreationDate": "2026-01-03T12:00:00Z",
            "Score": 31,
            "Title": "How do I handle exceptions in Python?",
            "Body": "<p>I want to properly capture errors and exceptions in my script so it does not crash. How do I use try/except/finally blocks, and how can I capture the specific exception object?</p>"
        },
        {
            "Id": 4,
            "OwnerUserId": 104,
            "CreationDate": "2026-01-04T12:00:00Z",
            "Score": 40,
            "Title": "How to merge two dictionaries in Python 3?",
            "Body": "<p>Suppose I have dict_a and dict_b. How do I merge them together into a single dictionary? I would love to see the newer Python 3.5+ double asterisk method as well as Python 3.9+ union operators.</p>"
        },
        {
            "Id": 5,
            "OwnerUserId": 105,
            "CreationDate": "2026-01-05T12:00:00Z",
            "Score": 25,
            "Title": "What is a lambda function and when should I use it?",
            "Body": "<p>Can someone explain Python lambda or anonymous functions with clear syntax, some real-world code examples, and standard use-cases like sorting?</p>"
        },
        {
            "Id": 6,
            "OwnerUserId": 106,
            "CreationDate": "2026-01-06T12:00:00Z",
            "Score": 18,
            "Title": "How do I use list comprehensions with conditions?",
            "Body": "<p>How can I write a list comprehension in Python that includes filters or if-else statements? Showing examples of both would be awesome.</p>"
        },
        {
            "Id": 7,
            "OwnerUserId": 107,
            "CreationDate": "2026-01-07T12:00:00Z",
            "Score": 15,
            "Title": "How to connect to a SQLite database using Python?",
            "Body": "<p>I want to open, query, write to, and close a local SQLite database in python. What standard library should I use, and what is the typical context manager pattern?</p>"
        },
        {
            "Id": 8,
            "OwnerUserId": 108,
            "CreationDate": "2026-01-08T12:00:00Z",
            "Score": 60,
            "Title": "What is the GIL in Python and how does it affect multithreading?",
            "Body": "<p>What is the Global Interpreter Lock (GIL) in CPython, why does it exist, and how does it affect CPU-bound vs I/O-bound multithreaded code?</p>"
        }
    ]

    answers = [
        {
            "Id": 1001,
            "OwnerUserId": 201,
            "CreationDate": "2026-01-01T12:15:00Z",
            "ParentId": 1,
            "Score": 125,
            "Body": "<p>To load a CSV file, use the <code>pd.read_csv()</code> function in pandas. Here is a complete code example:</p><pre><code>import pandas as pd\n\n# Read CSV file cleanly\ndf = pd.read_csv('myfile.csv')\nprint(df.head())\n</code></pre><p>This loads the full file into a DataFrame automatically mapping column names based on the first row.</p>"
        },
        {
            "Id": 1002,
            "OwnerUserId": 202,
            "CreationDate": "2026-01-02T12:10:00Z",
            "ParentId": 2,
            "Score": 98,
            "Body": "<ul><li><strong>Mutability:</strong> Lists are mutable (can be changed); tuples are immutable (cannot be changed after creation).</li><li><strong>Syntax:</strong> Lists use brackets <code>[1, 2]</code>; tuples use parentheses <code>(1, 2)</code>.</li><li><strong>Performance:</strong> Tuples are slightly faster and require less memory.</li></ul>"
        },
        {
            "Id": 1003,
            "OwnerUserId": 203,
            "CreationDate": "2026-01-03T12:20:00Z",
            "ParentId": 3,
            "Score": 84,
            "Body": "<p>Use the <code>try ... except</code> block structure in Python. Example:</p><pre><code>try:\n    result = 10 / 0\nexcept ZeroDivisionError as e:\n    print(f'Captured error: {e}')\nfinally:\n    print('Cleanup complete.')</code></pre>"
        },
        {
            "Id": 1004,
            "OwnerUserId": 204,
            "CreationDate": "2026-01-04T12:12:00Z",
            "ParentId": 4,
            "Score": 142,
            "Body": "<p>In Python 3.9+, use the merge operator <code>|</code>:</p><pre><code>merged_dict = dict_a | dict_b</code></pre><p>In Python 3.5+, use dictionary unpacking:</p><pre><code>merged_dict = {**dict_a, **dict_b}</code></pre>"
        },
        {
            "Id": 1005,
            "OwnerUserId": 205,
            "CreationDate": "2026-01-05T12:30:00Z",
            "ParentId": 5,
            "Score": 55,
            "Body": "<p>A lambda function is a small anonymous function defined with the <code>lambda</code> keyword:</p><pre><code># Syntax: lambda arguments: expression\nsquare = lambda x: x ** 2\n\n# Common with sorted()\npairs = [(1, 'one'), (2, 'two')]\npairs.sort(key=lambda pair: pair[1])</code></pre>"
        },
        {
            "Id": 1006,
            "OwnerUserId": 206,
            "CreationDate": "2026-01-06T12:25:00Z",
            "ParentId": 6,
            "Score": 39,
            "Body": "<p>To filter elements, place the <code>if</code> at the end of the comprehension:</p><pre><code>evens = [x for x in range(10) if x % 2 == 0]</code></pre><p>For if-else replacement mapping, place it before the generator loop:</p><pre><code>labels = ['even' if x % 2 == 0 else 'odd' for x in range(5)]</code></pre>"
        },
        {
            "Id": 1007,
            "OwnerUserId": 207,
            "CreationDate": "2026-01-07T12:40:00Z",
            "ParentId": 7,
            "Score": 45,
            "Body": "<p>Use Python's built-in <code>sqlite3</code> library. Best practice uses context managers:</p><pre><code>import sqlite3\n\nwith sqlite3.connect('local.db') as conn:\n    cursor = conn.cursor()\n    cursor.execute('CREATE TABLE IF NOT EXISTS users (id INT, name TEXT)')\n    cursor.execute('INSERT INTO users VALUES (1, \"Ajay\")')\n    conn.commit()</code></pre>"
        },
        {
            "Id": 1008,
            "OwnerUserId": 208,
            "CreationDate": "2026-01-08T12:45:00Z",
            "ParentId": 8,
            "Score": 110,
            "Body": "<p>The Global Interpreter Lock (GIL) allows only one thread to execute Python bytecode at a time. It prevents race conditions in CPython memory management.</p><p>For CPU-bound tasks, multithreading is bottlenecked; use <code>multiprocessing</code> instead. For I/O-bound tasks, multithreading is effective since threads release the GIL during I/O operations.</p>"
        }
    ]

    tags = [
        {"Id": 1, "Tag": "python"},
        {"Id": 1, "Tag": "pandas"},
        {"Id": 2, "Tag": "python"},
        {"Id": 2, "Tag": "list"},
        {"Id": 2, "Tag": "tuple"},
        {"Id": 3, "Tag": "python"},
        {"Id": 3, "Tag": "exception-handling"},
        {"Id": 4, "Tag": "python"},
        {"Id": 4, "Tag": "dictionary"},
        {"Id": 5, "Tag": "python"},
        {"Id": 5, "Tag": "lambda"},
        {"Id": 6, "Tag": "python"},
        {"Id": 6, "Tag": "list-comprehension"},
        {"Id": 7, "Tag": "python"},
        {"Id": 7, "Tag": "sqlite"},
        {"Id": 8, "Tag": "python"},
        {"Id": 8, "Tag": "multithreading"},
        {"Id": 8, "Tag": "gil"}
    ]

    # Save to CSV
    pd.DataFrame(questions).to_csv(DATA_DIR / "Questions.csv", index=False)
    pd.DataFrame(answers).to_csv(DATA_DIR / "Answers.csv", index=False)
    pd.DataFrame(tags).to_csv(DATA_DIR / "Tags.csv", index=False)
    
    print("[+] Simulated development/testing CSV datasets created successfully at:")
    print(f"    - {DATA_DIR / 'Questions.csv'}")
    print(f"    - {DATA_DIR / 'Answers.csv'}")
    print(f"    - {DATA_DIR / 'Tags.csv'}")

if __name__ == "__main__":
    main()
