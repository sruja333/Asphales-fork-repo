// This file runs in the background and helps coordinate between popup and content script
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
 if (message.action === 'SAVE_STATE') {
 chrome.storage.local.set({ isActive: message.isActive });
 }

 if (message.action === 'LOG') {
 console.log('SurakshaAI:', message.data);
 }
});
// When extension is installed
chrome.runtime.onInstalled.addListener(() => {
 console.log('SurakshaAI Shield installed successfully!');
});