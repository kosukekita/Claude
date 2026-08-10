const fs = require('fs');
const { spawn } = require('child_process');

const targetPath = "C:\\Users\\u8792\\.pixel-agents\\hooks\\claude-hook.js";

if (fs.existsSync(targetPath)) {
  const child = spawn(process.execPath, [targetPath, ...process.argv.slice(2)], {
    stdio: 'inherit'
  });
  
  child.on('exit', (code, signal) => {
    if (signal) {
      process.kill(process.pid, signal);
    } else {
      process.exit(code !== null ? code : 0);
    }
  });
} else {
  process.exit(0);
}
