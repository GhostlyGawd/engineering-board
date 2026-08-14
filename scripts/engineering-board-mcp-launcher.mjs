#!/usr/bin/env node

import { spawn } from "node:child_process";
import { fileURLToPath } from "node:url";
import { dirname, join, resolve } from "node:path";

const scriptDirectory = dirname(fileURLToPath(import.meta.url));
const pluginRoot = resolve(scriptDirectory, "..");
const server = join(pluginRoot, "mcp-server", "engineering_board_mcp.py");

const candidates = [];
if (process.env.PYTHON) {
  candidates.push({ command: process.env.PYTHON, args: [] });
}
if (process.platform === "win32") {
  candidates.push(
    { command: "python", args: [] },
    { command: "py", args: ["-3"] },
  );
} else {
  candidates.push(
    { command: "python3", args: [] },
    { command: "python", args: [] },
  );
}

function start(index) {
  if (index >= candidates.length) {
    process.stderr.write(
      "Engineering Board requires Python 3. Set PYTHON to its executable path.\n",
    );
    process.exit(127);
  }

  const candidate = candidates[index];
  const child = spawn(candidate.command, [...candidate.args, server], {
    cwd: pluginRoot,
    env: {
      ...process.env,
      ENGINEERING_BOARD_REQUIRE_ROOT: "1",
    },
    shell: false,
    stdio: "inherit",
  });

  child.once("error", (error) => {
    if (error.code === "ENOENT") {
      start(index + 1);
      return;
    }
    process.stderr.write(`Engineering Board failed to start: ${error.message}\n`);
    process.exit(1);
  });
  child.once("exit", (code, signal) => {
    if (signal) {
      process.kill(process.pid, signal);
      return;
    }
    process.exit(code ?? 1);
  });
}

start(0);
