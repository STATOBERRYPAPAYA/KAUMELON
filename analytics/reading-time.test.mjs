import test from 'node:test';
import assert from 'node:assert/strict';
import {formatReadingTime} from '../assets/reading-time.js';
test('reading durations switch from minutes to hours at 60 minutes',()=>{
 assert.equal(formatReadingTime(0),'0 min');
 assert.equal(formatReadingTime(90),'1.5 min');
 assert.equal(formatReadingTime(3594),'59.9 min');
 assert.equal(formatReadingTime(3600),'1 hr');
 assert.equal(formatReadingTime(5400),'1.5 hr');
 assert.equal(formatReadingTime(360000),'100 hr');
 assert.equal(formatReadingTime(30,{includeSeconds:true}),'30 sec');
 assert.equal(formatReadingTime(-10),'0 min');
});
