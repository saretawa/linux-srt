import json
import subprocess

with open("rule_data.json", "r") as f:
    data = json.load(f)

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
        return True

class FileHandler(BaseHandler):
    def check(self):
        import os
        return os.path.isfile(self.rule["value"])

    def create(self):
        open(self.rule["value"], "a").close()
        return True

class FolderHandler(BaseHandler):
    def check(self):
        import os
        return os.path.isdir(self.rule["value"])

    def create(self):
        import os
        os.makedirs(self.rule["value"], exist_ok=True)
        return True

class NoneHandler(BaseHandler):
    def check(self):
        print(f"[NoneHandler] No prerequisites for rule: {self.rule['name']}")
        return True  # Always satisfied

    def create(self):
        return True  # Nothing to create

class GroupHandler(BaseHandler):
    def check(self):
        import subprocess
        result = subprocess.run(["getent", "group", self.rule["value"]],
                                stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL)
        print(f"[GroupHandler] Checking group: {self.rule['value']} → {'Exists' if result.returncode == 0 else 'Missing'}")
        return result.returncode == 0

    def create(self):
        import subprocess
        print(f"[GroupHandler] Creating group: {self.rule['value']}")
        subprocess.run(["groupadd", self.rule["value"]])
        return True


for rule in data:
    handler = PrerequisiteHandler(rule)
    handler.ensure()

print("\n[INFO] Prerequisite setup complete. Executing rule commands...\n")
subprocess.run(["python3", "run_commands.py"])
