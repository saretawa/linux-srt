import json
import subprocess
import argparse
import os

# ─── Handlers ────────────────────────────────────────────────

class PrerequisiteHandler:
    def __init__(self, rule):
        self.rule = rule
        self.type = rule["type"]
        self.value = rule["value"]

    def get_handler(self):
        if self.type == "user":
            return UserHandler(self.rule)
        elif self.type == "group":
            return GroupHandler(self.rule)
        elif self.type == "file":
            return FileHandler(self.rule)
        elif self.type == "folder":
            return FolderHandler(self.rule)
        elif self.type == "none":
            return NoneHandler(self.rule)
        else:
            raise ValueError(f"Unknown type: {self.type}")

    def ensure(self):
        handler = self.get_handler()
        if not handler.check():
            handler.create()

class BaseHandler:
    def __init__(self, rule):
        self.rule = rule

    def check(self): raise NotImplementedError
    def create(self): raise NotImplementedError

class UserHandler(BaseHandler):
    def check(self):
        result = subprocess.run(["id", self.rule["value"]], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return result.returncode == 0

    def create(self):
        subprocess.run(["useradd", self.rule["value"]])

class GroupHandler(BaseHandler):
    def check(self):
        result = subprocess.run(["getent", "group", self.rule["value"]],
                                stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL)
        print(f"[GroupHandler] Checking group: {self.rule['value']} → {'Exists' if result.returncode == 0 else 'Missing'}")
        return result.returncode == 0

    def create(self):
        print(f"[GroupHandler] Creating group: {self.rule['value']}")
        subprocess.run(["groupadd", self.rule["value"]])

class FileHandler(BaseHandler):
    def check(self):
        return os.path.isfile(self.rule["value"])

    def create(self):
        open(self.rule["value"], "a").close()

class FolderHandler(BaseHandler):
    def check(self):
        return os.path.isdir(self.rule["value"])

    def create(self):
        os.makedirs(self.rule["value"], exist_ok=True)

class NoneHandler(BaseHandler):
    def check(self):
        print(f"[NoneHandler] No prerequisites for rule: {self.rule['name']}")
        return True

    def create(self):
        return True

# ─── Main Execution ──────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="SRT Prerequisite Setup")
    parser.add_argument("--dry-run", action="store_true", help="Print commands without executing them")
    parser.add_argument("--use-bash", action="store_true", help="Execute commands via bash -c")
    args = parser.parse_args()

    with open("rule_data.json", "r") as f:
        data = json.load(f)

    for rule in data:
        handler = PrerequisiteHandler(rule)
        handler.ensure()

    print("\n[INFO] Prerequisite setup complete. Executing rule commands...\n")

    cmd = ["python3", "run_commands.py"]
    if args.dry_run:
        cmd.append("--dry-run")
    if args.use_bash:
        cmd.append("--use-bash")

    subprocess.run(cmd)

if __name__ == "__main__":
    main()
