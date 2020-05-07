function onOpen() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var menuItems = [{name: 'HideRows', functionName: 'hideRows'}, {name: 'SendMail', functionName: 'sendMail'}];
  ss.addMenu('Pohjus miks see avaneb mingi tund aega', menuItems);
  hideRows();
  //sendMail(); //trigger onChange
}

function hideRows() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName("Doodle");
  var maxRows = sheet.getLastRow();
  var rows = sheet.getRange(2, 1, maxRows);
  var count = rows.getHeight();
  var cutoff = new Date();
  cutoff.setDate(cutoff.getDate() - 1);
  var cell;
  var cellDate;
  var dateCell = sheet.getRange(1, 10).getCell(1, 1);
  var maxHiddenRow = dateCell.getValue().toString().split(':')[0];
  if (maxHiddenRow > 1) {
    sheet.hideRows(2, maxHiddenRow - 1);
  }


  //lol no forEach
  for (var i = maxHiddenRow; i < count - 1; i++) {
    cell = rows.getCell(i, 1);
    cellDate = cell.getValue();
    dateCell.setValue(i + ":" + cellDate.toISOString().split('T')[0]);
    if (cellDate && (cellDate > cutoff)) {
      sheet.hideRows(2, i - 1);
      break;
    }
  }
}

function sendMail() {
  var CALENDAR_ID = 'XXXXXXXXXXXX@group.calendar.google.com';
  var SHEETS_LINK = 'https://docs.google.com/spreadsheets/d/XXXXXXXXXXXXXXXXXXX';
  var CURRENT_USER = Session.getActiveUser().getEmail();

  //randomize script start time - attempt to disperse execution and reduce races
  console.info("init at : " + new Date());
  var randomWaitTime = Math.floor(Math.random() * 4) + 1;
  var randomId = Math.floor(Math.random() * 1024) + 1;
  console.info("run" + randomId + " by " + CURRENT_USER + " waiting : " + randomWaitTime);
  Utilities.sleep(1000 * randomWaitTime);
  console.info("run" + randomId + " by " + CURRENT_USER + " continue at : " + new Date());

  var ss = SpreadsheetApp.getActiveSpreadsheet(); //pretty hopeless to deduplicate
  var doodle = ss.getSheetByName("Doodle");
  var data = ss.getSheetByName("Data");

  var maxHiddenRow = +doodle.getRange(1, 10).getCell(1, 1).getValue().toString().split(':')[0]; //watman
  var lookaheadDays = 25;

  //check for a lock
  var runRange = doodle.getRange(1, 12, 1);
  var idleCell = runRange.getCell(1, 1);
  var isIdle = idleCell.isBlank();
  if (isIdle) {
    idleCell.setValue("run" + randomId);
    console.info(randomId + " script is idle : " + idleCell.getValue() + " by " + CURRENT_USER);
  } else {
    console.info("run" + randomId + " by " + CURRENT_USER + " detected running script : " + idleCell.getValue() + ", aborted");
    return;
  }

  var dateRange = doodle.getRange(maxHiddenRow + 1, 1, lookaheadDays);

  var yesRange = doodle.getRange(maxHiddenRow + 1, 8, lookaheadDays);     // H
  var maybeRange = doodle.getRange(maxHiddenRow + 1, 9, lookaheadDays);   // I
  var stateRange = doodle.getRange(maxHiddenRow + 1, 10, lookaheadDays);  // J
  var eventIdRange = doodle.getRange(maxHiddenRow + 1, 11, lookaheadDays); // K - hidden
  var commentRange = doodle.getRange(maxHiddenRow + 1, 12, lookaheadDays); // L

  var emails = getEmails(data);
  console.log("init emails : " + emails);
  verifyFill(maxHiddenRow, doodle, emails, SHEETS_LINK);

  for (var i = 1; i < lookaheadDays; i++) {
    var maybeCell = maybeRange.getCell(i, 1);
    var yesCell = yesRange.getCell(i, 1);
    var dateCell = dateRange.getCell(i, 1);
    var stateCell = stateRange.getCell(i, 1);
    var eventIdCell = eventIdRange.getCell(i, 1);
    var commentCell = commentRange.getCell(i, 1);
    var rown = maybeCell.getRow();
    console.log(("row: " + rown + " maybe: " + maybeCell.getValue() + " yes: " + yesCell.getValue() + " date: " + dateCell.getValue()));

    //check if event exits for day i, handle
    if (!stateCell.isBlank()) {
      var events = CalendarApp.getCalendarById(CALENDAR_ID).getEventsForDay(new Date(dateCell.getValue()));
      events.forEach(function (e) {
        console.log("event for " + dateCell.getValue() + " - " + e.getTitle() + ' ' + e.getId())
      });
      if (events.length > 1) {
        console.error(dateCell.getValue() + " has too many events : " + events.length)
      }

      var eventId;
      if (eventIdCell.isBlank()) {
        if (events.length === 0) {
          console.error(dateCell.getValue() + " has comment, and no events are available")
          continue;
        } else {
          eventId = events[0].getId();
          console.warn(dateCell.getValue() + " has comment, but no event, using " + eventId);
          eventIdCell.setValue(eventId);
        }
      } else {
        eventId = eventIdCell.getValue();
      }

      console.info(dateCell.getValue() + " has event " + eventId);
      var event = CalendarApp.getCalendarById(CALENDAR_ID).getEventById(eventId);
      if (!event) {
        stateCell.setBackground("#ff9a9a");
        stateCell.setValue('Event has been deleted')
      } else {
        var accepted = event.getGuestList(true).filter(function (guest) {
          console.info(eventId + " : " + guest.getGuestStatus() + ' ' + guest.getEmail());
          return guest.getGuestStatus() == 'YES'; //coerce
        });
        var declined = event.getGuestList(true).filter(function (guest) {
          return guest.getGuestStatus() == 'NO'; //coerce
        });
        stateCell.setValue('Invite sent [' + accepted.length + '/5 accepted]');
        if (declined.length > 0) {
          commentCell.setValue('NB! Declined by: ' + declined.map(function (guest) {
            return guest.getEmail()
          }))
        } else {
          commentCell.clear()
        }
      }

    }

    //if there is no event, but there should be
    if (stateCell.isBlank() && +maybeCell.getValue() >= 5) {
      stateCell.setValue('Sending invite')
      var message = dateCell.getValue() + ' on D&D night. '
      if (+yesCell.getValue() >= 5) {
        message += 'Ja lausa 5 kindlat JAH vastust on. Uskumatu!'
      }
      console.info(message)
      var date = dateCell.getValue()
      date.setHours(20)
      var endDate = dateCell.getValue()
      endDate.setHours(23)
      console.log('date: ' + date + ' end: ' + endDate)
      var event = CalendarApp.getCalendarById(CALENDAR_ID).createEvent('D&D', date, endDate, {
        guests: emails.join(','),
        sendInvites: true,
        description: message + ' Link: ' + SHEETS_LINK
      })
      console.info(("Sent event " + event.getId()))
      eventIdCell.setValue(event.getId())
      stateCell.setValue('Invite sent')
    }
  } //end for

  idleCell.clear();
  console.info("run" + randomId + " by " + CURRENT_USER + " finished")
}

