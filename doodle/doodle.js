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
  const CALENDAR_ID = 'XXXXXXXXXXXX@group.calendar.google.com';
  const SHEETS_LINK = 'https://docs.google.com/spreadsheets/d/XXXXXXXXXXXXXXXXXXX';
  const CURRENT_USER = Session.getActiveUser().getEmail();

  const PLAYERCOUNT = 6;
  const COL_DATE = 1;
  const COL_WEEKDAY = 2;
  const COL_YES = COL_WEEKDAY + PLAYERCOUNT + 1;
  const COL_MAYBE = COL_YES + 1;
  const COL_STATE = COL_YES + 2;
  const COL_EVENTID = COL_YES + 3;
  const COL_COMMENT = COL_YES + 4;

  const doodle = SpreadsheetApp.getActive().getSheetByName('Doodle'); //pretty hopeless to deduplicate

  const maxHiddenRow = +doodle.getRange(1, COL_STATE).getCell(1, 1).getValue().toString().split(':')[0]; //watman
  const LOOK_AHEAD = 25;


  const CORONATIME = false;
  if (CORONATIME) {
    /* since literally everyone has free time now */
    console.info("it's CORONATIME");
    return;
  }

  const emails = getEmails(SpreadsheetApp.getActive().getSheetByName("Data"), PLAYERCOUNT);
  console.log(`[${CURRENT_USER}] init emails : ${emails}`);

  const idleCell = doodle.getRange(1, COL_COMMENT, 1).getCell(1, 1);
  const runId = reserveRun(CURRENT_USER, Math.max(emails.indexOf(CURRENT_USER), 0), doodle, idleCell)
  if (!runId) {
    return;
  }

  const dateRange = doodle.getRange(maxHiddenRow + 1, COL_DATE, LOOK_AHEAD);       // A
  const yesRange = doodle.getRange(maxHiddenRow + 1, COL_YES, LOOK_AHEAD);         // H
  const maybeRange = doodle.getRange(maxHiddenRow + 1, COL_MAYBE, LOOK_AHEAD);     // I
  const stateRange = doodle.getRange(maxHiddenRow + 1, COL_STATE, LOOK_AHEAD);     // J
  const eventIdRange = doodle.getRange(maxHiddenRow + 1, COL_EVENTID, LOOK_AHEAD); // K - hidden
  const commentRange = doodle.getRange(maxHiddenRow + 1, COL_COMMENT, LOOK_AHEAD); // L

  verifyFill(runId, maxHiddenRow, doodle, emails, SHEETS_LINK);

  for (let i = 1; i < LOOK_AHEAD; i++) {
    const maybeCell = maybeRange.getCell(i, 1);
    const yesCell = yesRange.getCell(i, 1);
    const dateCell = dateRange.getCell(i, 1);
    const stateCell = stateRange.getCell(i, 1);
    const eventIdCell = eventIdRange.getCell(i, 1);
    const commentCell = commentRange.getCell(i, 1);
    const rown = maybeCell.getRow();
    console.log((`[${runId}] row: ${rown} maybe: ${maybeCell.getValue()} yes: ${yesCell.getValue()} date: ${dateCell.getValue()}`));

    //check if event exits for day i, handle
    if (!stateCell.isBlank()) {
      const events = CalendarApp.getCalendarById(CALENDAR_ID).getEventsForDay(new Date(dateCell.getValue()), {search: 'D&D'});
      events.forEach(function (e) {
        console.log(`[${runId}] event for ${dateCell.getValue()} - ${e.getTitle()} ${e.getId()}`)
      });
      if (events.length > 1) {
        console.error(dateCell.getValue() + " has too many events : " + events.length)
        for (i = 1; i < events.length; i++) {
          console.error(`[${runId}] deleting ${events[i].getTitle()} (${events[i].getId()})`)
          events[i].deleteEvent()
        }
        eventIdCell.setValue(events[0].getId())
      }

      let eventId;
      if (eventIdCell.isBlank()) {
        if (events.length === 0) {
          console.error(`[${runId}] ${dateCell.getValue()} has comment, and no events are available`)
          continue;
        } else {
          eventId = events[0].getId();
          console.warn(`[${runId}] ${dateCell.getValue()} has comment, but no event, using ${eventId}`);
          eventIdCell.setValue(eventId);
        }
      } else {
        eventId = eventIdCell.getValue();
      }

      const event = CalendarApp.getCalendarById(CALENDAR_ID).getEventById(eventId);
      if (!event) {
        stateCell.setBackground("#ff9a9a");
        stateCell.setValue('Event has been deleted')
      } else {
        let accepted = event.getGuestList(true).filter(function (guest) {
          console.info(`[${runId}] ${eventId} : ${guest.getGuestStatus()} ${guest.getEmail()}`);
          return guest.getGuestStatus() == 'YES'; //coerce
        });
        let declined = event.getGuestList(true).filter(function (guest) {
          return guest.getGuestStatus() == 'NO'; //coerce
        });
        stateCell.setValue(`Invite sent [${accepted.length}/${PLAYERCOUNT} accepted]`);

        if (declined.length > 0) {
          commentCell.setValue('NB! Declined by: ' + declined.map(function (guest) {
            return guest.getEmail()
          }))
        } else {
          commentCell.clear()
        }

        if (maybeCell.getValue() < PLAYERCOUNT) {
          console.warn(`[${runId}] Not enough people (${maybeCell.getValue()}/${PLAYERCOUNT}) ` +
            `to hold event on ${dateCell.getValue()}, deleting : ${event.getId()}`)
          event.deleteEvent()
          stateCell.setValue('Deleted event')
          commentCell.setValue('Someone changed their mind')
          eventIdCell.setValue('')
        }
      }
    }

    //if there is no event, but there should be
    if (stateCell.isBlank() && +maybeCell.getValue() >= PLAYERCOUNT) {
      stateCell.setValue('Sending invite')
      let message = dateCell.getValue() + ' on D&D night. '
      if (+yesCell.getValue() >= PLAYERCOUNT) {
        message += 'Ja lausa ' + PLAYERCOUNT + ' kindlat JAH vastust on. Uskumatu!'
      }
      console.info(`[${runId}] ${message}`)
      const date = dateCell.getValue()
      date.setHours(20)
      const endDate = dateCell.getValue()
      endDate.setHours(23)
      console.log(`[${runId}] date: ${date} end: ${endDate}`)
      const event = CalendarApp.getCalendarById(CALENDAR_ID).createEvent('D&D', date, endDate, {
        guests: emails.join(','),
        sendInvites: true,
        description: message + ' Link: ' + SHEETS_LINK
      })
      console.info(`[${runId}] Sent event ${event.getId()}`)
      eventIdCell.setValue(event.getId())
      stateCell.setValue('Invite sent')
    }

  } //end for

  idleCell.clear();
  console.info(`[${runId}] run${runId} by ${CURRENT_USER} finished`)
}

