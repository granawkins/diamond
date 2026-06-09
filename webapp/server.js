import express from "express";
import { spawn } from "node:child_process";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const repoRoot = path.resolve(__dirname, "..");
const pulseScriptPath = path.join(repoRoot, "scripts", "motor_pulse_test.py");
const mixScriptPath = path.join(repoRoot, "scripts", "motor_mix_test.py");

const app = express();
const port = Number(process.env.PORT || 3030);

app.use(express.json());
app.use(express.static(path.join(__dirname, "public")));

function parsePulse(body) {
  const side = body.side === "right" ? "right" : "left";
  const direction = body.direction === "reverse" ? "reverse" : "forward";
  const speed = Number(body.speed);
  const seconds = Number(body.seconds);

  if (!Number.isFinite(speed) || speed < 0 || speed > 1) {
    throw new Error("speed must be between 0 and 1");
  }

  if (!Number.isFinite(seconds) || seconds <= 0 || seconds > 5) {
    throw new Error("seconds must be greater than 0 and no more than 5");
  }

  return { side, direction, speed, seconds };
}

function parseMix(body) {
  const left = Number(body.left);
  const right = Number(body.right);
  const seconds = Number(body.seconds);

  if (!Number.isFinite(left) || left < -1 || left > 1) {
    throw new Error("left must be between -1 and 1");
  }

  if (!Number.isFinite(right) || right < -1 || right > 1) {
    throw new Error("right must be between -1 and 1");
  }

  if (!Number.isFinite(seconds) || seconds <= 0 || seconds > 5) {
    throw new Error("seconds must be greater than 0 and no more than 5");
  }

  return { left, right, seconds };
}

function runPython(args, res) {
  const child = spawn("python3", args, {
    cwd: repoRoot,
    stdio: ["ignore", "pipe", "pipe"],
  });

  let stdout = "";
  let stderr = "";

  child.stdout.on("data", (chunk) => {
    stdout += chunk;
  });

  child.stderr.on("data", (chunk) => {
    stderr += chunk;
  });

  child.on("error", (error) => {
    res.status(500).json({ ok: false, error: error.message, stdout, stderr });
  });

  child.on("close", (code) => {
    res.status(code === 0 ? 200 : 500).json({
      ok: code === 0,
      code,
      stdout,
      stderr,
    });
  });
}

app.post("/api/pulse", (req, res) => {
  let pulse;

  try {
    pulse = parsePulse(req.body || {});
  } catch (error) {
    res.status(400).json({ ok: false, error: error.message });
    return;
  }

  const args = [
    pulseScriptPath,
    "--side",
    pulse.side,
    "--direction",
    pulse.direction,
    "--speed",
    String(pulse.speed),
    "--seconds",
    String(pulse.seconds),
  ];

  runPython(args, res);
});

app.post("/api/mix", (req, res) => {
  let mix;

  try {
    mix = parseMix(req.body || {});
  } catch (error) {
    res.status(400).json({ ok: false, error: error.message });
    return;
  }

  const args = [
    mixScriptPath,
    "--left",
    String(mix.left),
    "--right",
    String(mix.right),
    "--seconds",
    String(mix.seconds),
  ];

  runPython(args, res);
});

app.listen(port, "0.0.0.0", () => {
  console.log(`motor pulse webapp listening on http://localhost:${port}`);
});
