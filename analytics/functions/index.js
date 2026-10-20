const {onRequest}=require('firebase-functions/v2/https');
const {initializeApp}=require('firebase-admin/app');
const {getFirestore,Timestamp}=require('firebase-admin/firestore');
const {getAuth}=require('firebase-admin/auth');
const {createHandler}=require('./metrics');
initializeApp();
exports.melonMetrics=onRequest({region:'asia-south1',memory:'256MiB',cpu:'gcf_gen1',maxInstances:2,minInstances:0,timeoutSeconds:20,invoker:'public'},createHandler(getFirestore(),getAuth(),Timestamp));
