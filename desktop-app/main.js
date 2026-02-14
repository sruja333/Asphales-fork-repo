const { app, BrowserWindow, globalShortcut, clipboard, ipcMain, screen } = require('electron');

let win;
const COLLAPSED_SIZE = { width: 48, height: 48 };
const EXPANDED_SIZE = { width: 420, height: 360 };
const WINDOW_MARGIN = 16;

function positionBottomRight(width, height) {
  const cursorPoint = screen.getCursorScreenPoint();
  const display = screen.getDisplayNearestPoint(cursorPoint);
  const { x: areaX, y: areaY, width: areaWidth, height: areaHeight } = display.workArea;

  const targetX = areaX + areaWidth - width - WINDOW_MARGIN;
  const targetY = areaY + areaHeight - height - WINDOW_MARGIN;

  const maxX = areaX + areaWidth - width;
  const maxY = areaY + areaHeight - height;
  const x = Math.min(Math.max(targetX, areaX), maxX);
  const y = Math.min(Math.max(targetY, areaY), maxY);

  win.setBounds({ x, y, width, height }, false);
}

function createWindow() {
  win = new BrowserWindow({
    width: COLLAPSED_SIZE.width,
    height: COLLAPSED_SIZE.height,
    alwaysOnTop: true,
    frame: false,
    resizable: false,
    transparent: true,
    backgroundColor: '#00000000',
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false
    }
  });

  win.loadFile('index.html');
  win.once('ready-to-show', () => {
    positionBottomRight(COLLAPSED_SIZE.width, COLLAPSED_SIZE.height);
  });
}

app.whenReady().then(() => {
  createWindow();

  ipcMain.on('set-window-state', (event, isExpanded) => {
    if (!win || win.isDestroyed()) return;

    const size = isExpanded ? EXPANDED_SIZE : COLLAPSED_SIZE;
    win.setResizable(false);
    win.setMinimumSize(COLLAPSED_SIZE.width, COLLAPSED_SIZE.height);

    positionBottomRight(size.width, size.height);
    win.show();
    win.focus();
  });

  // Register shortcut: Ctrl + Shift + X
  globalShortcut.register('CommandOrControl+Shift+X', () => {
    const selectionText = clipboard.readText('selection');
    const clipboardText = clipboard.readText();
    const selectedText = selectionText && selectionText.trim() ? selectionText : clipboardText;
    win.webContents.send('analyze-text', selectedText);
  });
});
