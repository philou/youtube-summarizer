// Google Sheets abstraction layer
// When running locally, this can mock the sheet with a CSV file
// When deployed, it connects to the real Google Sheet via Apps Script API

function getSheet() {
  if (typeof SpreadsheetApp !== 'undefined') {
    // Running in Apps Script
    return SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  } else {
    // Local mock (to be implemented)
    throw new Error('Local sheet mock not implemented.');
  }
}

module.exports = { getSheet };