function verifyFill(runId, maxHiddenRow, doodle, emails, SHEETS_LINK) {
  for (var i = 1; i <= emails.length; i++) {
    var userRange = doodle.getRange(maxHiddenRow + 1, 2 + i, 10, 1)
    var emptyCells = []
    for (var j = 1; j <= 10; j++) {
      var checkCell = userRange.getCell(j, 1)
      if (checkCell.isBlank()) {
        emptyCells.push(checkCell)
        console.log(`[${runId}][verifyFill] empty ${emails[i - 1]} ${emptyCells.length}`)
      }
    }
    if (emptyCells.length >= 3) {
      emptyCells.forEach(function (cell) {
        cell.setValue("?")
      })
      console.warn(`[${runId}][verifyFill] MailApp.sendEmail :: ${emails[i - 1]} has ${emptyCells.length} empty cells`)
      console.warn(`[${runId}][verifyFill] MailApp quota     :: ${MailApp.getRemainingDailyQuota()}`)
      MailApp.sendEmail(emails[i - 1], 'Täida D&D doodle', `Sul on ${emptyCells.length} tühja päeva järgmise 10 päeva jooksul. Link: ${SHEETS_LINK}`)
    }
  }
}

/**
 * Returns a run ID if available, otherwise null
 */
function reserveRun(user, userIdx, doodle, idleCell) {
  //randomize script start time - attempt to disperse execution and reduce races
  console.info(`[reserveRun] init at : ${new Date()} by ${user}`);
  let randomWaitTime = Math.floor(Math.random() * 1000) + userIdx * 1000;
  let randomId = Math.floor(Math.random() * 1024) + 1;
  console.info(`[${randomId}] run${randomId} by ${user} waiting : ${randomWaitTime}ms`);
  Utilities.sleep(randomWaitTime);
  console.info(`[${randomId}] run${randomId} by ${user}  continue at : ${new Date()}`);

  //check for a lock
  if (idleCell.isBlank()) {
    idleCell.setValue(`run${randomId}`);
    console.info(`[${randomId}] ${randomId} script is idle : ${idleCell.getValue()} by ${user}`);
    return randomId;
  } else {
    console.warn(`[${randomId}] ${randomId} by ${user} detected running script : ${idleCell.getValue()}, aborted`);
    return null;
  }
}


function getEmails(dataSheet, playerCount) {
  return dataSheet.getRange(1, 1, playerCount).getValues().map(function (arr) {
    return arr[0]
  }).filter(function (str) {
    return !!str
  })
}
