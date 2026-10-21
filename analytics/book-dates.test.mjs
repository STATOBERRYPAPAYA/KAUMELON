import test from 'node:test';
import assert from 'node:assert/strict';
import {badgeWindow,isNewBook} from '../assets/book-dates.js';
test('New badge expires at midnight IST one calendar month after publication',()=>{
 const end=Date.parse('2026-11-20T18:30:00Z');
 assert.equal(badgeWindow('2026-10-21').end,end);
 assert.equal(isNewBook('2026-10-21',end-1),true);
 assert.equal(isNewBook('2026-10-21',end),false);
 assert.equal(isNewBook('2026-10-21',Date.parse('2026-10-20T18:29:59Z')),false);
});
test('Month ends clamp to the last valid day and invalid dates stay hidden',()=>{
 assert.equal(badgeWindow('2027-01-31').end,Date.parse('2027-02-27T18:30:00Z'));
 assert.equal(badgeWindow('2028-01-31').end,Date.parse('2028-02-28T18:30:00Z'));
 assert.equal(isNewBook('2026-02-31'),false);
 assert.equal(isNewBook(''),false);
});
