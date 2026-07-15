/**
 * OpsReady Linux Lab feedback webhook
 *
 * Bind this script to the Google Sheet that will store feedback:
 * Google Sheet -> Extensions -> Apps Script.
 */

const SHEET_NAME = "Feedback";

const HEADERS = [
  "submission_id",
  "submitted_at_utc",
  "app_version",
  "session_id",
  "role",
  "linux_experience",
  "feedback_types",
  "sections_used",
  "usefulness_rating",
  "ease_rating",
  "confidence_rating",
  "recommendation_score",
  "most_useful",
  "improvement_needed",
  "missing_content",
  "issue_found",
  "issue_details",
  "email",
  "consent_to_feedback_use",
  "consent_to_contact",
  "source"
];

/** Browser health-check. Opening the deployed /exec URL should return JSON. */
function doGet() {
  return jsonResponse({
    ok: true,
    service: "OpsReady Linux Lab feedback webhook"
  });
}

/** Receives the JSON POST sent by the Streamlit application. */
function doPost(e) {
  const lock = LockService.getScriptLock();

  try {
    lock.waitLock(10000);

    if (!e || !e.postData || !e.postData.contents) {
      throw new Error("Missing POST body.");
    }

    const payload = JSON.parse(e.postData.contents);
    const spreadsheet = SpreadsheetApp.getActiveSpreadsheet();

    if (!spreadsheet) {
      throw new Error("No active spreadsheet. Create this script from the target Google Sheet.");
    }

    let sheet = spreadsheet.getSheetByName(SHEET_NAME);
    if (!sheet) {
      sheet = spreadsheet.insertSheet(SHEET_NAME);
    }

    if (sheet.getLastRow() === 0) {
      sheet.appendRow(HEADERS);
      sheet.setFrozenRows(1);
      sheet.getRange(1, 1, 1, HEADERS.length).setFontWeight("bold");
    }

    const row = HEADERS.map((key) => normaliseValue(payload[key]));
    sheet.appendRow(row);
    SpreadsheetApp.flush();

    return jsonResponse({
      ok: true,
      submission_id: payload.submission_id || ""
    });
  } catch (error) {
    return jsonResponse({
      ok: false,
      error: String(error)
    });
  } finally {
    try {
      lock.releaseLock();
    } catch (ignored) {
      // The lock may not have been acquired if waitLock failed.
    }
  }
}

function normaliseValue(value) {
  if (Array.isArray(value)) {
    return neutraliseFormula(value.join(" | "));
  }

  if (value === null || value === undefined) {
    return "";
  }

  if (typeof value === "number" || typeof value === "boolean") {
    return value;
  }

  if (typeof value === "object") {
    return neutraliseFormula(JSON.stringify(value));
  }

  return neutraliseFormula(String(value));
}

/** Prevent user-supplied text from being interpreted as a Sheet formula. */
function neutraliseFormula(value) {
  const text = String(value);
  return /^[=+\-@]/.test(text) ? "'" + text : text;
}

function jsonResponse(payload) {
  return ContentService
    .createTextOutput(JSON.stringify(payload))
    .setMimeType(ContentService.MimeType.JSON);
}
