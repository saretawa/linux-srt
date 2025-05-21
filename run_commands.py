import json
import subprocess
import argparse
from typing import Union, List, Optional


class Rule:
    def __init__(self, rule_data: dict):
        self.id: int = rule_data.get("id", -1)
        self.name: str = rule_data.get("name", "Unnamed")
        self.type: str = rule_data.get("type", "none")
        self.command: Optional[Union[str, List[str]]] = rule_data.get("command")
        self.value: Optional[str] = rule_data.get("value")

    def is_valid(self) -> bool:
        return isinstance(self.command, (str, list))

    def is_multiple(self) -> bool:
        return isinstance(self.command, list)

    def get_commands(self) -> List[List[str]]:
        commands: List[List[str]] = []

        if self.command is None:
            return commands

        cmd_list = self.command if isinstance(self.command, list) else [self.command]

        for cmd in cmd_list:
            parts = cmd.split()
            if self.value:
                parts.append(self.value)
            commands.append(parts)

        return commands


class CommandExecutor:
    def __init__(self, rule: Rule):
        self.rule = rule

    def execute(self, dry_run: bool = False, use_bash: bool = False):
        print(f"\n[RUNNING] Rule #{self.rule.id}: {self.rule.name}")

        if not self.rule.is_valid():
            print(f"[SKIPPED] No valid command defined.")
            return
        
        for cmd_parts in self.rule.get_commands():
            cmd_str = " ".join(cmd_parts)

            if use_bash:
                final_cmd = ["bash", "-c", cmd_str]
            else:
                final_cmd = cmd_parts

            print(f"-> {'[DRY RUN]' if dry_run else 'Executing'}: {' '.join(final_cmd)}")

            if dry_run:
                continue

            try:
                result = subprocess.run(final_cmd, check=True)
                print(f"[SUCCESS] Exit code: {result.returncode}")
            except subprocess.CalledProcessError as e:
                print(f"[FAILED] Command '{cmd_str}' failed with code {e.returncode}")
            except FileNotFoundError:
                print(f"[ERROR] Command not found: {final_cmd[0]}")



def load_rules(json_path: str) -> List[Rule]:
    with open(json_path, "r") as f:
        raw_data = json.load(f)
    return [Rule(entry) for entry in raw_data if isinstance(entry, dict)]


def main():
    parser = argparse.ArgumentParser(description="SIEM Rule Command Executor")
    parser.add_argument("--dry-run", action="store_true", help="Print commands without executing them")
    parser.add_argument("--use-bash", action="store_true", help="Execute commands through bash -c")
    args = parser.parse_args()

    rules = load_rules("rule_data.json")
    for rule in rules:
        executor = CommandExecutor(rule)
        executor.execute(dry_run=args.dry_run, use_bash=args.use_bash)

    print(f"\n[INFO] Processed {len(rules)} rule(s) successfully.\n")

if __name__ == "__main__":
    main()


