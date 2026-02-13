const { app, BrowserWindow, globalShortcut, clipboard } = require('electron');

let win;

function createWindow() {
  win = new BrowserWindow({
    width: 320,
    height: 250,
    alwaysOnTop: true,
    frame: false,
    resizable: false,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false
    }
  });

  win.loadFile('index.html');
}

app.whenReady().then(() => {
  createWindow();

  // Register shortcut: Ctrl + Shift + X
  globalShortcut.register('CommandOrControl+Shift+X', () => {
    const selectedText = clipboard.readText();
    win.webContents.send('analyze-text', selectedText);
  });
});
