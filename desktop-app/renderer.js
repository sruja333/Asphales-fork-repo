const { ipcRenderer } = require('electron');

let isOn = false;
const toggleBtn = document.getElementById('toggle');
const resultDiv = document.getElementById('result');

toggleBtn.addEventListener('click', () => {
  isOn = !isOn;
  toggleBtn.innerText = isOn ? "ON" : "OFF";
  toggleBtn.style.background = isOn ? "green" : "red";
});

ipcRenderer.on('analyze-text', async (event, text) => {
  if (!isOn || !text) return;

  resultDiv.innerText = "Analyzing...";

  try {
    const response = await fetch("http://127.0.0.1:8000/analyze", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ text: text })
    });

    const data = await response.json();

    resultDiv.innerText = "Threat Level: " + data.result;

  } catch (err) {
    resultDiv.innerText = "Backend not running!";
  }
});
