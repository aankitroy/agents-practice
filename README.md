# Agents Practice

This project contains various agents implemented using the `agno` library. Each agent is designed to perform specific tasks, such as interacting with knowledge bases or using web tools.

## Setup

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/yourusername/agents-practice.git
   cd agents-practice
   ```

2. **Create a Virtual Environment:**

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
   ```

3. **Install Dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

   If you encounter a `ModuleNotFoundError` for `pypdf`, install it using:

   ```bash
   pip install pypdf
   ```

4. **Install Rust and Cargo (if needed):**

   Some packages may require Rust and Cargo. Install them using:

   ```bash
   curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
   ```

   Add Cargo to your PATH:

   ```bash
   export PATH="$HOME/.cargo/bin:$PATH"
   ```

## Running the Agents

- **Agent with Knowledge:**

  To run the agent with a knowledge base, execute:

  ```bash
  python agent_with_knowledge.py
  ```

- **Basic Agent:**

  To run the basic agent, execute:

  ```bash
  python basic_agent.py
  ```

- **Agent with Tools:**

  To run the agent with tools, execute:

  ```bash
  python agent_with_tools.py
  ```

## Troubleshooting

- Ensure all dependencies are installed.
- Verify that Rust and Cargo are installed if you encounter issues with packages requiring them.
- Check that your virtual environment is activated when running the scripts.

## Contributing

Feel free to open issues or submit pull requests for improvements or bug fixes.
