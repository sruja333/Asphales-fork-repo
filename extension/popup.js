// Track if protection is active
let isActive = false;
// Get the toggle button
const toggleBtn = document.getElementById('toggleBtn');
const statusDiv = document.getElementById('status');
const infoDiv = document.getElementById('info');
// When button is clicked
toggleBtn.addEventListener('click', async () => {
 // Toggle the state
 isActive = !isActive;

 // Get the current active tab
 const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

 // Send message to content script
 chrome.tabs.sendMessage(tab.id, {
 action: isActive ? 'START_SCAN' : 'STOP_SCAN'
 });

 // Update UI
 if (isActive) {
 statusDiv.textContent = 'Protection: ON ✓';
 statusDiv.className = 'status active';
 toggleBtn.textContent = 'Deactivate Protection';
 infoDiv.style.display = 'block';
 } else {
 statusDiv.textContent = 'Protection: OFF';
 statusDiv.className = 'status inactive';
 toggleBtn.textContent = 'Activate Protection';
 infoDiv.style.display = 'none';
 }
});
// Load saved state when popup opens
chrome.storage.local.get(['isActive'], (result) => {
 if (result.isActive) {
 isActive = true;
 statusDiv.textContent = 'Protection: ON ✓';
 statusDiv.className = 'status active';
 toggleBtn.textContent = 'Deactivate Protection';
 }
});