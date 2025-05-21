**SRT (SIEM Rule Tester)** is a lightweight, modular toolkit designed for testing and validating SIEM detection rules on Linux systems.

It safely simulates alert-triggering behavior by setting up required conditions (users, files, folders, etc.) and executing mapped system commands — with optional --dry-run mode for non-disruptive evaluation and --use-bash to execute commands through a shell for improved SIEM visibility.

* Test and verify detection logic before production deployment
* Simulate real attacker behavior in a controlled lab
* Clean separation between **setup** and **execution**
* Extensible with JSON-based rule definitions

### Project Structure

```
linux-srt/
├── main.py              # Handles asset setup (users, files, folders)
├── run_commands.py      # Executes SIEM-triggering commands
├── rule_data.json       # List of rules (command, type, value)
```

* Add more rules to `rule_data.json`
* Add new types to `main.py` handlers
* Modify `run_commands.py` logic for logging, cleanup, or integration


### Sample Rule Entry

```json
{
  "id": 40,
  "name": "Recursively delete folder",
  "type": "folder",
  "command": "rm -rf",
  "value": "/tmp/fake-root"
}
```

### How to Use

#### 1. Setup test environment(creates and runs, use --dry-run flag to just create):

```bash
sudo python3 main.py
```

#### 2. Run rule commands:

```bash
python3 run_commands.py
```

#### Optional: Dry-run to preview commands only

```bash
python3 run_commands.py --dry-run
```
#### Optional: Execute commands through a shell

```bash
python3 main.py --use-bash
```
or
```bash
python3 run_commands.py --use-bash
```

### Currently Supported Rule Types

| Type     | Description                              |
| -------- | ---------------------------------------- |
| `user`   | Creates a test user (e.g. for `userdel`) |
| `group`  | Creates a test group                     |
| `file`   | Creates a dummy file                     |
| `folder` | Creates a directory for deletion, etc.   |
| `none`   | No setup needed, runs command as-is      |

### Safety

* Always run in a **test VM or container**
* Requires `sudo` for creating users or groups
* All test assets are local, isolated, and minimal

### Contributing

PRs are welcome — especially for new rule types, detection scenarios, or improved execution logic.

### License

MIT — open for personal, academic, or professional use.