function verifyFill(maxHiddenRow, doodle, emails, SHEETS_LINK) {
  for (var i = 1; i <= 5; i++) {
    var userRange = doodle.getRange(maxHiddenRow + 1, 2 + i, 10, 1)
    console.log("[verifyFill] " + emails[i - 1] + " range " + userRange.getA1Notation())
    var emptyCells = []
    for (var j = 1; j <= 10; j++) {
      var checkCell = userRange.getCell(j, 1)
      console.log("[verifyFill] cell" + j + " " + checkCell.getA1Notation())
      if (checkCell.isBlank()) {
        emptyCells.push(checkCell)
        console.log("[verifyFill] empty " + emails[i - 1] + " " + emptyCells.length)
      }
    }
    if (emptyCells.length >= 3) {
      emptyCells.forEach(function (cell) {
        cell.setValue("?")
      })
      console.warn("[verifyFill] MailApp.sendEmail :: " + emails[i - 1] + ", 'Täida D&D doodle', 'Sul on " + emptyCells.length + " tühja päeva järgmise 10 päeva jooksul. Link: '" + SHEETS_LINK)
      console.warn("[verifyFill] MailApp quota     :: " + MailApp.getRemainingDailyQuota())
      MailApp.sendEmail(emails[i - 1], 'Täida D&D doodle', 'Sul on ' + emptyCells.length + ' tühja päeva järgmise 10 päeva jooksul. Link: ' + SHEETS_LINK)
    }
  }
}


function getEmails(dataSheet) {
  return dataSheet.getRange(1, 1, 5).getValues().map(function (arr) {
    return arr[0]
  }).filter(function (str) {
    return !!str
  })
}
